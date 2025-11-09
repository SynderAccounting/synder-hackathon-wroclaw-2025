"""REST endpoints exposing the recommendation engine."""
from __future__ import annotations

import time
from typing import Any, Dict, Generator, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.models import Recommendation, RecommendationPriority, RecommendationStatus, RecommendationType
from app.services.recommendation_service import run_recommendation_engine
from db.database import SessionLocal
from models.recommendation import RecommendationRecord

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])

# Global status tracking for recommendation generation
generation_status: Dict[str, Any] = {
    "is_running": False,
    "last_run": None,
    "last_run_duration": None,
    "last_run_count": 0,
    "error": None
}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:  # pragma: no cover - defensive cleanup
        db.close()


class RecommendationAction(BaseModel):
    action: RecommendationStatus
    quantity_ordered: Optional[int] = None
    supplier: Optional[str] = None
    expected_delivery: Optional[str] = None
    notes: Optional[str] = None


class GenerationStatusResponse(BaseModel):
    is_running: bool
    last_run: Optional[float] = None
    last_run_duration: Optional[float] = None
    last_run_count: int = 0
    error: Optional[str] = None


class GenerateResponse(BaseModel):
    message: str
    status: str


@router.get("/", response_model=List[Recommendation])
async def get_recommendations(
    type: Optional[RecommendationType] = Query(default=None),
    priority: Optional[RecommendationPriority] = Query(default=None),
    status: RecommendationStatus = Query(default=RecommendationStatus.PENDING, alias="status"),
    db: Session = Depends(get_db),
) -> List[Recommendation]:
    stmt = select(RecommendationRecord).where(RecommendationRecord.status == status)
    if type:
        stmt = stmt.where(RecommendationRecord.type == type)
    if priority:
        stmt = stmt.where(RecommendationRecord.priority == priority)
    stmt = stmt.order_by(RecommendationRecord.priority.desc(), RecommendationRecord.confidence.desc())

    results = db.execute(stmt).scalars().all()
    return [record.to_domain() for record in results]


@router.get("/status", response_model=GenerationStatusResponse)
async def get_generation_status() -> Dict[str, Any]:
    """Get the current status of recommendation generation."""
    return generation_status


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED, response_model=GenerateResponse)
async def generate_recommendations_now(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Trigger recommendation generation in the background."""
    if generation_status["is_running"]:
        return {
            "message": "Recommendation generation is already in progress",
            "status": "running"
        }

    async def run_with_tracking():
        generation_status["is_running"] = True
        generation_status["error"] = None
        start_time = time.time()

        try:
            count = run_recommendation_engine()
            duration = time.time() - start_time
            generation_status["last_run"] = time.time()
            generation_status["last_run_duration"] = duration
            generation_status["last_run_count"] = count
        except Exception as e:
            generation_status["error"] = str(e)
        finally:
            generation_status["is_running"] = False

    background_tasks.add_task(run_with_tracking)
    return {
        "message": "Recommendation analysis started",
        "status": "started"
    }


@router.post("/{recommendation_id}/action")
async def action_recommendation(
    recommendation_id: int,
    payload: RecommendationAction,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Take action on a recommendation (accept or dismiss)."""
    from app.services.preference_learning_service import PreferenceLearningService

    record = db.get(RecommendationRecord, recommendation_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    # Update status
    record.status = payload.action

    # If dismissed, record in preference learning
    if payload.action == RecommendationStatus.DISMISSED:
        preference_service = PreferenceLearningService(db)
        preference_service.record_dismissal(record, reason=payload.notes)

    # Add metadata to reasoning
    if payload.quantity_ordered is not None:
        record.reasoning += f"\nQuantity ordered: {payload.quantity_ordered}"
    if payload.supplier:
        record.reasoning += f"\nSupplier: {payload.supplier}"
    if payload.expected_delivery:
        record.reasoning += f"\nExpected delivery: {payload.expected_delivery}"
    if payload.notes:
        record.reasoning += f"\nNotes: {payload.notes}"

    db.add(record)
    db.commit()

    action_msg = "dismissed and learned from" if payload.action == RecommendationStatus.DISMISSED else "updated"
    return {"message": f"Recommendation {action_msg} successfully"}


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
) -> None:
    record = db.get(RecommendationRecord, recommendation_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    db.delete(record)
    db.commit()


@router.get("/preferences/stats")
async def get_preference_stats(db: Session = Depends(get_db)) -> dict:
    """Get statistics about user preferences and dismissed recommendations."""
    from app.services.preference_learning_service import PreferenceLearningService

    preference_service = PreferenceLearningService(db)
    stats = preference_service.get_dismissal_stats()

    return {
        "stats": stats,
        "message": "AI learns from your dismissed recommendations to provide better suggestions"
    }

