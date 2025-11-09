from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class Connector(BaseModel):
    id: str
    name: str
    platform: str
    description: str
    status: str  # active, inactive, error
    last_sync: Optional[datetime] = None
    config: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class IngestionJob(BaseModel):
    id: str
    connector_id: str
    connector_name: str
    status: str  # pending, running, completed, failed
    records_processed: int
    records_failed: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class TriggerIngestionRequest(BaseModel):
    connector_id: str
    date_from: Optional[str] = None
    date_to: Optional[str] = None
