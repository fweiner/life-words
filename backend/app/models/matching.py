"""Pydantic models for answer matching endpoints."""
from typing import List, Optional
from pydantic import BaseModel


class MatchSettings(BaseModel):
    """User accommodation settings that control matching behavior."""
    match_acceptable_alternatives: bool = True
    match_partial_substring: bool = True
    match_word_overlap: bool = True
    match_stop_word_filtering: bool = True
    match_synonyms: bool = True
    match_first_name_only: bool = True


class NameMatchRequest(BaseModel):
    """Request to evaluate a name-practice answer."""
    user_answer: str
    expected_name: str
    nickname: Optional[str] = None
    alternatives: List[str] = []
    settings: Optional[MatchSettings] = None


class NameMatchResponse(BaseModel):
    """Result of a name-practice match."""
    is_correct: bool
    matched_via: Optional[str] = None  # exact, nickname, first_name, partial, etc.


class QuestionMatchRequest(BaseModel):
    """Request to evaluate a question-practice answer."""
    user_answer: str
    expected_answer: str
    acceptable_answers: List[str] = []
    settings: Optional[MatchSettings] = None


class QuestionMatchResponse(BaseModel):
    """Result of a question-practice match."""
    is_correct: bool
    is_partial: bool = False
    score: float = 0.0


class InformationMatchRequest(BaseModel):
    """Request to evaluate an information-practice answer."""
    user_answer: str
    expected_value: str
    field_name: str


class InformationMatchResponse(BaseModel):
    """Result of an information-practice match."""
    is_correct: bool
    confidence: float = 0.0


class WordFindingMatchRequest(BaseModel):
    """Request to evaluate a word-finding answer."""
    user_answer: str
    expected_name: str
    alternatives: List[str] = []


class WordFindingMatchResponse(BaseModel):
    """Result of a word-finding match."""
    is_correct: bool


class ExtractAnswerRequest(BaseModel):
    """Request to extract an answer from a speech transcript."""
    transcript: str


class ExtractAnswerResponse(BaseModel):
    """Extracted answer from speech."""
    answer: str
