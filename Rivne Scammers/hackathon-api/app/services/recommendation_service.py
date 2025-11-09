"""Service helpers around the recommendation engine."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterable, List

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.ml.models import Recommendation, RecommendationStatus
from app.ml.recommendation_engine import RecommendationEngine
from db.database import SessionLocal
from models.recommendation import RecommendationRecord

logger = logging.getLogger(__name__)


@contextmanager
def session_scope() -> Iterable[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - defensive rollback
        session.rollback()
        raise
    finally:
        session.close()


def run_recommendation_engine() -> int:
    """Run recommendation engine and return count of recommendations generated."""
    with session_scope() as session:
        recommendations = generate_and_persist_recommendations(session)
        count = len(recommendations)
        logger.info("Generated %s recommendations", count)
        return count


def generate_and_persist_recommendations(session: Session) -> List[Recommendation]:
    engine = RecommendationEngine(session)
    recommendations = engine.generate_recommendations()
    session.execute(delete(RecommendationRecord).where(RecommendationRecord.status == RecommendationStatus.PENDING))
    for rec in recommendations:
        session.add(
            RecommendationRecord(
                type=rec.type,
                sku=rec.sku,
                product_name=rec.product_name,
                priority=rec.priority,
                message=rec.message,
                suggested_quantity=rec.suggested_quantity,
                current_stock=rec.current_stock,
                days_until_stockout=rec.days_until_stockout,
                growth_percentage=rec.growth_percentage,
                confidence=rec.confidence,
                reasoning=rec.reasoning,
                status=rec.status,
            )
        )
    return recommendations
