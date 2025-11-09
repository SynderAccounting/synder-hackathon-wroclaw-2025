from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
from datetime import datetime

from app.schemas.connector import Connector, IngestionJob, TriggerIngestionRequest
from app.schemas.user import User
from app.api.auth import get_current_user
from app.models.mock_data import mock_db

router = APIRouter()


@router.get("", response_model=List[Connector])
async def get_connectors(current_user: User = Depends(get_current_user)):
    """Get all connectors"""
    return mock_db.connectors


@router.get("/{connector_id}", response_model=Connector)
async def get_connector(
    connector_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a single connector"""
    for connector in mock_db.connectors:
        if connector["id"] == connector_id:
            return connector
    raise HTTPException(status_code=404, detail="Connector not found")


@router.post("/trigger", response_model=IngestionJob)
async def trigger_ingestion(
    request: TriggerIngestionRequest,
    current_user: User = Depends(get_current_user),
):
    """Trigger an ingestion job"""
    # Find connector
    connector = None
    for c in mock_db.connectors:
        if c["id"] == request.connector_id:
            connector = c
            break

    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    # Create new ingestion job
    job = {
        "id": str(uuid.uuid4()),
        "connector_id": connector["id"],
        "connector_name": connector["name"],
        "status": "pending",
        "records_processed": 0,
        "records_failed": 0,
        "started_at": None,
        "completed_at": None,
        "error_message": None,
    }

    mock_db.ingestion_jobs.insert(0, job)  # Insert at beginning
    return job


@router.get("/jobs", response_model=List[IngestionJob])
async def get_ingestion_jobs(current_user: User = Depends(get_current_user)):
    """Get all ingestion jobs"""
    # Sort by most recent first
    sorted_jobs = sorted(
        mock_db.ingestion_jobs,
        key=lambda x: x.get("started_at") or datetime.utcnow(),
        reverse=True
    )
    return sorted_jobs[:20]  # Return last 20 jobs


@router.get("/jobs/{job_id}", response_model=IngestionJob)
async def get_ingestion_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a single ingestion job"""
    for job in mock_db.ingestion_jobs:
        if job["id"] == job_id:
            return job
    raise HTTPException(status_code=404, detail="Job not found")
