"""Life Words Information Practice Pydantic models."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class InformationItem(BaseModel):
    """A single information item to teach and test."""
    field_name: str  # e.g., 'phone_number', 'address_city'
    field_label: str  # e.g., 'phone number', 'city'
    teach_text: str  # e.g., "Your phone number is 555-1234"
    question_text: str  # e.g., "What is your phone number?"
    expected_answer: str  # The correct answer
    hint_text: str  # e.g., "The first digit is 5"


class InformationStatusResponse(BaseModel):
    """Status response for information practice availability."""
    can_start_session: bool
    filled_fields_count: int
    min_fields_required: int = 5


class LifeWordsInformationSessionCreate(BaseModel):
    """Create information practice session request."""
    pass  # No parameters needed, items selected randomly from profile


class LifeWordsInformationSessionResponse(BaseModel):
    """Information practice session response."""
    id: str
    user_id: str
    is_completed: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_items: int
    total_correct: int
    total_hints_used: int
    total_timeouts: int
    average_response_time: float
    statistics: Optional[Dict[str, Any]] = None


class LifeWordsInformationResponseCreate(BaseModel):
    """Information practice response submission."""
    field_name: str
    field_label: str
    teach_text: str
    question_text: str
    expected_answer: str
    hint_text: Optional[str] = None
    user_answer: Optional[str] = None
    is_correct: bool
    used_hint: bool = False
    timed_out: bool = False
    response_time: Optional[int] = None  # milliseconds


class LifeWordsInformationResponseResponse(BaseModel):
    """Information practice response record."""
    id: str
    session_id: str
    field_name: str
    field_label: str
    teach_text: str
    question_text: str
    expected_answer: str
    hint_text: Optional[str] = None
    user_answer: Optional[str] = None
    is_correct: bool
    used_hint: bool
    timed_out: bool
    response_time: Optional[int] = None
    created_at: datetime
