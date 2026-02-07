"""Short-Term Memory Pydantic models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class STMGroceryItemResponse(BaseModel):
    """Grocery item response."""
    id: str
    name: str
    category: str


class STMSessionCreate(BaseModel):
    """Create short-term memory session request."""
    list_length: int = Field(..., ge=2, le=5, description="Number of items per list (2-5)")


class STMSessionResponse(BaseModel):
    """Short-term memory session response."""
    id: str
    user_id: str
    list_length: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_correct: int
    total_trials: int


class STMTrialCreate(BaseModel):
    """Create a trial within a session."""
    session_id: str
    trial_number: int = Field(..., ge=1, le=10)
    item_ids: list[str]  # List of grocery item IDs for this trial


class STMTrialResponse(BaseModel):
    """Trial response."""
    id: str
    session_id: str
    trial_number: int
    list_length: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    items_correct: int
    is_fully_correct: bool
    items: Optional[list[STMGroceryItemResponse]] = None


class STMRecallAttemptCreate(BaseModel):
    """Record a recall attempt."""
    trial_id: str
    target_item_name: str
    spoken_item: Optional[str] = None
    match_confidence: Optional[float] = Field(None, ge=0, le=1)
    is_correct: bool
    is_partial: bool = False
    time_to_recall: Optional[int] = None  # milliseconds


class STMRecallAttemptResponse(BaseModel):
    """Recall attempt response."""
    id: str
    trial_id: str
    target_item_name: str
    spoken_item: Optional[str] = None
    match_confidence: Optional[float] = None
    is_correct: bool
    is_partial: bool
    time_to_recall: Optional[int] = None
    created_at: datetime


class STMCompleteTrialRequest(BaseModel):
    """Complete a trial with recall attempts."""
    recall_attempts: list[STMRecallAttemptCreate]


class STMProgressResponse(BaseModel):
    """User's STM progress statistics."""
    total_sessions: int
    total_trials: int
    total_items_correct: int
    average_accuracy: float
    max_list_length: int


class STMSessionListResponse(BaseModel):
    """List of recent sessions."""
    sessions: list[STMSessionResponse]
    progress: STMProgressResponse
