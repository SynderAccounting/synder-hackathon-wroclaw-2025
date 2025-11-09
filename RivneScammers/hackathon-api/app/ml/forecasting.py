"""Demand forecasting helpers leveraging classical time-series models."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sqlalchemy.orm import Session

from app.ml.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """Container returned by the forecaster."""

    sku: str
    horizon_days: int
    daily_demand: float
    series: pd.Series
    confidence_interval: tuple[float, float]


class DemandForecaster:
    """Wrapper around ARIMA to forecast per-SKU demand."""

    def __init__(self, db: Session, feature_engineer: FeatureEngineer):
        self.db = db
        self.feature_engineer = feature_engineer
        self.models: Dict[str, Any] = {}

    def train_model(self, sku: str, historical_sales: pd.Series) -> Optional[Any]:
        """Fit a simple ARIMA model, falling back gracefully when data is sparse."""
        if historical_sales.empty or len(historical_sales) < 14:
            return None
        try:
            model = ARIMA(historical_sales, order=(1, 1, 1), enforce_stationarity=False, enforce_invertibility=False)
            fitted = model.fit()
            self.models[sku] = fitted
            return fitted
        except Exception:  # pragma: no cover - statsmodels raises a variety of errors
            return None

    def predict_demand(self, sku: str, horizon_days: int = 30) -> ForecastResult:
        """Forecast average daily demand with multiple fallback methods."""
        series = self._load_series(sku)

        # Initialize variables
        mean_forecast: Optional[pd.Series] = None
        lower: Optional[pd.Series] = None
        upper: Optional[pd.Series] = None

        # Try ARIMA first
        model = self.models.get(sku) or self.train_model(sku, series)

        if model:
            try:
                forecast = model.get_forecast(steps=horizon_days)
                mean_forecast = forecast.predicted_mean
                lower, upper = forecast.conf_int(alpha=0.32).T  # ~68% interval
                logger.debug(f"ARIMA forecast successful for SKU {sku}")
            except Exception as e:
                logger.warning(f"ARIMA forecast failed for SKU {sku}: {e}, trying exponential smoothing")
                model = None

        # Fallback to exponential smoothing
        if not model and len(series) >= 7:
            try:
                exp_model = ExponentialSmoothing(
                    series,
                    trend='add' if len(series) >= 14 else None,
                    seasonal=None,
                    initialization_method="estimated"
                ).fit()
                mean_forecast = exp_model.forecast(steps=horizon_days)
                # Estimate confidence interval
                std = series.std()
                lower = mean_forecast - 1.0 * std
                upper = mean_forecast + 1.0 * std
                logger.debug(f"Exponential smoothing successful for SKU {sku}")
            except Exception as e:
                logger.warning(f"Exponential smoothing failed for SKU {sku}: {e}, using simple average")

        # Final fallback to simple average
        if mean_forecast is None or lower is None or upper is None:
            avg = series.mean() if not series.empty else 0.0
            mean_forecast = pd.Series([avg] * horizon_days)
            lower = mean_forecast * 0.7
            upper = mean_forecast * 1.3
            logger.debug(f"Using simple average forecast for SKU {sku}")

        daily_demand = float(np.clip(mean_forecast.mean(), a_min=0.0, a_max=None))
        interval = (max(0.0, float(lower.min())), float(upper.max()))
        return ForecastResult(
            sku=sku,
            horizon_days=horizon_days,
            daily_demand=daily_demand,
            series=series,
            confidence_interval=interval
        )

    def detect_seasonality(self, sku: str) -> Optional[Dict[str, float]]:
        """Rudimentary seasonal signal detection using year-over-year comparisons."""
        series = self._load_series(sku, days=365)
        if series.empty or len(series) < 60:
            return None
        monthly = series.resample("M").sum()
        if monthly.empty:
            return None
        rolling = monthly.rolling(window=3, min_periods=1).mean()
        current_month = monthly.index[-1].month
        seasonal_mean = rolling.groupby(rolling.index.month).mean()
        baseline = monthly.mean()
        lift = float((seasonal_mean.get(current_month, baseline) / baseline) - 1.0) if baseline else 0.0
        confidence = min(1.0, max(0.1, len(monthly) / 24))
        return {
            "seasonal_lift": lift,
            "confidence": confidence,
            "reference_month": current_month,
        }

    def _load_series(self, sku: str, days: int = 180) -> pd.Series:
        series = self.feature_engineer._load_sales_history(sku, days)  # noqa: SLF001 - intentional reuse of helper
        if series.empty:
            return series
        series = series.asfreq("D", fill_value=0.0)
        return series
