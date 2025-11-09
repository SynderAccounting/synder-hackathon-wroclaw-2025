"""User preference learning model for ML recommendations."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class RecommendationPreference(Base):
    """Track user preferences and dismissed recommendation patterns."""

    __tablename__ = "recommendation_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String, index=True)
    product_name: Mapped[str] = mapped_column(String)

    # Pattern tracking
    recommendation_type: Mapped[str] = mapped_column(String, index=True)
    dismissal_count: Mapped[int] = mapped_column(Integer, default=1)
    last_dismissed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Context when dismissed
    dismissed_priority: Mapped[str | None] = mapped_column(String, nullable=True)
    dismissed_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dismissed_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Alternative suggestions that were tried
    alternative_attempts: Mapped[int] = mapped_column(Integer, default=0)

    # Extra metadata for learning (renamed from metadata to avoid SQLAlchemy conflict)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Cooldown period (days before suggesting again)
    cooldown_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


__all__ = ["RecommendationPreference"]

