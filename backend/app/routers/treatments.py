"""Treatment endpoints for treatment sessions."""
from fastapi import APIRouter
from typing import List, Optional
from app.core.dependencies import CurrentUserId, Database
from app.models.schemas import (
    TreatmentSessionCreate,
    TreatmentSessionResponse,
    TreatmentSessionUpdate,
)
from app.services.treatment_service import TreatmentService


router = APIRouter()


@router.post("/sessions", response_model=dict)
async def create_treatment_session(
    session_data: TreatmentSessionCreate,
    user_id: CurrentUserId,
    db: Database
):
    """Create a new treatment session."""
    service = TreatmentService(db)
    result = await service.create_session(user_id, session_data)
    return result


@router.get("/sessions", response_model=List[dict])
async def get_user_sessions(
    user_id: CurrentUserId,
    db: Database,
    treatment_type: Optional[str] = None,
    limit: int = 50
):
    """Get all sessions for the current user."""
    service = TreatmentService(db)
    results = await service.get_user_sessions(
        user_id,
        treatment_type=treatment_type,
        limit=limit
    )
    return results


@router.get("/sessions/{session_id}", response_model=dict)
async def get_session(
    session_id: str,
    user_id: CurrentUserId,
    db: Database
):
    """Get a specific session."""
    service = TreatmentService(db)
    return await service.get_session(session_id, user_id)


@router.patch("/sessions/{session_id}", response_model=dict)
async def update_session(
    session_id: str,
    update_data: TreatmentSessionUpdate,
    user_id: CurrentUserId,
    db: Database
):
    """Update a treatment session."""
    service = TreatmentService(db)
    result = await service.complete_session(
        session_id,
        user_id,
        data=update_data.data
    )
    return result
