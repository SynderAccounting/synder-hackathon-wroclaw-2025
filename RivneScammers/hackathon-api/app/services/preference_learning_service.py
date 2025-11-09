"""Service for learning from user preferences and dismissed recommendations."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Set

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from models.preference import RecommendationPreference
from models.recommendation import RecommendationRecord
from app.ml.models import RecommendationType

logger = logging.getLogger(__name__)


class PreferenceLearningService:
    """Learn from user feedback to improve future recommendations."""

    def __init__(self, db: Session):
        self.db = db
        self.default_cooldown_days = 30  # Don't suggest same thing for 30 days
        self.max_alternative_attempts = 3  # Try max 3 alternative approaches

    def record_dismissal(
        self,
        recommendation: RecommendationRecord,
        reason: Optional[str] = None
    ) -> None:
        """Record that a recommendation was dismissed."""
        # Check if we already have a preference record for this SKU + type combo
        stmt = select(RecommendationPreference).where(
            and_(
                RecommendationPreference.sku == recommendation.sku,
                RecommendationPreference.recommendation_type == recommendation.type.value
            )
        )
        preference = self.db.execute(stmt).scalar_one_or_none()

        if preference:
            # Update existing preference
            preference.dismissal_count += 1
            preference.last_dismissed_at = datetime.utcnow()
            preference.dismissed_reasoning = reason or recommendation.reasoning
            preference.dismissed_priority = recommendation.priority.value
            preference.dismissed_quantity = recommendation.suggested_quantity
            preference.updated_at = datetime.utcnow()

            # Increase cooldown based on dismissal count
            cooldown_days = min(self.default_cooldown_days * preference.dismissal_count, 180)
            preference.cooldown_until = datetime.utcnow() + timedelta(days=cooldown_days)

            logger.info(
                f"Updated preference for SKU {recommendation.sku} type {recommendation.type.value}: "
                f"{preference.dismissal_count} dismissals, cooldown until {preference.cooldown_until}"
            )
        else:
            # Create new preference record
            preference = RecommendationPreference(
                sku=recommendation.sku,
                product_name=recommendation.product_name,
                recommendation_type=recommendation.type.value,
                dismissal_count=1,
                last_dismissed_at=datetime.utcnow(),
                dismissed_priority=recommendation.priority.value,
                dismissed_quantity=recommendation.suggested_quantity,
                dismissed_reasoning=reason or recommendation.reasoning,
                cooldown_until=datetime.utcnow() + timedelta(days=self.default_cooldown_days),
                extra_metadata={
                    "initial_confidence": recommendation.confidence,
                    "initial_stock": recommendation.current_stock
                }
            )
            self.db.add(preference)
            logger.info(
                f"Created new preference for SKU {recommendation.sku} type {recommendation.type.value}"
            )

        # Update the recommendation record
        recommendation.dismissed_at = datetime.utcnow()
        recommendation.dismissed_reason = reason

        self.db.commit()

    def get_excluded_recommendations(self) -> Set[tuple[str, str]]:
        """Get set of (SKU, type) combinations that should be excluded from recommendations."""
        now = datetime.utcnow()

        # Get preferences that are still in cooldown period
        stmt = select(RecommendationPreference).where(
            RecommendationPreference.cooldown_until > now
        )
        preferences = self.db.execute(stmt).scalars().all()

        excluded = {(pref.sku, pref.recommendation_type) for pref in preferences}

        logger.info(f"Excluding {len(excluded)} SKU/type combinations from recommendations")
        return excluded

    def should_try_alternative(self, sku: str, recommendation_type: str) -> bool:
        """Check if we should try an alternative approach for this SKU."""
        stmt = select(RecommendationPreference).where(
            and_(
                RecommendationPreference.sku == sku,
                RecommendationPreference.recommendation_type == recommendation_type
            )
        )
        preference = self.db.execute(stmt).scalar_one_or_none()

        if not preference:
            return True  # No history, can suggest

        # Don't try if we've exceeded max attempts or still in cooldown
        if preference.alternative_attempts >= self.max_alternative_attempts:
            return False

        if preference.cooldown_until and preference.cooldown_until > datetime.utcnow():
            return False

        return True

    def record_alternative_attempt(self, sku: str, recommendation_type: str) -> None:
        """Record that we tried an alternative approach."""
        stmt = select(RecommendationPreference).where(
            and_(
                RecommendationPreference.sku == sku,
                RecommendationPreference.recommendation_type == recommendation_type
            )
        )
        preference = self.db.execute(stmt).scalar_one_or_none()

        if preference:
            preference.alternative_attempts += 1
            preference.updated_at = datetime.utcnow()
            self.db.commit()
            logger.info(
                f"Recorded alternative attempt {preference.alternative_attempts} for SKU {sku}"
            )

    def get_dismissal_stats(self) -> dict:
        """Get statistics about dismissed recommendations."""
        stmt = select(RecommendationPreference)
        preferences = self.db.execute(stmt).scalars().all()

        type_stats = {}
        for pref in preferences:
            if pref.recommendation_type not in type_stats:
                type_stats[pref.recommendation_type] = {
                    "total_dismissals": 0,
                    "unique_skus": 0,
                    "avg_dismissals_per_sku": 0.0
                }
            type_stats[pref.recommendation_type]["total_dismissals"] += pref.dismissal_count
            type_stats[pref.recommendation_type]["unique_skus"] += 1

        # Calculate averages
        for type_name, stats in type_stats.items():
            if stats["unique_skus"] > 0:
                stats["avg_dismissals_per_sku"] = stats["total_dismissals"] / stats["unique_skus"]

        return {
            "total_preferences": len(preferences),
            "by_type": type_stats,
            "total_dismissals": sum(p.dismissal_count for p in preferences)
        }

    def suggest_alternative_approach(
        self,
        sku: str,
        original_type: RecommendationType,
        product_name: str,
        current_stock: int
    ) -> Optional[dict]:
        """Suggest an alternative recommendation approach based on dismissal history."""
        stmt = select(RecommendationPreference).where(
            RecommendationPreference.sku == sku
        )
        preferences = self.db.execute(stmt).scalars().all()

        # Get all dismissed types for this SKU
        dismissed_types = {pref.recommendation_type for pref in preferences}

        # Define alternative strategies based on what was dismissed
        alternatives = {
            "urgent_restock": [
                {
                    "type": "slow_mover",
                    "message": f"Consider a promotion or bundle for {product_name} to move inventory",
                    "reasoning": "Alternative to restocking: focus on selling existing stock through promotions"
                },
                {
                    "type": "seasonal",
                    "message": f"Wait for seasonal demand increase for {product_name}",
                    "reasoning": "Alternative to restocking: time purchases based on seasonal patterns"
                }
            ],
            "slow_mover": [
                {
                    "type": "trending",
                    "message": f"Create a marketing campaign to boost {product_name} visibility",
                    "reasoning": "Alternative to discounting: increase demand through marketing"
                },
                {
                    "type": "urgent_restock",
                    "message": f"Reduce stock levels for {product_name} and focus on faster-moving items",
                    "reasoning": "Alternative to promoting: optimize inventory mix"
                }
            ],
            "trending": [
                {
                    "type": "urgent_restock",
                    "message": f"Monitor {product_name} closely for potential restock needs",
                    "reasoning": "Alternative to aggressive stocking: cautious inventory approach"
                },
                {
                    "type": "seasonal",
                    "message": f"Analyze if {product_name} trend is seasonal or permanent",
                    "reasoning": "Alternative to immediate action: wait and analyze trend"
                }
            ],
            "seasonal": [
                {
                    "type": "urgent_restock",
                    "message": f"Stock {product_name} based on recent sales velocity instead of seasonal patterns",
                    "reasoning": "Alternative to seasonal forecast: use recent data only"
                },
                {
                    "type": "trending",
                    "message": f"Check if {product_name} is trending beyond seasonal expectations",
                    "reasoning": "Alternative to seasonal approach: identify trend drivers"
                }
            ]
        }

        # Get alternatives for the original type
        possible_alternatives = alternatives.get(original_type.value, [])

        # Filter out alternatives that have also been dismissed
        valid_alternatives = [
            alt for alt in possible_alternatives
            if alt["type"] not in dismissed_types
        ]

        if valid_alternatives:
            # Return the first valid alternative
            alternative = valid_alternatives[0]
            logger.info(
                f"Suggesting alternative '{alternative['type']}' for SKU {sku} "
                f"instead of '{original_type.value}'"
            )
            return alternative

        return None


__all__ = ["PreferenceLearningService"]

