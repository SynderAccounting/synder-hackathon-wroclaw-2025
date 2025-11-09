"""Scheduled background jobs for the recommendation engine."""
from __future__ import annotations

import logging
from typing import Iterable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.ml.feature_engineering import FeatureEngineer
from app.ml.forecasting import DemandForecaster
from app.ml.models import Recommendation, RecommendationPriority
from app.services.recommendation_service import generate_and_persist_recommendations, session_scope

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("cron", hour=2)
async def daily_recommendation_analysis() -> None:
    with session_scope() as session:
        recommendations = generate_and_persist_recommendations(session)
        critical = [rec for rec in recommendations if rec.priority == RecommendationPriority.CRITICAL]
    if critical:
        await send_alert_email(critical)


@scheduler.scheduled_job("cron", day_of_week="sun", hour=3)
async def retrain_models() -> None:
    with session_scope() as session:
        feature_engineer = FeatureEngineer(session)
        forecaster = DemandForecaster(session, feature_engineer)
        for sku in feature_engineer.iter_active_skus():
            series = feature_engineer._load_sales_history(sku, days=365)  # noqa: SLF001 - trusted internal call
            forecaster.train_model(sku, series)
    logger.info("Demand models retrained")


async def send_alert_email(recommendations: Iterable[Recommendation]) -> None:
    # Placeholder for integration with notification/email service
    for rec in recommendations:
        logger.warning("CRITICAL recommendation for %s: %s", rec.sku, rec.message)


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
