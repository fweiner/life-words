"""Results and progress tracking endpoints."""
from fastapi import APIRouter
from typing import List, Optional
from app.core.dependencies import CurrentUserId, Database
from app.services.treatment_service import TreatmentService


router = APIRouter()


@router.get("/my-results", response_model=List[dict])
async def get_my_results(
    user_id: CurrentUserId,
    db: Database,
    limit: int = 50
):
    """Get all results for the current user."""
    service = TreatmentService(db)
    results = await service.get_user_results(user_id, limit=limit)
    return results


@router.get("/my-progress", response_model=List[dict])
async def get_my_progress(
    user_id: CurrentUserId,
    db: Database,
    treatment_type: Optional[str] = None
):
    """Get progress for the current user."""
    service = TreatmentService(db)
    results = await service.get_user_progress(
        user_id,
        treatment_type=treatment_type
    )
    return results
