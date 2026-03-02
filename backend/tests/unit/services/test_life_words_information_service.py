"""Unit tests for life words information practice service."""
import pytest
from fastapi import HTTPException


@pytest.fixture(autouse=True)
def _bypass_subscription_check(mocker):
    """Bypass verify_can_practice for all tests in this module."""
    mocker.patch("app.services.life_words_information_service.verify_can_practice")


# ---- format_phone_for_tts ----


def test_format_phone_for_tts_10_digits():
    """Test formatting a 10-digit phone number for TTS."""
    from app.services.life_words_information_service import format_phone_for_tts

    result = format_phone_for_tts("5551234567")
    assert result == "5 5 5, 1 2 3, 4 5 6 7"


def test_format_phone_for_tts_10_digits_with_formatting():
    """Test formatting a 10-digit phone with dashes/parens for TTS."""
    from app.services.life_words_information_service import format_phone_for_tts

    result = format_phone_for_tts("(555) 123-4567")
    assert result == "5 5 5, 1 2 3, 4 5 6 7"


def test_format_phone_for_tts_7_digits():
    """Test formatting a 7-digit phone number for TTS."""
    from app.services.life_words_information_service import format_phone_for_tts

    result = format_phone_for_tts("5551234")
    assert result == "5 5 5, 1 2 3 4"


def test_format_phone_for_tts_other_length():
    """Test formatting an unusual-length phone number for TTS."""
    from app.services.life_words_information_service import format_phone_for_tts

    result = format_phone_for_tts("12345")
    assert result == "1 2 3 4 5"


# ---- format_zip_for_tts ----


def test_format_zip_for_tts():
    """Test formatting a zip code for TTS reads digits individually."""
    from app.services.life_words_information_service import format_zip_for_tts

    result = format_zip_for_tts("90210")
    assert result == "9 0 2 1 0"


def test_format_zip_for_tts_with_dash():
    """Test formatting a zip+4 code strips non-digit chars."""
    from app.services.life_words_information_service import format_zip_for_tts

    result = format_zip_for_tts("90210-1234")
    assert result == "9 0 2 1 0 1 2 3 4"


# ---- format_state_for_tts ----


def test_format_state_for_tts_abbreviation():
    """Test expanding a state abbreviation to full name."""
    from app.services.life_words_information_service import format_state_for_tts

    result = format_state_for_tts("CA")
    assert result == "California"


def test_format_state_for_tts_lowercase_abbreviation():
    """Test expanding a lowercase state abbreviation."""
    from app.services.life_words_information_service import format_state_for_tts

    result = format_state_for_tts("ny")
    assert result == "New York"


def test_format_state_for_tts_full_name():
    """Test that a full state name is returned as-is when not an abbreviation."""
    from app.services.life_words_information_service import format_state_for_tts

    result = format_state_for_tts("California")
    assert result == "California"


# ---- format_date_for_display ----


def test_format_date_for_display_iso_string():
    """Test formatting an ISO date string for display."""
    from app.services.life_words_information_service import format_date_for_display

    result = format_date_for_display("1990-05-15")
    assert result == "May 15"


def test_format_date_for_display_none():
    """Test formatting None returns empty string."""
    from app.services.life_words_information_service import format_date_for_display

    result = format_date_for_display(None)
    assert result == ""


def test_format_date_for_display_invalid_string():
    """Test formatting an unparseable string returns it unchanged."""
    from app.services.life_words_information_service import format_date_for_display

    result = format_date_for_display("not-a-date")
    assert result == "not-a-date"


def test_format_date_for_display_datetime_object():
    """Test formatting a datetime object for display."""
    from datetime import datetime
    from app.services.life_words_information_service import format_date_for_display

    dt = datetime(1990, 5, 15, 12, 0, 0)
    result = format_date_for_display(dt)
    assert result == "May 15"


# ---- generate_hint ----


def test_generate_hint_first_letter():
    """Test generating a first letter hint."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("California", "first_letter")
    assert result == "It starts with the letter C"


def test_generate_hint_first_digit():
    """Test generating a first digit hint."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("5551234567", "first_digit")
    assert result == "The first digit is 5"


def test_generate_hint_first_digit_no_digits():
    """Test first_digit hint when value has no digits falls back."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("abc", "first_digit")
    assert result == "It starts with a"


def test_generate_hint_empty_value():
    """Test generating a hint with empty value returns empty string."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("", "first_letter")
    assert result == ""


def test_generate_hint_unknown_type():
    """Test generating a hint with unknown hint type uses first character."""
    from app.services.life_words_information_service import generate_hint

    result = generate_hint("Hello", "unknown_type")
    assert result == "The first character is H"


# ---- get_filled_fields_count ----


def test_get_filled_fields_count_multiple_fields():
    """Test counting multiple filled profile fields."""
    from app.services.life_words_information_service import get_filled_fields_count

    profile = {
        "phone_number": "5551234567",
        "address_city": "Los Angeles",
        "address_state": "CA",
        "full_name": "John Doe",
        "job": "Engineer",
        "address_zip": None,
        "date_of_birth": None,
    }
    result = get_filled_fields_count(profile)
    assert result == 5


def test_get_filled_fields_count_empty_profile():
    """Test counting filled fields in an empty profile."""
    from app.services.life_words_information_service import get_filled_fields_count

    profile = {}
    result = get_filled_fields_count(profile)
    assert result == 0


def test_get_filled_fields_count_whitespace_only():
    """Test that whitespace-only fields are not counted."""
    from app.services.life_words_information_service import get_filled_fields_count

    profile = {
        "phone_number": "   ",
        "address_city": "Springfield",
    }
    result = get_filled_fields_count(profile)
    assert result == 1


# ---- generate_information_items ----


def test_generate_information_items_with_profile_data():
    """Test generating information items from a profile with data."""
    from app.services.life_words_information_service import generate_information_items

    profile = {
        "phone_number": "5551234567",
        "address_city": "Los Angeles",
        "address_state": "CA",
        "address_zip": "90210",
        "date_of_birth": "1990-05-15",
        "full_name": "John Doe",
        "job": "Engineer",
    }
    items = generate_information_items(profile)

    # Should return at most 5 items
    assert len(items) <= 5
    assert len(items) >= 1

    # Each item should have required fields
    for item in items:
        assert item.field_name in profile
        assert item.field_label != ""
        assert item.teach_text != ""
        assert item.question_text != ""
        assert item.expected_answer != ""
        assert item.hint_text != ""


def test_generate_information_items_with_pronunciation():
    """Test that full_name uses pronunciation when available."""
    from app.services.life_words_information_service import generate_information_items
    import random

    # Seed random so full_name is selected consistently
    random.seed(42)
    profile = {
        "full_name": "John Doe",
        "full_name_pronunciation": "Jon Doh",
        "phone_number": "5551234567",
        "address_city": "LA",
        "address_state": "CA",
        "address_zip": "90210",
        "date_of_birth": "1990-05-15",
    }
    items = generate_information_items(profile)

    # Find the full_name item
    full_name_items = [i for i in items if i.field_name == "full_name"]
    if full_name_items:
        item = full_name_items[0]
        assert "Jon Doh" in item.teach_text


def test_generate_information_items_phone_formatted():
    """Test that phone_number field uses TTS formatting in teach_text."""
    from app.services.life_words_information_service import generate_information_items

    # Profile with only phone_number filled (plus enough others to pass)
    profile = {
        "phone_number": "5551234567",
        "address_city": "LA",
        "address_state": "CA",
        "address_zip": "90210",
        "full_name": "John",
        "job": "Dev",
    }
    items = generate_information_items(profile)

    phone_items = [i for i in items if i.field_name == "phone_number"]
    if phone_items:
        item = phone_items[0]
        # The teach text should contain the TTS-formatted phone
        assert "5 5 5" in item.teach_text


def test_generate_information_items_caps_at_five():
    """Test that at most 5 items are generated even with more filled fields."""
    from app.services.life_words_information_service import generate_information_items

    profile = {
        "phone_number": "5551234567",
        "address_city": "Los Angeles",
        "address_state": "CA",
        "address_zip": "90210",
        "date_of_birth": "1990-05-15",
        "full_name": "John Doe",
        "job": "Engineer",
        "marital_status": "Single",
        "number_of_children": "2",
        "favorite_food": "Pizza",
        "favorite_music": "Jazz",
        "hair_color": "Brown",
        "eye_color": "Blue",
    }
    items = generate_information_items(profile)
    assert len(items) == 5


def test_generate_information_items_empty_profile():
    """Test that an empty profile generates no items."""
    from app.services.life_words_information_service import generate_information_items

    profile = {}
    items = generate_information_items(profile)
    assert len(items) == 0


# ---- get_information_status ----


@pytest.mark.asyncio
async def test_get_information_status_enough_fields(mock_db):
    """Test status when user has enough profile fields."""
    from app.services.life_words_information_service import LifeWordsInformationService

    mock_db.query.return_value = [{
        "phone_number": "5551234567",
        "address_city": "Los Angeles",
        "address_state": "CA",
        "address_zip": "90210",
        "full_name": "John Doe",
    }]

    service = LifeWordsInformationService(mock_db)
    result = await service.get_information_status("user-123")

    assert result["can_start_session"] is True
    assert result["filled_fields_count"] == 5
    assert result["min_fields_required"] == 5


@pytest.mark.asyncio
async def test_get_information_status_not_enough_fields(mock_db):
    """Test status when user has insufficient profile fields."""
    from app.services.life_words_information_service import LifeWordsInformationService

    mock_db.query.return_value = [{
        "phone_number": "5551234567",
        "address_city": "Los Angeles",
    }]

    service = LifeWordsInformationService(mock_db)
    result = await service.get_information_status("user-123")

    assert result["can_start_session"] is False
    assert result["filled_fields_count"] == 2


@pytest.mark.asyncio
async def test_get_information_status_no_profile(mock_db):
    """Test status when user has no profile."""
    from app.services.life_words_information_service import LifeWordsInformationService

    mock_db.query.return_value = []

    service = LifeWordsInformationService(mock_db)
    result = await service.get_information_status("user-123")

    assert result["can_start_session"] is False
    assert result["filled_fields_count"] == 0


# ---- create_session ----


@pytest.mark.asyncio
async def test_create_session_success(mock_db):
    """Test creating a session successfully with enough profile data."""
    from app.services.life_words_information_service import LifeWordsInformationService

    mock_db.query.return_value = [{
        "phone_number": "5551234567",
        "address_city": "Los Angeles",
        "address_state": "CA",
        "address_zip": "90210",
        "full_name": "John Doe",
        "job": "Engineer",
    }]
    mock_db.insert.return_value = [{
        "id": "session-001",
        "user_id": "user-123",
        "is_completed": False,
        "total_items": 5,
        "total_correct": 0,
        "total_hints_used": 0,
        "total_timeouts": 0,
        "average_response_time": 0,
    }]

    service = LifeWordsInformationService(mock_db)
    result = await service.create_session("user-123")

    assert "session" in result
    assert "items" in result
    assert result["session"]["id"] == "session-001"
    assert len(result["items"]) <= 5
    assert len(result["items"]) >= 1
    mock_db.insert.assert_called_once()


@pytest.mark.asyncio
async def test_create_session_no_profile(mock_db):
    """Test creating a session with no profile raises 404."""
    from app.services.life_words_information_service import LifeWordsInformationService

    mock_db.query.return_value = []

    service = LifeWordsInformationService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_session("user-123")

    assert exc_info.value.status_code == 404
    assert "Profile not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_session_insufficient_fields(mock_db):
    """Test creating a session with too few profile fields raises 400."""
    from app.services.life_words_information_service import LifeWordsInformationService

    mock_db.query.return_value = [{
        "phone_number": "5551234567",
        "address_city": "Los Angeles",
    }]

    service = LifeWordsInformationService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_session("user-123")

    assert exc_info.value.status_code == 400
    assert "profile fields required" in exc_info.value.detail


# ---- complete_session ----


@pytest.mark.asyncio
async def test_complete_session_success(mock_db):
    """Test completing a session calculates statistics correctly."""
    from app.services.life_words_information_service import LifeWordsInformationService

    session_data = {
        "id": "session-001",
        "user_id": "user-123",
        "is_completed": False,
    }
    responses_data = [
        {
            "field_name": "phone_number",
            "is_correct": True,
            "used_hint": False,
            "timed_out": False,
            "response_time": 3000,
        },
        {
            "field_name": "address_city",
            "is_correct": False,
            "used_hint": True,
            "timed_out": False,
            "response_time": 5000,
        },
        {
            "field_name": "full_name",
            "is_correct": True,
            "used_hint": False,
            "timed_out": True,
            "response_time": 10000,
        },
    ]

    mock_db.query.side_effect = [
        [session_data],     # session query
        responses_data,     # responses query
    ]
    updated_session = {**session_data, "is_completed": True}
    mock_db.update.return_value = updated_session

    service = LifeWordsInformationService(mock_db)
    result = await service.complete_session("session-001", "user-123")

    assert "session" in result
    assert "statistics" in result

    stats = result["statistics"]
    assert stats["total_items"] == 3
    assert stats["total_correct"] == 2
    assert stats["total_hints_used"] == 1
    assert stats["total_timeouts"] == 1
    assert stats["accuracy_percentage"] == 66.7
    assert stats["average_response_time_ms"] == 6000.0

    # Check by_field breakdown
    assert "phone_number" in stats["by_field"]
    assert stats["by_field"]["phone_number"]["is_correct"] is True
    assert stats["by_field"]["address_city"]["used_hint"] is True

    # Verify db update was called correctly
    mock_db.update.assert_called_once()
    update_args = mock_db.update.call_args.args
    assert update_args[0] == "life_words_information_sessions"
    update_data = update_args[2]
    assert update_data["is_completed"] is True
    assert update_data["total_correct"] == 2


@pytest.mark.asyncio
async def test_complete_session_no_responses(mock_db):
    """Test completing a session with no responses still succeeds with zero stats."""
    from app.services.life_words_information_service import LifeWordsInformationService

    mock_db.query.side_effect = [
        [{"id": "session-001", "user_id": "user-123"}],  # session found
        [],  # no responses
    ]
    mock_db.update.return_value = {"id": "session-001", "is_completed": True}

    service = LifeWordsInformationService(mock_db)
    result = await service.complete_session("session-001", "user-123")
    assert "session" in result


@pytest.mark.asyncio
async def test_complete_session_not_found(mock_db):
    """Test completing a non-existent session raises 404."""
    from app.services.life_words_information_service import LifeWordsInformationService

    mock_db.query.return_value = []

    service = LifeWordsInformationService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.complete_session("nonexistent", "user-123")

    assert exc_info.value.status_code == 404
    assert "Session not found" in exc_info.value.detail
