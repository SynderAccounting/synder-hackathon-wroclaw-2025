from __future__ import annotations

from unittest.mock import MagicMock

from app.ml.models import RecommendationPriority, StockMetrics
from app.ml.recommendation_engine import RecommendationEngine


def test_calculate_reorder_quantity():
    engine = RecommendationEngine(MagicMock())
    metrics = StockMetrics(
        sku="SKU-123",
        product_name="Test Product",
        current_stock=50,
        safety_stock=20,
        lead_time_days=7,
        avg_daily_sales_30d=8.0,
        avg_daily_sales_7d=9.0,
        velocity_trend=1.0,
        days_until_stockout=5.0,
        holding_cost_per_day=0.5,
    )
    qty = engine.calculate_reorder_quantity(metrics, avg_daily_sales=10.0)
    expected = int(max(10.0 * metrics.lead_time_days + metrics.safety_stock, 10.0 * 45) - metrics.current_stock)
    assert qty == expected
    assert qty >= 0


def test_priority_bucket_ordering():
    engine = RecommendationEngine(MagicMock())
    assert engine._priority_bucket(RecommendationPriority.CRITICAL) > engine._priority_bucket(RecommendationPriority.HIGH)
```}
