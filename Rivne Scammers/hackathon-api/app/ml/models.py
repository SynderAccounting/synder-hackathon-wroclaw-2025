"""Pydantic data structures used by the recommendation engine."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class RecommendationType(str, Enum):
    """Supported recommendation categories."""

    URGENT_RESTOCK = "urgent_restock"
    TRENDING = "trending"
    SLOW_MOVER = "slow_mover"
    SEASONAL = "seasonal"
    OPTIMIZATION = "optimization"
    NEW_PRODUCT_MONITOR = "new_product_monitor"


class RecommendationPriority(str, Enum):
    """Level of urgency the merchant should associate with the recommendation."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationStatus(str, Enum):
    """Tracks whether the merchant actioned a recommendation."""

    PENDING = "pending"
    ACTIONED = "actioned"
    DISMISSED = "dismissed"


class Recommendation(BaseModel):
    """Canonical structure returned to API consumers and persisted in the database."""

    id: Optional[int] = Field(default=None, description="Database identifier")
    type: RecommendationType
    sku: str
    product_name: str = Field(default="Unknown product")
    priority: RecommendationPriority
    message: str
    suggested_quantity: Optional[int] = Field(default=None, ge=0)
    current_stock: int = Field(default=0, ge=0)
    days_until_stockout: Optional[float] = Field(default=None, ge=0)
    growth_percentage: Optional[float] = Field(default=None)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reasoning: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: RecommendationStatus = RecommendationStatus.PENDING

    model_config = ConfigDict(from_attributes=True)

    @field_validator("message")
    @classmethod
    def _message_not_empty(cls, value: str) -> str:
        if not value.strip():  # pragma: no cover - double guard against empty strings
            raise ValueError("Recommendation message cannot be empty")
        return value


class StockMetrics(BaseModel):
    """Aggregate inventory KPIs required by the recommendation engine."""

    sku: str
    product_name: str
    current_stock: int
    safety_stock: int
    lead_time_days: int
    avg_daily_sales_30d: float
    avg_daily_sales_7d: float
    velocity_trend: float
    days_until_stockout: Optional[float]
    holding_cost_per_day: Optional[float]


class TrendSignal(BaseModel):
    """Signal surface for trending and slow mover detection."""

    sku: str
    product_name: str
    growth_rate: float = 0.0
    stability_index: float = 0.0
    is_trending: bool = False
    is_slow_mover: bool = False
    days_since_last_sale: Optional[int] = None
    inventory_value: Optional[float] = None


__all__ = [
    "Recommendation",
    "RecommendationPriority",
    "RecommendationStatus",
    "RecommendationType",
    "StockMetrics",
    "TrendSignal",
]
