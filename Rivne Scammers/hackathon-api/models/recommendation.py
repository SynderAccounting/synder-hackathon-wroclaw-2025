"""Recommendation persistence model."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base
from app.ml.models import Recommendation, RecommendationPriority, RecommendationStatus, RecommendationType


class RecommendationRecord(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[RecommendationType] = mapped_column(
        Enum(RecommendationType, name="recommendation_type", native_enum=False)
    )
    sku: Mapped[str] = mapped_column(String, index=True)
    product_name: Mapped[str] = mapped_column(String)
    priority: Mapped[RecommendationPriority] = mapped_column(
        Enum(RecommendationPriority, name="recommendation_priority", native_enum=False)
    )
    message: Mapped[str] = mapped_column(String)
    suggested_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_stock: Mapped[int] = mapped_column(Integer, default=0)
    days_until_stockout: Mapped[float | None] = mapped_column(Float, nullable=True)
    growth_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    reasoning: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(RecommendationStatus, name="recommendation_status", native_enum=False),
        default=RecommendationStatus.PENDING,
    )
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    dismissed_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_domain(self) -> Recommendation:
        return Recommendation(
            id=self.id,
            type=self.type,
            sku=self.sku,
            product_name=self.product_name,
            priority=self.priority,
            message=self.message,
            suggested_quantity=self.suggested_quantity,
            current_stock=self.current_stock,
            days_until_stockout=self.days_until_stockout,
            growth_percentage=self.growth_percentage,
            confidence=self.confidence,
            reasoning=self.reasoning,
            created_at=self.created_at,
            status=self.status,
        )


__all__ = ["RecommendationRecord"]
