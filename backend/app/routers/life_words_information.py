"""Life Words Information Practice endpoints."""
from typing import Dict, Any
from fastapi import APIRouter
from app.core.dependencies import CurrentUserId, Database
from app.models.life_words_information import (
    InformationStatusResponse,
    LifeWordsInformationSessionCreate,
    LifeWordsInformationResponseCreate,
)
from app.services.life_words_information_service import LifeWordsInformationService

router = APIRouter()


@router.get("/information-status")
async def get_information_status(
    user_id: CurrentUserId, db: Database
) -> InformationStatusResponse:
    """Check if user has enough profile data for information practice."""
    service = LifeWordsInformationService(db)
    status = await service.get_information_status(user_id)
    return InformationStatusResponse(**status)


@router.post("/information-sessions")
async def create_information_session(
    session_data: LifeWordsInformationSessionCreate,
    user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Create a new information practice session with 5 random items."""
    service = LifeWordsInformationService(db)
    return await service.create_session(user_id)


@router.get("/information-sessions/{session_id}")
async def get_information_session(
    session_id: str, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Get information session with responses."""
    service = LifeWordsInformationService(db)
    return await service.get_session(session_id, user_id)


@router.post("/information-sessions/{session_id}/responses")
async def save_information_response(
    session_id: str, response_data: LifeWordsInformationResponseCreate,
    user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Save a response to an information item."""
    service = LifeWordsInformationService(db)
    return await service.save_response(session_id, user_id, response_data)


@router.put("/information-sessions/{session_id}/complete")
async def complete_information_session(
    session_id: str, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Complete an information session and calculate statistics."""
    service = LifeWordsInformationService(db)
    return await service.complete_session(session_id, user_id)
