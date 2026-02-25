"""Integration tests for Life Words Question endpoints."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


SAMPLE_USER_ID = "user-123"
SAMPLE_SESSION_ID = "session-123"

SAMPLE_CONTACTS = [
    {
        "id": "contact-1",
        "user_id": SAMPLE_USER_ID,
        "name": "John Smith",
        "nickname": "Johnny",
        "relationship": "son",
        "photo_url": "https://example.com/john.jpg",
        "interests": "playing soccer",
        "personality": "energetic and fun",
        "location_context": "at family dinners",
        "is_active": True,
    },
    {
        "id": "contact-2",
        "user_id": SAMPLE_USER_ID,
        "name": "Jane Smith",
        "relationship": "daughter",
        "photo_url": "https://example.com/jane.jpg",
        "interests": "reading books",
        "personality": "calm and thoughtful",
        "location_context": "at the library",
        "is_active": True,
    },
]

SAMPLE_SESSION = {
    "id": SAMPLE_SESSION_ID,
    "user_id": SAMPLE_USER_ID,
    "contact_ids": ["contact-1", "contact-2"],
    "is_completed": False,
    "total_questions": 5,
    "total_correct": 0,
    "average_response_time": 0,
    "average_clarity_score": 0,
}

SAMPLE_RESPONSE = {
    "id": "response-1",
    "session_id": SAMPLE_SESSION_ID,
    "user_id": SAMPLE_USER_ID,
    "contact_id": "contact-1",
    "question_type": 1,
    "question_text": "What is John Smith's relationship to you?",
    "expected_answer": "son",
    "user_answer": "son",
    "is_correct": True,
    "is_partial": False,
    "response_time": 2500,
    "clarity_score": 0.9,
    "correctness_score": 1.0,
}


def test_create_question_session_unauthorized(client):
    """Test that creating a question session requires authentication."""
    response = client.post("/api/life-words/question-sessions", json={})
    assert response.status_code == 401


def test_create_question_session_success(app, client, mock_user_id, mock_db):
    """Test successfully creating a question session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = SAMPLE_CONTACTS
    mock_db.insert.return_value = [SAMPLE_SESSION]

    response = client.post(
        "/api/life-words/question-sessions",
        json={},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "session" in data
    assert "questions" in data
    assert "contacts" in data
    assert len(data["questions"]) == 5


def test_create_question_session_not_enough_contacts(app, client, mock_user_id, mock_db):
    """Test that creating a question session requires at least 2 contacts."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [SAMPLE_CONTACTS[0]]  # Only one contact

    response = client.post(
        "/api/life-words/question-sessions",
        json={},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 400
    assert "At least 2 contacts required" in response.json()["detail"]


def test_get_question_session_unauthorized(client):
    """Test that getting a question session requires authentication."""
    response = client.get(f"/api/life-words/question-sessions/{SAMPLE_SESSION_ID}")
    assert response.status_code == 401


def test_get_question_session_success(app, client, mock_user_id, mock_db):
    """Test successfully getting a question session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],  # Get session
        [],  # Get responses
        SAMPLE_CONTACTS,  # Get contacts
    ]

    response = client.get(
        f"/api/life-words/question-sessions/{SAMPLE_SESSION_ID}",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "session" in data
    assert "responses" in data
    assert "contacts" in data


def test_get_question_session_not_found(app, client, mock_user_id, mock_db):
    """Test getting a non-existent question session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.get(
        "/api/life-words/question-sessions/nonexistent",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_save_question_response_unauthorized(client):
    """Test that saving a response requires authentication."""
    response = client.post(
        f"/api/life-words/question-sessions/{SAMPLE_SESSION_ID}/responses",
        json={
            "contact_id": "contact-1",
            "question_type": 1,
            "question_text": "What is John's relationship to you?",
            "expected_answer": "son",
            "user_answer": "son",
            "is_correct": True,
            "is_partial": False,
            "response_time": 2500,
            "clarity_score": 0.9,
            "correctness_score": 1.0,
        }
    )
    assert response.status_code == 401


def test_save_question_response_success(app, client, mock_user_id, mock_db):
    """Test successfully saving a question response."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [SAMPLE_SESSION]
    mock_db.insert.return_value = [SAMPLE_RESPONSE]

    response = client.post(
        f"/api/life-words/question-sessions/{SAMPLE_SESSION_ID}/responses",
        json={
            "contact_id": "contact-1",
            "question_type": 1,
            "question_text": "What is John Smith's relationship to you?",
            "expected_answer": "son",
            "user_answer": "son",
            "is_correct": True,
            "is_partial": False,
            "response_time": 2500,
            "clarity_score": 0.9,
            "correctness_score": 1.0,
        },
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"]["is_correct"] == True


def test_save_question_response_session_not_found(app, client, mock_user_id, mock_db):
    """Test saving response for non-existent session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.post(
        "/api/life-words/question-sessions/nonexistent/responses",
        json={
            "contact_id": "contact-1",
            "question_type": 1,
            "question_text": "What is John's relationship to you?",
            "expected_answer": "son",
            "user_answer": "son",
            "is_correct": True,
            "is_partial": False,
            "response_time": 2500,
            "clarity_score": 0.9,
            "correctness_score": 1.0,
        },
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_complete_question_session_unauthorized(client):
    """Test that completing a question session requires authentication."""
    response = client.put(f"/api/life-words/question-sessions/{SAMPLE_SESSION_ID}/complete")
    assert response.status_code == 401


def test_complete_question_session_success(app, client, mock_user_id, mock_db):
    """Test successfully completing a question session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],  # Get session
        [
            {**SAMPLE_RESPONSE, "question_type": 1},
            {**SAMPLE_RESPONSE, "question_type": 2, "is_correct": False, "correctness_score": 0.0},
            {**SAMPLE_RESPONSE, "question_type": 3},
            {**SAMPLE_RESPONSE, "question_type": 4},
            {**SAMPLE_RESPONSE, "question_type": 5, "is_partial": True, "correctness_score": 0.8},
        ],  # Get responses
    ]
    mock_db.update.return_value = {**SAMPLE_SESSION, "is_completed": True}

    response = client.put(
        f"/api/life-words/question-sessions/{SAMPLE_SESSION_ID}/complete",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "statistics" in data
    assert data["statistics"]["total_questions"] == 5


def test_complete_question_session_not_found(app, client, mock_user_id, mock_db):
    """Test completing non-existent session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.put(
        "/api/life-words/question-sessions/nonexistent/complete",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_complete_question_session_no_responses(app, client, mock_user_id, mock_db):
    """Test completing session with no responses."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],  # Get session
        [],  # No responses
    ]

    response = client.put(
        f"/api/life-words/question-sessions/{SAMPLE_SESSION_ID}/complete",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200


def test_generate_questions_produces_5_questions(app, client, mock_user_id, mock_db):
    """Test that 5 questions are generated for a session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = SAMPLE_CONTACTS
    mock_db.insert.return_value = [SAMPLE_SESSION]

    response = client.post(
        "/api/life-words/question-sessions",
        json={},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    questions = data["questions"]

    # Should have 5 questions
    assert len(questions) == 5

    # Check question types (1-5)
    question_types = [q["question_type"] for q in questions]
    assert 1 in question_types  # Relationship
    assert 2 in question_types  # Association
    assert 3 in question_types  # Interests
    assert 4 in question_types  # Personality
    assert 5 in question_types  # Name from description


def test_evaluate_answer_function():
    """Test the evaluate_answer utility function."""
    from app.services.life_words_question_service import evaluate_answer

    # Exact match
    is_correct, is_partial, score = evaluate_answer("son", "son", ["son"])
    assert is_correct == True
    assert is_partial == False
    assert score == 1.0

    # Acceptable alternative
    is_correct, is_partial, score = evaluate_answer("my son", "son", ["my son"])
    assert is_correct == True

    # Partial match - contains
    is_correct, is_partial, score = evaluate_answer("my son john", "son", [])
    assert is_correct == True
    assert is_partial == True

    # No match
    is_correct, is_partial, score = evaluate_answer("daughter", "son", [])
    assert is_correct == False
    assert score == 0.0

    # Empty answer
    is_correct, is_partial, score = evaluate_answer("", "son", [])
    assert is_correct == False
    assert score == 0.0
