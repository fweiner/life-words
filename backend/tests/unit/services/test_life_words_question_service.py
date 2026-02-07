"""Unit tests for life words question service."""
import pytest
from datetime import datetime, timezone
from fastapi import HTTPException


SAMPLE_CONTACT_1 = {
    "id": "contact-001",
    "user_id": "user-123",
    "name": "John Smith",
    "nickname": "Johnny",
    "pronunciation": None,
    "relationship": "friend",
    "photo_url": "https://example.com/john.jpg",
    "category": None,
    "first_letter": "J",
    "description": "Tall guy from work",
    "association": "the office",
    "location_context": "at work",
    "interests": "playing golf",
    "personality": "outgoing and friendly",
    "values": None,
    "social_behavior": None,
    "is_active": True,
    "is_complete": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

SAMPLE_CONTACT_2 = {
    "id": "contact-002",
    "user_id": "user-123",
    "name": "Mary Johnson",
    "nickname": None,
    "pronunciation": None,
    "relationship": "daughter",
    "photo_url": "https://example.com/mary.jpg",
    "category": None,
    "first_letter": "M",
    "description": "Lives nearby",
    "association": "home",
    "location_context": "at home",
    "interests": "reading books",
    "personality": "calm and kind",
    "values": None,
    "social_behavior": None,
    "is_active": True,
    "is_complete": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

SAMPLE_CONTACT_3 = {
    "id": "contact-003",
    "user_id": "user-123",
    "name": "Bob",
    "nickname": None,
    "pronunciation": None,
    "relationship": "spouse",
    "photo_url": "https://example.com/bob.jpg",
    "category": None,
    "first_letter": "B",
    "description": None,
    "association": None,
    "location_context": None,
    "interests": None,
    "personality": None,
    "values": None,
    "social_behavior": None,
    "is_active": True,
    "is_complete": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

SAMPLE_SESSION = {
    "id": "session-789",
    "user_id": "user-123",
    "contact_ids": ["contact-001", "contact-002"],
    "is_completed": False,
    "started_at": datetime.now(timezone.utc).isoformat(),
    "completed_at": None,
    "total_questions": 5,
    "total_correct": 0,
    "average_response_time": 0,
    "average_clarity_score": 0,
    "statistics": None,
}

SAMPLE_RESPONSE = {
    "id": "response-001",
    "session_id": "session-789",
    "user_id": "user-123",
    "contact_id": "contact-001",
    "question_type": 1,
    "question_text": "What is John Smith's relationship to you?",
    "expected_answer": "friend",
    "user_answer": "friend",
    "is_correct": True,
    "is_partial": False,
    "response_time": 3500,
    "clarity_score": 0.95,
    "correctness_score": 1.0,
    "created_at": datetime.now(timezone.utc).isoformat(),
}


# ---- extract_significant_words ----


def test_extract_significant_words_removes_stop_words():
    """Test that stop words are removed from text."""
    from app.services.life_words_question_service import extract_significant_words

    result = extract_significant_words("the big red dog in the park")
    assert "the" not in result
    assert "in" not in result
    assert "big" in result
    assert "red" in result
    assert "dog" in result
    assert "park" in result


def test_extract_significant_words_empty_string():
    """Test extracting from empty string returns empty set."""
    from app.services.life_words_question_service import extract_significant_words

    result = extract_significant_words("")
    assert result == set()


def test_extract_significant_words_all_stop_words():
    """Test that text of only stop words returns empty set."""
    from app.services.life_words_question_service import extract_significant_words

    result = extract_significant_words("the a an is are was")
    assert result == set()


# ---- find_synonym_match ----


def test_find_synonym_match_true():
    """Test that synonyms in the same group match."""
    from app.services.life_words_question_service import find_synonym_match

    assert find_synonym_match("spouse", "husband") is True
    assert find_synonym_match("daughter", "girl") is True
    assert find_synonym_match("friend", "buddy") is True


def test_find_synonym_match_false():
    """Test that unrelated words do not match."""
    from app.services.life_words_question_service import find_synonym_match

    assert find_synonym_match("spouse", "friend") is False
    assert find_synonym_match("dog", "airplane") is False


def test_find_synonym_match_case_insensitive():
    """Test that synonym matching is case-insensitive."""
    from app.services.life_words_question_service import find_synonym_match

    assert find_synonym_match("Spouse", "HUSBAND") is True
    assert find_synonym_match("  friend  ", "buddy") is True


# ---- words_are_similar ----


def test_words_are_similar_matching():
    """Test similar word sets return True with score >= 0.5."""
    from app.services.life_words_question_service import words_are_similar

    is_similar, score = words_are_similar({"husband"}, {"spouse"})
    assert is_similar is True
    assert score >= 0.5


def test_words_are_similar_not_matching():
    """Test dissimilar word sets return False."""
    from app.services.life_words_question_service import words_are_similar

    is_similar, score = words_are_similar({"airplane"}, {"banana"})
    assert is_similar is False
    assert score == 0.0


def test_words_are_similar_empty_sets():
    """Test empty word sets return False with 0.0 score."""
    from app.services.life_words_question_service import words_are_similar

    is_similar, score = words_are_similar(set(), {"hello"})
    assert is_similar is False
    assert score == 0.0

    is_similar2, score2 = words_are_similar({"hello"}, set())
    assert is_similar2 is False
    assert score2 == 0.0


def test_words_are_similar_exact_overlap():
    """Test identical word sets get full score."""
    from app.services.life_words_question_service import words_are_similar

    is_similar, score = words_are_similar({"golf", "tennis"}, {"golf", "tennis"})
    assert is_similar is True
    assert score == 1.0


# ---- get_relationship_alternatives ----


def test_get_relationship_alternatives_known():
    """Test known relationship returns predefined alternatives."""
    from app.services.life_words_question_service import get_relationship_alternatives

    alts = get_relationship_alternatives("child")
    assert "child" in alts
    assert "son" in alts
    assert "daughter" in alts


def test_get_relationship_alternatives_case_insensitive():
    """Test that relationship lookup is case-insensitive."""
    from app.services.life_words_question_service import get_relationship_alternatives

    alts = get_relationship_alternatives("SPOUSE")
    assert "husband" in alts
    assert "wife" in alts


def test_get_relationship_alternatives_unknown():
    """Test unknown relationship returns fallback list."""
    from app.services.life_words_question_service import get_relationship_alternatives

    alts = get_relationship_alternatives("cousin")
    assert "cousin" in alts
    assert "Cousin" in alts


# ---- evaluate_answer: exact match ----


def test_evaluate_answer_exact_match():
    """Test exact match returns correct with score 1.0."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer("friend", "friend", [])
    assert is_correct is True
    assert is_partial is False
    assert score == 1.0


def test_evaluate_answer_exact_match_case_insensitive():
    """Test exact match is case-insensitive."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer("FRIEND", "friend", [])
    assert is_correct is True
    assert is_partial is False
    assert score == 1.0


# ---- evaluate_answer: empty answer ----


def test_evaluate_answer_empty_answer():
    """Test empty answer returns incorrect."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer("", "friend", [])
    assert is_correct is False
    assert is_partial is False
    assert score == 0.0


def test_evaluate_answer_none_answer():
    """Test None answer returns incorrect."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer(None, "friend", [])
    assert is_correct is False
    assert is_partial is False
    assert score == 0.0


# ---- evaluate_answer: acceptable alternatives ----


def test_evaluate_answer_acceptable_alternative():
    """Test matching an acceptable alternative returns correct."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer(
        "son", "child", ["son", "daughter", "kid"]
    )
    assert is_correct is True
    assert is_partial is False
    assert score == 1.0


def test_evaluate_answer_acceptable_alternative_case_insensitive():
    """Test acceptable alternatives matching is case-insensitive."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer(
        "MY SON", "child", ["my son", "my daughter"]
    )
    assert is_correct is True
    assert score == 1.0


# ---- evaluate_answer: first name only ----


def test_evaluate_answer_first_name_only():
    """Test first name matches full name partially."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer(
        "john", "John Smith", []
    )
    assert is_correct is True
    assert is_partial is True
    assert score == 0.9


def test_evaluate_answer_first_name_no_space_in_expected():
    """Test first name match skipped when expected has no space."""
    from app.services.life_words_question_service import evaluate_answer

    # "john" == "john" is exact match, not first-name match
    is_correct, is_partial, score = evaluate_answer(
        "john", "John", []
    )
    assert is_correct is True
    assert is_partial is False
    assert score == 1.0


# ---- evaluate_answer: substring containment ----


def test_evaluate_answer_substring_user_contains_expected():
    """Test user answer containing expected answer matches as partial."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer(
        "playing golf at the club", "playing golf", []
    )
    assert is_correct is True
    assert is_partial is True
    assert score == 0.8


def test_evaluate_answer_substring_expected_contains_user():
    """Test expected answer containing user answer matches as partial."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer(
        "golf", "playing golf", []
    )
    assert is_correct is True
    assert is_partial is True
    assert score == 0.8


# ---- evaluate_answer: word overlap ----


def test_evaluate_answer_word_overlap():
    """Test word overlap with score >= 0.5 matches."""
    from app.services.life_words_question_service import evaluate_answer

    # "playing" and "golf" overlap; 2 out of max(2,2) = 1.0 score
    is_correct, is_partial, score = evaluate_answer(
        "golf playing", "playing golf", []
    )
    # This would be exact match after normalization or word overlap
    assert is_correct is True


def test_evaluate_answer_word_overlap_insufficient():
    """Test word overlap below 0.5 threshold does not match via overlap alone."""
    from app.services.life_words_question_service import evaluate_answer

    # Disable substring and stop word and synonym to isolate word overlap
    settings = {
        "match_partial_substring": False,
        "match_stop_word_filtering": False,
        "match_synonyms": False,
        "match_first_name_only": False,
        "match_acceptable_alternatives": False,
    }
    is_correct, is_partial, score = evaluate_answer(
        "alpha bravo charlie delta", "charlie echo foxtrot golf hotel",
        [], settings
    )
    # 1 overlap out of max(4,5) = 0.2 < 0.5
    assert is_correct is False


# ---- evaluate_answer: stop word filtering ----


def test_evaluate_answer_stop_word_filtering():
    """Test stop word filtering finds significant word match."""
    from app.services.life_words_question_service import evaluate_answer

    # Without stop word filtering, "the park" and "going to the park" differ
    # With it, "park" matches "park"
    settings = {
        "match_partial_substring": False,
        "match_word_overlap": False,
        "match_synonyms": False,
        "match_first_name_only": False,
    }
    is_correct, is_partial, score = evaluate_answer(
        "the park is nice", "at the park", [], settings
    )
    assert is_correct is True
    assert is_partial is True
    assert score >= 0.7


def test_evaluate_answer_stop_word_filtering_no_significant_match():
    """Test stop word filtering with no significant overlap fails."""
    from app.services.life_words_question_service import evaluate_answer

    settings = {
        "match_partial_substring": False,
        "match_word_overlap": False,
        "match_synonyms": False,
        "match_first_name_only": False,
        "match_acceptable_alternatives": False,
    }
    is_correct, is_partial, score = evaluate_answer(
        "the airplane", "the banana", [], settings
    )
    assert is_correct is False


# ---- evaluate_answer: synonym matching ----


def test_evaluate_answer_synonym_match():
    """Test synonym matching finds semantic equivalents."""
    from app.services.life_words_question_service import evaluate_answer

    settings = {
        "match_partial_substring": False,
        "match_word_overlap": False,
        "match_stop_word_filtering": False,
        "match_first_name_only": False,
        "match_acceptable_alternatives": False,
    }
    is_correct, is_partial, score = evaluate_answer(
        "husband", "spouse", [], settings
    )
    assert is_correct is True
    assert is_partial is True


def test_evaluate_answer_synonym_match_individual_words():
    """Test synonym matching via individual word pairs."""
    from app.services.life_words_question_service import evaluate_answer

    settings = {
        "match_partial_substring": False,
        "match_word_overlap": False,
        "match_stop_word_filtering": False,
        "match_first_name_only": False,
        "match_acceptable_alternatives": False,
    }
    # "buddy" is a synonym of "friend" via individual word scan
    is_correct, is_partial, score = evaluate_answer(
        "my buddy", "my friend", [], settings
    )
    assert is_correct is True
    assert is_partial is True


def test_evaluate_answer_synonym_with_stop_word_filtering():
    """Test synonym matching combined with stop word filtering."""
    from app.services.life_words_question_service import evaluate_answer

    settings = {
        "match_partial_substring": False,
        "match_word_overlap": False,
        "match_first_name_only": False,
        "match_acceptable_alternatives": False,
        "match_stop_word_filtering": True,
        "match_synonyms": True,
    }
    # "calm" and "relaxed" are synonyms; stop words "is" "very" filtered
    is_correct, is_partial, score = evaluate_answer(
        "she is very relaxed", "he is calm", [], settings
    )
    assert is_correct is True
    assert is_partial is True


# ---- evaluate_answer: disabled accommodations ----


def test_evaluate_answer_all_accommodations_disabled():
    """Test with all accommodations disabled, only exact match works."""
    from app.services.life_words_question_service import evaluate_answer

    settings = {
        "match_acceptable_alternatives": False,
        "match_first_name_only": False,
        "match_partial_substring": False,
        "match_word_overlap": False,
        "match_stop_word_filtering": False,
        "match_synonyms": False,
    }
    # Exact match still works
    is_correct, is_partial, score = evaluate_answer(
        "friend", "friend", ["buddy", "pal"], settings
    )
    assert is_correct is True
    assert score == 1.0

    # Non-exact match fails when everything disabled
    is_correct2, is_partial2, score2 = evaluate_answer(
        "buddy", "friend", ["buddy", "pal"], settings
    )
    assert is_correct2 is False
    assert score2 == 0.0


def test_evaluate_answer_no_match_at_all():
    """Test completely wrong answer returns false."""
    from app.services.life_words_question_service import evaluate_answer

    is_correct, is_partial, score = evaluate_answer(
        "elephant", "friend", []
    )
    assert is_correct is False
    assert is_partial is False
    assert score == 0.0


def test_evaluate_answer_default_settings_none():
    """Test that None settings defaults to all accommodations enabled."""
    from app.services.life_words_question_service import evaluate_answer

    # With defaults, "husband" should match "spouse" via synonym
    is_correct, is_partial, score = evaluate_answer(
        "husband", "spouse", [], None
    )
    assert is_correct is True


# ---- generate_questions_for_contacts ----


def test_generate_questions_fewer_than_2_contacts():
    """Test generating questions with fewer than 2 contacts returns empty."""
    from app.services.life_words_question_service import generate_questions_for_contacts

    result = generate_questions_for_contacts([SAMPLE_CONTACT_1])
    assert result == []


def test_generate_questions_empty_contacts():
    """Test generating questions with empty list returns empty."""
    from app.services.life_words_question_service import generate_questions_for_contacts

    result = generate_questions_for_contacts([])
    assert result == []


def test_generate_questions_with_2_contacts():
    """Test generating questions with 2 contacts produces questions."""
    from app.services.life_words_question_service import generate_questions_for_contacts

    result = generate_questions_for_contacts([SAMPLE_CONTACT_1, SAMPLE_CONTACT_2])
    assert len(result) >= 4  # At least 4 questions (Q5 depends on interests)
    assert len(result) <= 5


def test_generate_questions_types():
    """Test generated questions cover the expected types."""
    from app.services.life_words_question_service import generate_questions_for_contacts
    from app.models.life_words_questions import QuestionType

    result = generate_questions_for_contacts([SAMPLE_CONTACT_1, SAMPLE_CONTACT_2])
    question_types = [q.question_type for q in result]

    assert QuestionType.RELATIONSHIP in question_types
    assert QuestionType.ASSOCIATION in question_types
    assert QuestionType.INTERESTS in question_types
    assert QuestionType.PERSONALITY in question_types


def test_generate_questions_relationship_has_alternatives():
    """Test relationship question includes alternative answers."""
    from app.services.life_words_question_service import generate_questions_for_contacts
    from app.models.life_words_questions import QuestionType

    result = generate_questions_for_contacts([SAMPLE_CONTACT_1, SAMPLE_CONTACT_2])
    rel_questions = [q for q in result if q.question_type == QuestionType.RELATIONSHIP]

    assert len(rel_questions) == 1
    assert len(rel_questions[0].acceptable_answers) > 1


def test_generate_questions_name_from_desc():
    """Test Q5 name-from-description is generated for contacts with interests."""
    from app.services.life_words_question_service import generate_questions_for_contacts
    from app.models.life_words_questions import QuestionType

    result = generate_questions_for_contacts([SAMPLE_CONTACT_1, SAMPLE_CONTACT_2])
    name_questions = [q for q in result if q.question_type == QuestionType.NAME_FROM_DESC]

    assert len(name_questions) == 1
    q = name_questions[0]
    assert q.expected_answer in [SAMPLE_CONTACT_1["name"], SAMPLE_CONTACT_2["name"]]


def test_generate_questions_contact_without_interests_or_personality():
    """Test question generation with contacts lacking optional fields."""
    from app.services.life_words_question_service import generate_questions_for_contacts

    # SAMPLE_CONTACT_3 has no interests, personality, or description
    result = generate_questions_for_contacts([SAMPLE_CONTACT_1, SAMPLE_CONTACT_3])
    # Should still generate questions; fallback values used
    assert len(result) >= 4


def test_generate_questions_name_from_desc_acceptable_answers():
    """Test Q5 name-from-desc includes first name and nickname in acceptable."""
    from app.services.life_words_question_service import generate_questions_for_contacts
    from app.models.life_words_questions import QuestionType

    result = generate_questions_for_contacts([SAMPLE_CONTACT_1, SAMPLE_CONTACT_2])
    name_questions = [q for q in result if q.question_type == QuestionType.NAME_FROM_DESC]

    assert len(name_questions) == 1
    q = name_questions[0]
    # Acceptable answers should include lowered full name and first name
    assert q.expected_answer.lower() in q.acceptable_answers or \
        q.expected_answer.split()[0].lower() in q.acceptable_answers


# ---- create_session ----


@pytest.mark.asyncio
async def test_create_session_success(mock_db):
    """Test creating a question session with enough contacts."""
    from app.services.life_words_question_service import LifeWordsQuestionService
    from app.models.life_words_questions import LifeWordsQuestionSessionCreate

    mock_db.query.return_value = [SAMPLE_CONTACT_1, SAMPLE_CONTACT_2]
    mock_db.insert.return_value = [SAMPLE_SESSION]

    service = LifeWordsQuestionService(mock_db)
    result = await service.create_session(
        "user-123",
        LifeWordsQuestionSessionCreate()
    )

    assert "session" in result
    assert "questions" in result
    assert "contacts" in result
    assert len(result["questions"]) >= 4
    mock_db.insert.assert_called_once()


@pytest.mark.asyncio
async def test_create_session_with_specific_contact_ids(mock_db):
    """Test creating a session filtering by specific contact IDs."""
    from app.services.life_words_question_service import LifeWordsQuestionService
    from app.models.life_words_questions import LifeWordsQuestionSessionCreate

    mock_db.query.return_value = [SAMPLE_CONTACT_1, SAMPLE_CONTACT_2, SAMPLE_CONTACT_3]
    mock_db.insert.return_value = [SAMPLE_SESSION]

    service = LifeWordsQuestionService(mock_db)
    result = await service.create_session(
        "user-123",
        LifeWordsQuestionSessionCreate(contact_ids=["contact-001", "contact-002"])
    )

    assert "session" in result
    # Contacts filtered to only requested IDs
    assert len(result["contacts"]) == 2


@pytest.mark.asyncio
async def test_create_session_not_enough_contacts(mock_db):
    """Test creating a session with fewer than minimum contacts raises 400."""
    from app.services.life_words_question_service import LifeWordsQuestionService
    from app.models.life_words_questions import LifeWordsQuestionSessionCreate

    mock_db.query.return_value = [SAMPLE_CONTACT_1]

    service = LifeWordsQuestionService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_session(
            "user-123",
            LifeWordsQuestionSessionCreate()
        )

    assert exc_info.value.status_code == 400
    assert "At least" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_session_no_contacts(mock_db):
    """Test creating a session with no contacts raises 400."""
    from app.services.life_words_question_service import LifeWordsQuestionService
    from app.models.life_words_questions import LifeWordsQuestionSessionCreate

    mock_db.query.return_value = []

    service = LifeWordsQuestionService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_session(
            "user-123",
            LifeWordsQuestionSessionCreate()
        )

    assert exc_info.value.status_code == 400


# ---- get_session ----


@pytest.mark.asyncio
async def test_get_session_success(mock_db):
    """Test getting a question session with responses."""
    from app.services.life_words_question_service import LifeWordsQuestionService

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],                                     # session query
        [SAMPLE_RESPONSE],                                    # responses query
        [SAMPLE_CONTACT_1, SAMPLE_CONTACT_2, SAMPLE_CONTACT_3],  # contacts query
    ]

    service = LifeWordsQuestionService(mock_db)
    result = await service.get_session("session-789", "user-123")

    assert result["session"]["id"] == "session-789"
    assert len(result["responses"]) == 1
    # Only contacts matching session contact_ids returned
    assert len(result["contacts"]) == 2


@pytest.mark.asyncio
async def test_get_session_not_found(mock_db):
    """Test getting a non-existent session raises 404."""
    from app.services.life_words_question_service import LifeWordsQuestionService

    mock_db.query.return_value = []

    service = LifeWordsQuestionService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_session("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


# ---- save_response ----


@pytest.mark.asyncio
async def test_save_response_success(mock_db):
    """Test saving a response to a question."""
    from app.services.life_words_question_service import LifeWordsQuestionService
    from app.models.life_words_questions import LifeWordsQuestionResponseCreate

    mock_db.query.return_value = [SAMPLE_SESSION]
    mock_db.insert.return_value = [SAMPLE_RESPONSE]

    service = LifeWordsQuestionService(mock_db)
    result = await service.save_response(
        "session-789", "user-123",
        LifeWordsQuestionResponseCreate(
            contact_id="contact-001",
            question_type=1,
            question_text="What is John's relationship?",
            expected_answer="friend",
            user_answer="friend",
            is_correct=True,
            is_partial=False,
            response_time=3500,
            clarity_score=0.95,
            correctness_score=1.0,
        )
    )

    assert result["response"]["is_correct"] is True
    mock_db.insert.assert_called_once()
    call_data = mock_db.insert.call_args.args[1]
    assert call_data["session_id"] == "session-789"
    assert call_data["user_id"] == "user-123"


@pytest.mark.asyncio
async def test_save_response_session_not_found(mock_db):
    """Test saving a response for a non-existent session raises 404."""
    from app.services.life_words_question_service import LifeWordsQuestionService
    from app.models.life_words_questions import LifeWordsQuestionResponseCreate

    mock_db.query.return_value = []

    service = LifeWordsQuestionService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.save_response(
            "nonexistent", "user-123",
            LifeWordsQuestionResponseCreate(
                contact_id="contact-001",
                question_type=1,
                question_text="Test?",
                expected_answer="friend",
                is_correct=True,
            )
        )

    assert exc_info.value.status_code == 404


# ---- complete_session ----


@pytest.mark.asyncio
async def test_complete_session_success(mock_db):
    """Test completing a session calculates statistics correctly."""
    from app.services.life_words_question_service import LifeWordsQuestionService

    response2 = {
        **SAMPLE_RESPONSE,
        "id": "response-002",
        "contact_id": "contact-002",
        "question_type": 2,
        "is_correct": False,
        "is_partial": True,
        "response_time": 5000,
        "clarity_score": 0.8,
        "correctness_score": 0.6,
    }

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],                    # session query
        [SAMPLE_RESPONSE, response2],        # responses query
    ]
    updated_session = {**SAMPLE_SESSION, "is_completed": True}
    mock_db.update.return_value = [updated_session]

    service = LifeWordsQuestionService(mock_db)
    result = await service.complete_session("session-789", "user-123")

    assert "session" in result
    assert "statistics" in result

    stats = result["statistics"]
    assert stats["total_questions"] == 2
    assert stats["total_correct"] == 1
    assert stats["total_partial"] == 1
    assert stats["accuracy_percentage"] == 50.0
    assert stats["average_response_time_ms"] == round((3500 + 5000) / 2, 0)
    assert stats["average_clarity_score"] == round((0.95 + 0.8) / 2, 2)
    assert stats["average_correctness_score"] == round((1.0 + 0.6) / 2, 2)

    mock_db.update.assert_called_once()
    update_data = mock_db.update.call_args.args[2]
    assert update_data["is_completed"] is True
    assert update_data["total_correct"] == 1


@pytest.mark.asyncio
async def test_complete_session_no_responses(mock_db):
    """Test completing a session with no responses raises 400."""
    from app.services.life_words_question_service import LifeWordsQuestionService

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],  # session found
        [],                 # no responses
    ]

    service = LifeWordsQuestionService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.complete_session("session-789", "user-123")

    assert exc_info.value.status_code == 400
    assert "No responses" in exc_info.value.detail


@pytest.mark.asyncio
async def test_complete_session_not_found(mock_db):
    """Test completing a non-existent session raises 404."""
    from app.services.life_words_question_service import LifeWordsQuestionService

    mock_db.query.return_value = []

    service = LifeWordsQuestionService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.complete_session("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_complete_session_by_question_type_breakdown(mock_db):
    """Test that complete_session produces per-question-type statistics."""
    from app.services.life_words_question_service import LifeWordsQuestionService

    responses = [
        {**SAMPLE_RESPONSE, "id": "r1", "question_type": 1, "is_correct": True, "is_partial": False},
        {**SAMPLE_RESPONSE, "id": "r2", "question_type": 1, "is_correct": False, "is_partial": False},
        {**SAMPLE_RESPONSE, "id": "r3", "question_type": 2, "is_correct": True, "is_partial": False},
    ]

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],
        responses,
    ]
    mock_db.update.return_value = [SAMPLE_SESSION]

    service = LifeWordsQuestionService(mock_db)
    result = await service.complete_session("session-789", "user-123")

    by_type = result["statistics"]["by_question_type"]
    assert "1" in by_type
    assert by_type["1"]["total"] == 2
    assert by_type["1"]["correct"] == 1
    assert "2" in by_type
    assert by_type["2"]["total"] == 1
    assert by_type["2"]["correct"] == 1


@pytest.mark.asyncio
async def test_complete_session_null_optional_fields(mock_db):
    """Test completing a session when some responses lack optional fields."""
    from app.services.life_words_question_service import LifeWordsQuestionService

    response_no_optionals = {
        **SAMPLE_RESPONSE,
        "id": "r-no-opts",
        "response_time": None,
        "clarity_score": None,
        "correctness_score": None,
    }

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],
        [response_no_optionals],
    ]
    mock_db.update.return_value = [SAMPLE_SESSION]

    service = LifeWordsQuestionService(mock_db)
    result = await service.complete_session("session-789", "user-123")

    stats = result["statistics"]
    assert stats["average_response_time_ms"] == 0
    assert stats["average_clarity_score"] == 0
    assert stats["average_correctness_score"] == 0
