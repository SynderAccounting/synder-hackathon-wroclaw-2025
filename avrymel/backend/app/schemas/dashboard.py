from pydantic import BaseModel
from typing import List


class TrendData(BaseModel):
    date: str
    value: float


class PlatformStats(BaseModel):
    platform: str
    count: int
    revenue: float


class DashboardMetrics(BaseModel):
    total_transactions: int
    total_revenue: float
    active_connectors: int
    pending_jobs: int
    transactions_today: int
    revenue_today: float
    transactions_trend: List[TrendData]
    revenue_trend: List[TrendData]
    platform_distribution: List[PlatformStats]
