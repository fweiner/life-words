"""Answer matching endpoints for evaluating user responses."""
from fastapi import APIRouter
from app.models.matching import (
    NameMatchRequest,
    NameMatchResponse,
    QuestionMatchRequest,
    QuestionMatchResponse,
    InformationMatchRequest,
    InformationMatchResponse,
    WordFindingMatchRequest,
    WordFindingMatchResponse,
    ExtractAnswerRequest,
    ExtractAnswerResponse,
)
from app.services.answer_matching_service import (
    match_name_answer,
    match_question_answer,
    match_information_answer,
    match_word_finding_answer,
    extract_answer,
)

router = APIRouter()


@router.post("/evaluate/name")
async def evaluate_name_answer(req: NameMatchRequest) -> NameMatchResponse:
    """Evaluate a name-practice answer against expected name."""
    settings = req.settings.model_dump() if req.settings else None
    is_correct, matched_via = match_name_answer(
        req.user_answer,
        req.expected_name,
        nickname=req.nickname,
        alternatives=req.alternatives,
        settings=settings,
    )
    return NameMatchResponse(is_correct=is_correct, matched_via=matched_via)


@router.post("/evaluate/question")
async def evaluate_question_answer(req: QuestionMatchRequest) -> QuestionMatchResponse:
    """Evaluate a question-practice answer."""
    settings = req.settings.model_dump() if req.settings else None
    is_correct, is_partial, score = match_question_answer(
        req.user_answer,
        req.expected_answer,
        acceptable=req.acceptable_answers,
        settings=settings,
    )
    return QuestionMatchResponse(
        is_correct=is_correct, is_partial=is_partial, score=score
    )


@router.post("/evaluate/information")
async def evaluate_information_answer(
    req: InformationMatchRequest,
) -> InformationMatchResponse:
    """Evaluate an information-practice answer (phone, zip, date, text, etc.)."""
    is_correct, confidence = match_information_answer(
        req.user_answer, req.expected_value, req.field_name
    )
    return InformationMatchResponse(is_correct=is_correct, confidence=confidence)


@router.post("/evaluate/word-finding")
async def evaluate_word_finding_answer(
    req: WordFindingMatchRequest,
) -> WordFindingMatchResponse:
    """Evaluate a word-finding answer (image naming)."""
    is_correct = match_word_finding_answer(
        req.user_answer, req.expected_name, req.alternatives
    )
    return WordFindingMatchResponse(is_correct=is_correct)


@router.post("/extract-answer")
async def extract_answer_endpoint(req: ExtractAnswerRequest) -> ExtractAnswerResponse:
    """Extract the most likely answer from a speech transcript."""
    answer = extract_answer(req.transcript)
    return ExtractAnswerResponse(answer=answer)
