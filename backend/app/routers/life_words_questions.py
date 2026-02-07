"""Life Words Question-Based Recall endpoints."""
from typing import List, Dict, Any
from fastapi import APIRouter
from app.core.dependencies import CurrentUserId, Database
from app.models.life_words_questions import (
    LifeWordsQuestionSessionCreate,
    LifeWordsQuestionResponseCreate,
)
from app.services.life_words_question_service import (
    LifeWordsQuestionService,
    evaluate_answer,
)

router = APIRouter()


@router.post("/question-sessions")
async def create_question_session(
    session_data: LifeWordsQuestionSessionCreate,
    user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Create a new question-based session and generate questions."""
    service = LifeWordsQuestionService(db)
    return await service.create_session(user_id, session_data)


@router.get("/question-sessions/{session_id}")
async def get_question_session(
    session_id: str, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Get question session with responses."""
    service = LifeWordsQuestionService(db)
    return await service.get_session(session_id, user_id)


@router.post("/question-sessions/{session_id}/responses")
async def save_question_response(
    session_id: str, response_data: LifeWordsQuestionResponseCreate,
    user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Save a response to a question."""
    service = LifeWordsQuestionService(db)
    return await service.save_response(session_id, user_id, response_data)


@router.put("/question-sessions/{session_id}/complete")
async def complete_question_session(
    session_id: str, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Complete a question session and calculate statistics."""
    service = LifeWordsQuestionService(db)
    return await service.complete_session(session_id, user_id)


@router.post("/evaluate-answer")
async def evaluate_answer_endpoint(
    user_id: CurrentUserId,
    expected_answer: str,
    user_answer: str,
    acceptable_answers: List[str] = []
) -> Dict[str, Any]:
    """Evaluate an answer against expected (utility endpoint)."""
    is_correct, is_partial, score = evaluate_answer(user_answer, expected_answer, acceptable_answers)
    return {
        "is_correct": is_correct,
        "is_partial": is_partial,
        "correctness_score": score,
    }
