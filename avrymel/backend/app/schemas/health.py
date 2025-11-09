from pydantic import BaseModel
from typing import Optional


class ComponentHealth(BaseModel):
    status: str  # up, down, degraded
    latency_ms: Optional[int] = None
    details: Optional[str] = None


class HealthStatus(BaseModel):
    status: str  # healthy, degraded, unhealthy
    api: ComponentHealth
    database: ComponentHealth
    workers: ComponentHealth
    timestamp: str
