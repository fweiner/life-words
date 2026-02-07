"""Treatment-related Pydantic models."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class TreatmentSessionCreate(BaseModel):
    """Create treatment session request."""
    treatment_type: str
    data: Optional[Dict[str, Any]] = {}


class TreatmentSessionUpdate(BaseModel):
    """Update treatment session request."""
    completed_at: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None


class TreatmentSessionResponse(BaseModel):
    """Treatment session response."""
    id: str
    user_id: str
    treatment_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    data: Dict[str, Any]
    created_at: datetime


class TreatmentResultCreate(BaseModel):
    """Create treatment result request."""
    session_id: str
    score: Optional[int] = None
    details: Optional[Dict[str, Any]] = {}


class TreatmentResultResponse(BaseModel):
    """Treatment result response."""
    id: str
    session_id: str
    user_id: str
    score: Optional[int] = None
    details: Dict[str, Any]
    created_at: datetime


class UserProgressResponse(BaseModel):
    """User progress response."""
    id: str
    user_id: str
    treatment_type: str
    total_sessions: int
    average_score: Optional[float] = None
    last_session_at: Optional[datetime] = None
    updated_at: datetime


class WordFindingSessionCreate(BaseModel):
    """Create word-finding session request."""
    pass  # No parameters needed, stimuli selected randomly


class WordFindingResponse(BaseModel):
    """Word-finding response submission."""
    stimulus_id: int
    is_correct: bool
    cues_used: int = 0
    response_time: Optional[float] = None
    user_answer: Optional[str] = None
    correct_answer: str
