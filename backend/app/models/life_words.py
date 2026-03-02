"""Life Words (Find My Life Words) Pydantic models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PersonalContactCreate(BaseModel):
    """Create personal contact request."""
    name: str
    nickname: Optional[str] = None
    pronunciation: Optional[str] = None  # How to pronounce the name (e.g., "Wyner" for "Weiner")
    relationship: str
    photo_url: str
    category: Optional[str] = None
    description: Optional[str] = None
    association: Optional[str] = None
    location_context: Optional[str] = None
    # Personal characteristics
    interests: Optional[str] = None
    personality: Optional[str] = None
    values: Optional[str] = None
    social_behavior: Optional[str] = None


class PersonalContactUpdate(BaseModel):
    """Update personal contact request."""
    name: Optional[str] = None
    nickname: Optional[str] = None
    pronunciation: Optional[str] = None
    relationship: Optional[str] = None
    photo_url: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    association: Optional[str] = None
    location_context: Optional[str] = None
    # Personal characteristics
    interests: Optional[str] = None
    personality: Optional[str] = None
    values: Optional[str] = None
    social_behavior: Optional[str] = None


class PersonalContactResponse(BaseModel):
    """Personal contact response."""
    id: str
    user_id: str
    name: str
    nickname: Optional[str] = None
    pronunciation: Optional[str] = None
    relationship: str
    photo_url: str
    category: Optional[str] = None
    first_letter: Optional[str] = None
    description: Optional[str] = None
    association: Optional[str] = None
    location_context: Optional[str] = None
    # Personal characteristics
    interests: Optional[str] = None
    personality: Optional[str] = None
    values: Optional[str] = None
    social_behavior: Optional[str] = None
    is_active: bool
    is_complete: bool = True
    created_at: datetime
    updated_at: datetime


class QuickAddContactCreate(BaseModel):
    """Quick add contact - photo only, creates incomplete draft."""
    photo_url: str
    category: str = "family"  # 'family' for people, 'pet' for pets


class LifeWordsStatusResponse(BaseModel):
    """Life words status response."""
    contact_count: int
    item_count: int
    total_count: int
    can_start_session: bool
    min_contacts_required: int = 2


class LifeWordsSessionCreate(BaseModel):
    """Create life words session request."""
    contact_ids: Optional[list[str]] = None  # None = use all active contacts
    category: Optional[str] = None  # "people", "items", or None for all


class LifeWordsSessionResponse(BaseModel):
    """Life words session response."""
    id: str
    user_id: str
    contact_ids: list[str]
    is_completed: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_correct: int = 0
    total_incorrect: int = 0
    average_cues_used: float = 0.0
    average_response_time: float = 0.0
    contacts: Optional[list[PersonalContactResponse]] = None


class LifeWordsResponseCreate(BaseModel):
    """Life words response submission."""
    contact_id: str
    is_correct: bool
    cues_used: int = 0
    response_time: Optional[float] = None
    user_answer: Optional[str] = None
    correct_answer: str
    speech_confidence: Optional[float] = None
