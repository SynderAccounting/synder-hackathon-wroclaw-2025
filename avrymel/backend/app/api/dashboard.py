from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.schemas.dashboard import DashboardMetrics, TrendData, PlatformStats
from app.schemas.user import User
from app.api.auth import get_current_user
from app.chat.database import get_db

router = APIRouter()


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard metrics from the merchant's database"""

    # Set merchant context (hardcoded to merchant 1 for now)
    merchant_id = 1
    await db.execute(text("SELECT set_current_merchant(:merchant_id)"), {"merchant_id": merchant_id})

    # Total transactions (orders)
    result = await db.execute(text("SELECT COUNT(*) FROM orders"))
    total_transactions = result.scalar() or 0

    # Total revenue
    result = await db.execute(text("SELECT COALESCE(SUM(final_price), 0) FROM orders"))
    total_revenue = float(result.scalar() or 0)

    # Today's metrics
    today = datetime.utcnow().date()
    result = await db.execute(
        text("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = :today"),
        {"today": today}
    )
    transactions_today = result.scalar() or 0

    result = await db.execute(
        text("SELECT COALESCE(SUM(final_price), 0) FROM orders WHERE DATE(created_at) = :today"),
        {"today": today}
    )
    revenue_today = float(result.scalar() or 0)

    # Active connectors (mock for now)
    active_connectors = 3  # Amazon, Etsy, Shopify

    # Pending jobs (mock for now)
    pending_jobs = 0

    # Transaction trend (last 30 days)
    transactions_trend = []
    revenue_trend = []

    for i in range(30, -1, -1):
        date = today - timedelta(days=i)

        # Count transactions for this day
        result = await db.execute(
            text("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = :date"),
            {"date": date}
        )
        count = result.scalar() or 0

        # Sum revenue for this day
        result = await db.execute(
            text("SELECT COALESCE(SUM(final_price), 0) FROM orders WHERE DATE(created_at) = :date"),
            {"date": date}
        )
        revenue = float(result.scalar() or 0)

        transactions_trend.append(TrendData(
            date=date.isoformat(),
            value=float(count)
        ))

        revenue_trend.append(TrendData(
            date=date.isoformat(),
            value=revenue
        ))

    # Platform distribution (service = Amazon, Etsy, Shopify)
    result = await db.execute(
        text("""
            SELECT
                service as platform,
                COUNT(*) as count,
                COALESCE(SUM(final_price), 0) as revenue
            FROM orders
            GROUP BY service
        """)
    )

    platform_distribution = [
        PlatformStats(
            platform=row[0],
            count=row[1],
            revenue=float(row[2])
        )
        for row in result.fetchall()
    ]

    return DashboardMetrics(
        total_transactions=total_transactions,
        total_revenue=total_revenue,
        active_connectors=active_connectors,
        pending_jobs=pending_jobs,
        transactions_today=transactions_today,
        revenue_today=revenue_today,
        transactions_trend=transactions_trend,
        revenue_trend=revenue_trend,
        platform_distribution=platform_distribution,
    )
