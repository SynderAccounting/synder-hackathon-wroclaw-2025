from fastapi import APIRouter
from datetime import datetime
import random

from app.schemas.health import HealthStatus, ComponentHealth

router = APIRouter()


@router.get("", response_model=HealthStatus)
async def get_health():
    """Get system health status"""
    # Mock health check - in production, these would be real checks
    api_health = ComponentHealth(
        status="up",
        latency_ms=random.randint(10, 50),
        details="API server is running normally"
    )

    database_health = ComponentHealth(
        status="up",
        latency_ms=random.randint(5, 30),
        details="Database connection established"
    )

    workers_health = ComponentHealth(
        status="up",
        latency_ms=random.randint(20, 100),
        details="All workers are processing jobs"
    )

    # Determine overall status
    component_statuses = [api_health.status, database_health.status, workers_health.status]

    if all(s == "up" for s in component_statuses):
        overall_status = "healthy"
    elif any(s == "down" for s in component_statuses):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return HealthStatus(
        status=overall_status,
        api=api_health,
        database=database_health,
        workers=workers_health,
        timestamp=datetime.utcnow().isoformat(),
    )
