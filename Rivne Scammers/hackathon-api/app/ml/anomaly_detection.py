"""Trend and anomaly detection for product performance."""
from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.feature_engineering import FeatureEngineer
from app.ml.models import TrendSignal
from models.catalog import Product


class TrendDetector:
    """Detects statistically relevant growth or decline signals."""

    def __init__(self, db: Session, feature_engineer: FeatureEngineer, contamination: float = 0.1):
        self.db = db
        self.feature_engineer = feature_engineer
        self.model = IsolationForest(contamination=contamination, random_state=42)

    def detect_trending_products(self) -> List[TrendSignal]:
        dataset = self._build_dataset()
        if dataset.empty:
            return []
        # Lowered threshold from 0.5 to 0.2 (20% growth) to detect more trending products
        growth_mask = dataset["growth_rate"] > 0.2
        trending = dataset[growth_mask]
        if len(trending) >= 5:
            scores = self._score_dataset(trending)
            trending = trending.assign(isolation_score=scores)
            trending = trending[trending["isolation_score"] < 0]
        signals = [self.feature_engineer.build_trend_signal(row.sku) for row in trending.itertuples()]
        return [signal for signal in signals if signal and signal.is_trending]

    def detect_slow_movers(self) -> List[TrendSignal]:
        dataset = self._build_dataset()
        if dataset.empty:
            return []
        # Relaxed criteria: lowered sales threshold from 0.5 to 1.0 and stock from 100 to 50
        slow_mask = (dataset["avg_daily_sales_30d"] < 1.0) & (dataset["current_stock"] >= 50)
        slow = dataset[slow_mask]
        signals = [self.feature_engineer.build_trend_signal(row.sku) for row in slow.itertuples()]
        return [signal for signal in signals if signal and signal.is_slow_mover]

    def calculate_growth_rate(self, sku: str) -> float:
        dataset = self._build_dataset()
        record = dataset.loc[dataset["sku"] == sku]
        if record.empty:
            return 0.0
        return float(record.iloc[0]["growth_rate"])

    def _score_dataset(self, frame: pd.DataFrame) -> np.ndarray:
        feature_cols = ["growth_rate", "avg_daily_sales_7d", "avg_daily_sales_30d", "current_stock"]
        features = frame[feature_cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
        if len(features) < 5:
            return np.zeros(len(features))
        return self.model.fit_predict(features.values)

    def _build_dataset(self) -> pd.DataFrame:
        stmt = select(Product.sku, Product.title, Product.current_stock)
        rows = self.db.execute(stmt).all()
        if not rows:
            return pd.DataFrame(columns=["sku", "product_name", "current_stock", "avg_daily_sales_7d", "avg_daily_sales_30d", "growth_rate"])

        records = []
        for row in rows:
            velocity = self.feature_engineer.calculate_sales_velocity(row.sku)
            records.append(
                {
                    "sku": row.sku,
                    "product_name": row.title or row.sku,
                    "current_stock": row.current_stock or 0,
                    "avg_daily_sales_7d": velocity["avg_daily_sales_7d"],
                    "avg_daily_sales_30d": velocity["avg_daily_sales_30d"],
                    "growth_rate": (velocity["avg_daily_sales_7d"] / max(velocity["avg_daily_sales_30d"], 1e-3)) - 1.0,
                }
            )
        return pd.DataFrame.from_records(records)
