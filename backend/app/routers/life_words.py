"""Find My Life Words treatment endpoints."""
from typing import List, Dict, Any
from fastapi import APIRouter
from app.core.dependencies import CurrentUserId, Database
from app.models.life_words import (
    PersonalContactCreate,
    PersonalContactUpdate,
    PersonalContactResponse,
    QuickAddContactCreate,
    LifeWordsStatusResponse,
    LifeWordsSessionCreate,
    LifeWordsResponseCreate,
)
from app.services.life_words_service import LifeWordsService

router = APIRouter()


# ============== Status ==============

@router.get("/status")
async def get_life_words_status(
    user_id: CurrentUserId, db: Database
) -> LifeWordsStatusResponse:
    """Get user's life words setup status."""
    service = LifeWordsService(db)
    status = await service.get_status(user_id)
    return LifeWordsStatusResponse(**status)


# ============== Personal Contacts ==============

@router.post("/contacts")
async def create_personal_contact(
    contact_data: PersonalContactCreate, user_id: CurrentUserId, db: Database
) -> PersonalContactResponse:
    """Create a new personal contact."""
    service = LifeWordsService(db)
    contact = await service.create_contact(user_id, contact_data)
    return PersonalContactResponse(**contact)


@router.post("/contacts/quick-add")
async def quick_add_contact(
    data: QuickAddContactCreate, user_id: CurrentUserId, db: Database
) -> PersonalContactResponse:
    """Quick add a contact with just a photo - creates an incomplete draft entry."""
    service = LifeWordsService(db)
    contact = await service.quick_add_contact(user_id, data)
    return PersonalContactResponse(**contact)


@router.get("/contacts")
async def list_personal_contacts(
    user_id: CurrentUserId, db: Database, include_inactive: bool = False
) -> List[PersonalContactResponse]:
    """List user's personal contacts."""
    service = LifeWordsService(db)
    contacts = await service.list_contacts(user_id, include_inactive)
    return [PersonalContactResponse(**c) for c in contacts]


@router.get("/contacts/{contact_id}")
async def get_personal_contact(
    contact_id: str, user_id: CurrentUserId, db: Database
) -> PersonalContactResponse:
    """Get a specific personal contact."""
    service = LifeWordsService(db)
    contact = await service.get_contact(contact_id, user_id)
    return PersonalContactResponse(**contact)


@router.put("/contacts/{contact_id}")
async def update_personal_contact(
    contact_id: str, contact_data: PersonalContactUpdate,
    user_id: CurrentUserId, db: Database
) -> PersonalContactResponse:
    """Update a personal contact."""
    service = LifeWordsService(db)
    updated = await service.update_contact(contact_id, user_id, contact_data)
    return PersonalContactResponse(**updated)


@router.delete("/contacts/{contact_id}")
async def delete_personal_contact(
    contact_id: str, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Soft delete a personal contact (set is_active=false)."""
    service = LifeWordsService(db)
    return await service.delete_contact(contact_id, user_id)


# ============== Sessions ==============

@router.post("/sessions")
async def create_life_words_session(
    session_data: LifeWordsSessionCreate, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Create a new life words session including contacts and items."""
    service = LifeWordsService(db)
    return await service.create_session(user_id, session_data)


@router.get("/sessions/{session_id}")
async def get_life_words_session(
    session_id: str, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Get session details with contacts, items, and responses."""
    service = LifeWordsService(db)
    return await service.get_session(session_id, user_id)


@router.post("/sessions/{session_id}/responses")
async def save_life_words_response(
    session_id: str, response_data: LifeWordsResponseCreate,
    user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Save a response for a contact."""
    service = LifeWordsService(db)
    return await service.save_response(session_id, user_id, response_data)


@router.get("/progress")
async def get_life_words_progress(
    user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Get user's life words progress statistics."""
    service = LifeWordsService(db)
    return await service.get_progress(user_id)


@router.put("/sessions/{session_id}/complete")
async def complete_life_words_session(
    session_id: str, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Mark session as completed and calculate statistics."""
    service = LifeWordsService(db)
    return await service.complete_session(session_id, user_id)
