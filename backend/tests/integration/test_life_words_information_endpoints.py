"""Integration tests for Life Words Information Practice endpoints."""
import pytest
from datetime import datetime


# ============== Helper Function Tests ==============

def test_format_phone_for_tts_10_digits():
    """Test formatting 10-digit phone number for TTS."""
    from app.services.life_words_information_service import format_phone_for_tts

    result = format_phone_for_tts("5551234567")
    assert result == "5 5 5, 1 2 3, 4 5 6 7"


def test_format_phone_for_tts_7_digits():
    """Test formatting 7-digit phone number for TTS."""
    from app.services.life_words_information_service import format_phone_for_tts

    result = format_phone_for_tts("1234567")
    assert result == "1 2 3, 4 5 6 7"


def test_format_phone_for_tts_other():
    """Test formatting other length phone number for TTS."""
    from app.services.life_words_information_service import format_phone_for_tts

    result = format_phone_for_tts("12345")
    assert result == "1 2 3 4 5"


def test_format_phone_for_tts_with_dashes():
    """Test formatting phone number with dashes for TTS."""
    from app.services.life_words_information_service import format_phone_for_tts

    result = format_phone_for_tts("555-123-4567")
    assert result == "5 5 5, 1 2 3, 4 5 6 7"


def test_format_zip_for_tts():
    """Test formatting zip code for TTS."""
    from app.services.life_words_information_service import format_zip_for_tts

    result = format_zip_for_tts("90210")
    assert result == "9 0 2 1 0"


def test_format_state_for_tts_abbreviation():
    """Test expanding state abbreviation for TTS."""
    from app.services.life_words_information_service import format_state_for_tts

    result = format_state_for_tts("CA")
    assert result == "California"


def test_format_state_for_tts_full_name():
    """Test state full name passes through."""
    from app.services.life_words_information_service import format_state_for_tts

    result = format_state_for_tts("California")
    assert result == "California"


def test_format_state_for_tts_lowercase():
    """Test lowercase state abbreviation works."""
    from app.services.life_words_information_service import format_state_for_tts

    result = format_state_for_tts("ny")
    assert result == "New York"


def test_format_date_for_display_string():
    """Test formatting date string for display."""
    from app.services.life_words_information_service import format_date_for_display

    result = format_date_for_display("1950-01-15")
    assert result == "January 15"


def test_format_date_for_display_none():
    """Test formatting None date."""
    from app.services.life_words_information_service import format_date_for_display

    result = format_date_for_display(None)
    assert result == ""


def test_format_date_for_display_invalid():
    """Test formatting invalid date string."""
    from app.services.life_words_information_service import format_date_for_display

    result = format_date_for_display("not-a-date")
    assert result == "not-a-date"


def test_generate_hint_first_letter():
    """Test generating first letter hint."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("Boston", "first_letter")
    assert result == "It starts with the letter B"


def test_generate_hint_first_digit():
    """Test generating first digit hint."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("5551234", "first_digit")
    assert result == "The first digit is 5"


def test_generate_hint_first_digit_no_digits():
    """Test generating first digit hint when no digits exist."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("ABC", "first_digit")
    assert result == "It starts with A"


def test_generate_hint_empty_value():
    """Test generating hint for empty value."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("", "first_letter")
    assert result == ""


def test_generate_hint_unknown_type():
    """Test generating hint with unknown type."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("Test", "unknown")
    assert result == "The first character is T"


def test_get_filled_fields_count():
    """Test counting filled profile fields."""
    from app.services.life_words_information_service import get_filled_fields_count

    profile = {
        "phone_number": "5551234567",
        "address_city": "Boston",
        "address_state": "MA",
        "address_zip": "02101",
        "full_name": "John Smith",
        "job": None,
        "favorite_food": "",
    }

    result = get_filled_fields_count(profile)
    assert result == 5


def test_generate_information_items():
    """Test generating information items from profile."""
    from app.services.life_words_information_service import generate_information_items

    profile = {
        "phone_number": "5551234567",
        "address_city": "Boston",
        "address_state": "MA",
        "address_zip": "02101",
        "full_name": "John Smith",
        "date_of_birth": "1950-01-15",
    }

    items = generate_information_items(profile)

    assert len(items) == 5
    for item in items:
        assert item.field_name is not None
        assert item.teach_text is not None
        assert item.question_text is not None
        assert item.expected_answer is not None
        assert item.hint_text is not None


def test_generate_information_items_with_pronunciation():
    """Test generating information items uses pronunciation for full_name."""
    from app.services.life_words_information_service import generate_information_items

    profile = {
        "full_name": "John Smith",
        "full_name_pronunciation": "Jon Smythe",
        "phone_number": "5551234567",
        "address_city": "Boston",
        "address_state": "MA",
        "address_zip": "02101",
    }

    items = generate_information_items(profile)

    # Find the full_name item
    full_name_items = [i for i in items if i.field_name == "full_name"]
    if full_name_items:
        assert "Jon Smythe" in full_name_items[0].teach_text


# ============== Information Status Tests ==============

def test_get_information_status_unauthorized(client):
    """Test getting information status without authentication."""
    response = client.get("/api/life-words/information-status")
    assert response.status_code == 401


def test_get_information_status_success(app, client, mock_user_id, mock_db):
    """Test getting information status successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "id": mock_user_id,
        "phone_number": "5551234567",
        "address_city": "Boston",
        "address_state": "MA",
        "address_zip": "02101",
        "full_name": "John Smith",
        "date_of_birth": "1950-01-15",
    }]

    response = client.get(
        "/api/life-words/information-status",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["can_start_session"] is True
    assert data["filled_fields_count"] == 6
    assert data["min_fields_required"] == 5


def test_get_information_status_not_enough_fields(app, client, mock_user_id, mock_db):
    """Test information status shows can't start with insufficient fields."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "id": mock_user_id,
        "phone_number": "5551234567",
        "address_city": "Boston",
    }]

    response = client.get(
        "/api/life-words/information-status",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["can_start_session"] is False
    assert data["filled_fields_count"] == 2


def test_get_information_status_no_profile(app, client, mock_user_id, mock_db):
    """Test information status with no profile."""
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
        "/api/life-words/information-status",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["can_start_session"] is False
    assert data["filled_fields_count"] == 0


# ============== Information Session Tests ==============

def test_create_information_session_unauthorized(client):
    """Test creating an information session without authentication."""
    response = client.post("/api/life-words/information-sessions", json={})
    assert response.status_code == 401


def test_create_information_session_success(app, client, mock_user_id, mock_db, mocker):
    """Test creating an information session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    mocker.patch("app.services.life_words_information_service.verify_can_practice")

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "id": mock_user_id,
        "phone_number": "5551234567",
        "address_city": "Boston",
        "address_state": "MA",
        "address_zip": "02101",
        "full_name": "John Smith",
        "date_of_birth": "1950-01-15",
    }]

    mock_db.insert.return_value = [{
        "id": "info-session-123",
        "user_id": mock_user_id,
        "is_completed": False,
        "total_items": 5,
        "total_correct": 0,
        "total_hints_used": 0,
        "total_timeouts": 0,
        "average_response_time": 0,
        "created_at": datetime.utcnow().isoformat()
    }]

    response = client.post(
        "/api/life-words/information-sessions",
        json={},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session"]["id"] == "info-session-123"
    assert len(data["items"]) == 5


def test_create_information_session_no_profile(app, client, mock_user_id, mock_db, mocker):
    """Test creating information session with no profile."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    mocker.patch("app.services.life_words_information_service.verify_can_practice")

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.post(
        "/api/life-words/information-sessions",
        json={},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 400
    assert "Profile not found" in response.json()["detail"]


def test_create_information_session_insufficient_fields(app, client, mock_user_id, mock_db, mocker):
    """Test creating information session with insufficient profile fields."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    mocker.patch("app.services.life_words_information_service.verify_can_practice")

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "id": mock_user_id,
        "phone_number": "5551234567",
        "address_city": "Boston",
    }]

    response = client.post(
        "/api/life-words/information-sessions",
        json={},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 400
    assert "At least 5 profile fields required" in response.json()["detail"]


def test_get_information_session_unauthorized(client):
    """Test getting an information session without authentication."""
    response = client.get("/api/life-words/information-sessions/session-123")
    assert response.status_code == 401


def test_get_information_session_success(app, client, mock_user_id, mock_db):
    """Test getting an information session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    def mock_query(table, select=None, filters=None, order=None):
        if table == "life_words_information_sessions":
            return [{
                "id": "session-123",
                "user_id": mock_user_id,
                "is_completed": False
            }]
        elif table == "life_words_information_responses":
            return []
        return []

    mock_db.query.side_effect = mock_query

    response = client.get(
        "/api/life-words/information-sessions/session-123",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session"]["id"] == "session-123"
    assert data["responses"] == []


def test_get_information_session_not_found(app, client, mock_user_id, mock_db):
    """Test getting a non-existent information session."""
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
        "/api/life-words/information-sessions/nonexistent",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


# ============== Information Response Tests ==============

def test_save_information_response_unauthorized(client):
    """Test saving an information response without authentication."""
    response = client.post("/api/life-words/information-sessions/session-123/responses", json={
        "field_name": "phone_number",
        "field_label": "phone number",
        "teach_text": "Your phone number is 555-1234",
        "question_text": "What is your phone number?",
        "expected_answer": "555-1234",
        "hint_text": "The first digit is 5",
        "user_answer": "555-1234",
        "is_correct": True,
        "used_hint": False,
        "timed_out": False,
        "response_time": 5000
    })
    assert response.status_code == 401


def test_save_information_response_success(app, client, mock_user_id, mock_db):
    """Test saving an information response successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "id": "session-123",
        "user_id": mock_user_id
    }]

    mock_db.insert.return_value = [{
        "id": "response-123",
        "session_id": "session-123",
        "user_id": mock_user_id,
        "field_name": "phone_number",
        "field_label": "phone number",
        "teach_text": "Your phone number is 555-1234",
        "question_text": "What is your phone number?",
        "expected_answer": "555-1234",
        "hint_text": "The first digit is 5",
        "user_answer": "555-1234",
        "is_correct": True,
        "used_hint": False,
        "timed_out": False,
        "response_time": 5000,
        "created_at": datetime.utcnow().isoformat()
    }]

    response = client.post(
        "/api/life-words/information-sessions/session-123/responses",
        json={
            "field_name": "phone_number",
            "field_label": "phone number",
            "teach_text": "Your phone number is 555-1234",
            "question_text": "What is your phone number?",
            "expected_answer": "555-1234",
            "hint_text": "The first digit is 5",
            "user_answer": "555-1234",
            "is_correct": True,
            "used_hint": False,
            "timed_out": False,
            "response_time": 5000
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["response"]["id"] == "response-123"
    assert data["response"]["is_correct"] is True


def test_save_information_response_session_not_found(app, client, mock_user_id, mock_db):
    """Test saving information response for non-existent session."""
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
        "/api/life-words/information-sessions/nonexistent/responses",
        json={
            "field_name": "phone_number",
            "field_label": "phone number",
            "teach_text": "Your phone number is 555-1234",
            "question_text": "What is your phone number?",
            "expected_answer": "555-1234",
            "hint_text": "The first digit is 5",
            "user_answer": "555-1234",
            "is_correct": True,
            "used_hint": False,
            "timed_out": False,
            "response_time": 5000
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


# ============== Complete Information Session Tests ==============

def test_complete_information_session_unauthorized(client):
    """Test completing an information session without authentication."""
    response = client.put("/api/life-words/information-sessions/session-123/complete")
    assert response.status_code == 401


def test_complete_information_session_success(app, client, mock_user_id, mock_db):
    """Test completing an information session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    def mock_query(table, select=None, filters=None, order=None):
        if table == "life_words_information_sessions":
            return [{"id": "session-123", "user_id": mock_user_id}]
        elif table == "life_words_information_responses":
            return [
                {"id": "r1", "field_name": "phone_number", "is_correct": True, "used_hint": False, "timed_out": False, "response_time": 3500},
                {"id": "r2", "field_name": "address_city", "is_correct": False, "used_hint": True, "timed_out": False, "response_time": 8000},
                {"id": "r3", "field_name": "full_name", "is_correct": True, "used_hint": False, "timed_out": False, "response_time": 2500},
                {"id": "r4", "field_name": "address_state", "is_correct": False, "used_hint": False, "timed_out": True, "response_time": 30000},
                {"id": "r5", "field_name": "address_zip", "is_correct": True, "used_hint": False, "timed_out": False, "response_time": 4000},
            ]
        return []

    mock_db.query.side_effect = mock_query
    mock_db.update.return_value = [{
        "id": "session-123",
        "is_completed": True,
        "total_correct": 3,
        "total_hints_used": 1,
        "total_timeouts": 1,
        "average_response_time": 9600
    }]

    response = client.put(
        "/api/life-words/information-sessions/session-123/complete",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["statistics"]["total_items"] == 5
    assert data["statistics"]["total_correct"] == 3
    assert data["statistics"]["total_hints_used"] == 1
    assert data["statistics"]["total_timeouts"] == 1
    assert data["statistics"]["accuracy_percentage"] == 60.0


def test_complete_information_session_not_found(app, client, mock_user_id, mock_db):
    """Test completing a non-existent information session."""
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
        "/api/life-words/information-sessions/nonexistent/complete",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


def test_complete_information_session_no_responses(app, client, mock_user_id, mock_db):
    """Test completing an information session with no responses."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    def mock_query(table, select=None, filters=None, order=None):
        if table == "life_words_information_sessions":
            return [{"id": "session-123", "user_id": mock_user_id}]
        elif table == "life_words_information_responses":
            return []
        return []

    mock_db.query.side_effect = mock_query

    response = client.put(
        "/api/life-words/information-sessions/session-123/complete",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
