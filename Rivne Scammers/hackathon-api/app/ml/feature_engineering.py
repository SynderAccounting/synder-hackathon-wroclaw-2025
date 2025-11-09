"""Feature engineering helpers for the recommendation engine."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, Iterable, Optional

import numpy as np
import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ml.models import StockMetrics, TrendSignal
from models.catalog import InventorySnapshot, Order, OrderItem, Product


class FeatureEngineer:
    """Transforms raw order and inventory data into analytical features."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def calculate_sales_velocity(self, sku: str, days: int = 30) -> Dict[str, float]:
        """Return rolling sales metrics for the requested SKU."""
        history = self._load_sales_history(sku=sku, days=days)
        if history.empty:
            return {
                "avg_daily_sales_7d": 0.0,
                "avg_daily_sales_30d": 0.0,
                "std_dev": 0.0,
                "trend_direction": 0.0,
                "coefficient_of_variation": 0.0,
            }

        # Reindex to fill missing days with 0 sales so rolling windows are robust.
        idx = pd.date_range(history.index.min(), history.index.max(), freq="D")
        history = history.reindex(idx, fill_value=0.0)

        avg_7 = history.tail(7).mean()
        avg_30 = history.tail(min(30, len(history))).mean()
        std_dev = history.tail(min(30, len(history))).std(ddof=0) or 0.0
        trend = float(avg_7 - avg_30)
        coeff_var = float(std_dev / avg_30) if avg_30 else 0.0

        return {
            "avg_daily_sales_7d": float(avg_7),
            "avg_daily_sales_30d": float(avg_30),
            "std_dev": float(std_dev),
            "trend_direction": float(np.sign(trend)),
            "coefficient_of_variation": coeff_var,
        }

    def calculate_stock_metrics(self, sku: str) -> Optional[StockMetrics]:
        """Combine sales velocity with inventory levels for a SKU."""
        product = self.db.execute(
            select(Product).where(Product.sku == sku)
        ).scalar_one_or_none()
        if not product:
            return None

        latest_snapshot = self._latest_inventory_snapshot(sku)
        current_stock_value = latest_snapshot.available_quantity if latest_snapshot else product.current_stock
        current_stock = int(current_stock_value or 0)

        sales_metrics = self.calculate_sales_velocity(sku)
        days_until_stockout = None
        if sales_metrics["avg_daily_sales_30d"]:
            days_until_stockout = current_stock / max(sales_metrics["avg_daily_sales_30d"], 1e-3)

        holding_cost_per_day = None
        if product.holding_cost:
            holding_cost_per_day = float(product.holding_cost) * current_stock

        return StockMetrics(
            sku=sku,
            product_name=product.title or product.sku,
            current_stock=current_stock,
            safety_stock=product.safety_stock or 0,
            lead_time_days=product.lead_time_days or 14,
            avg_daily_sales_30d=sales_metrics["avg_daily_sales_30d"],
            avg_daily_sales_7d=sales_metrics["avg_daily_sales_7d"],
            velocity_trend=sales_metrics["trend_direction"],
            days_until_stockout=days_until_stockout,
            holding_cost_per_day=holding_cost_per_day,
        )

    def extract_temporal_features(self, when: datetime | date) -> Dict[str, int]:
        """Return calendar based features used by forecasting models."""
        if isinstance(when, datetime):
            when = when.date()
        week_of_month = (when.day - 1) // 7 + 1
        return {
            "day_of_week": when.weekday(),
            "is_weekend": int(when.weekday() >= 5),
            "week_of_month": week_of_month,
            "month": when.month,
            "quarter": (when.month - 1) // 3 + 1,
        }

    def build_feature_vector(self, sku: str) -> Optional[Dict[str, float]]:
        """Roll up all relevant features into a flat dictionary."""
        stock_metrics = self.calculate_stock_metrics(sku)
        if not stock_metrics:
            return None

        vector: Dict[str, float] = stock_metrics.dict()
        vector.update(
            {
                "stock_to_sales_ratio": self._safe_divide(stock_metrics.current_stock, stock_metrics.avg_daily_sales_30d),
                "safety_stock_coverage": self._safe_divide(
                    stock_metrics.current_stock, max(stock_metrics.safety_stock, 1)
                ),
                "velocity_trend": stock_metrics.velocity_trend,
            }
        )
        return vector

    def build_trend_signal(self, sku: str) -> Optional[TrendSignal]:
        """Return pre-computed signals used by anomaly detection."""
        metrics = self.calculate_stock_metrics(sku)
        if not metrics:
            return None
        seven = metrics.avg_daily_sales_7d
        thirty = metrics.avg_daily_sales_30d or 1e-3
        growth_rate = (seven / thirty) - 1.0

        last_sale = self._days_since_last_sale(sku)
        inventory_value = None
        if metrics.holding_cost_per_day:
            inventory_value = metrics.holding_cost_per_day * metrics.current_stock

        return TrendSignal(
            sku=sku,
            product_name=metrics.product_name,
            growth_rate=float(growth_rate),
            stability_index=1.0 - min(abs(metrics.velocity_trend), 1.0),
            is_trending=seven > 0 and growth_rate >= 0.2,  # Lowered from 0.5 to 0.2
            is_slow_mover=(thirty < 1.0 and metrics.current_stock >= 50) or (last_sale is not None and last_sale >= 30),  # Relaxed criteria
            days_since_last_sale=last_sale,
            inventory_value=inventory_value,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_sales_history(self, sku: str, days: int) -> pd.Series:
        cutoff = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(
                func.date(Order.created_at).label("doc_date"),
                func.sum(OrderItem.quantity).label("units"),
            )
            .select_from(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .where(OrderItem.sku == sku, Order.created_at >= cutoff)
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
        )
        rows = self.db.execute(stmt).all()
        if not rows:
            return pd.Series(dtype=float)
        data = {pd.to_datetime(row.doc_date): float(row.units) for row in rows}
        series = pd.Series(data).sort_index()
        return series

    def _latest_inventory_snapshot(self, sku: str) -> Optional[InventorySnapshot]:
        stmt = (
            select(InventorySnapshot)
            .where(InventorySnapshot.sku == sku)
            .order_by(InventorySnapshot.snapshot_date.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def _days_since_last_sale(self, sku: str) -> Optional[int]:
        stmt = (
            select(func.max(Order.created_at))
            .select_from(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .where(OrderItem.sku == sku)
        )
        last_sale: Optional[datetime] = self.db.execute(stmt).scalar_one_or_none()
        if not last_sale:
            return None
        return (datetime.utcnow() - last_sale).days

    @staticmethod
    def _safe_divide(num: float, denom: float) -> float:
        if denom:
            return float(num / denom)
        return float("inf") if num else 0.0

    def iter_active_skus(self) -> Iterable[str]:
        """Utility that yields SKUs that currently have inventory."""
        stmt = select(Product.sku).where(Product.current_stock > 0)
        return (row.sku for row in self.db.execute(stmt))
