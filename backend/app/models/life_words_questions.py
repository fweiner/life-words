"""Life Words Question Session Pydantic models."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class QuestionType:
    """Question types for Life Words recall."""
    RELATIONSHIP = 1  # "What is [Name]'s relationship to you?"
    ASSOCIATION = 2   # "Where do you usually see [Name]?"
    INTERESTS = 3     # "What does [Name] enjoy doing?"
    PERSONALITY = 4   # "How would you describe [Name]?"
    NAME_FROM_DESC = 5  # "Who is your [relationship] who likes [interest]?"


class LifeWordsQuestionSessionCreate(BaseModel):
    """Create question session request."""
    contact_ids: Optional[list[str]] = None  # None = use all active contacts


class LifeWordsQuestionSessionResponse(BaseModel):
    """Question session response."""
    id: str
    user_id: str
    contact_ids: list[str]
    is_completed: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_questions: int
    total_correct: int
    average_response_time: float
    average_clarity_score: float
    statistics: Optional[Dict[str, Any]] = None


class GeneratedQuestion(BaseModel):
    """A generated question about a contact."""
    contact_id: str
    contact_name: str
    contact_photo_url: str
    question_type: int
    question_text: str
    expected_answer: str
    acceptable_answers: list[str]  # Alternative correct answers


class LifeWordsQuestionResponseCreate(BaseModel):
    """Submit answer to a question."""
    contact_id: str
    question_type: int
    question_text: str
    expected_answer: str
    user_answer: Optional[str] = None
    is_correct: bool
    is_partial: bool = False
    response_time: Optional[int] = None  # milliseconds
    clarity_score: Optional[float] = Field(None, ge=0, le=1)  # speech confidence
    correctness_score: Optional[float] = Field(None, ge=0, le=1)  # semantic match


class LifeWordsQuestionResponseResponse(BaseModel):
    """Question response record."""
    id: str
    session_id: str
    contact_id: str
    question_type: int
    question_text: str
    expected_answer: str
    user_answer: Optional[str] = None
    is_correct: bool
    is_partial: bool
    response_time: Optional[int] = None
    clarity_score: Optional[float] = None
    correctness_score: Optional[float] = None
    created_at: datetime
