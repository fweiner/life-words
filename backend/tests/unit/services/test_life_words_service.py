"""Unit tests for life words service."""
import pytest
from datetime import datetime, timezone
from fastapi import HTTPException


@pytest.fixture(autouse=True)
def _bypass_subscription_check(mocker):
    """Bypass verify_can_practice for all tests in this module."""
    mocker.patch("app.services.life_words_service.verify_can_practice")


SAMPLE_CONTACT = {
    "id": "contact-123",
    "user_id": "user-123",
    "name": "John",
    "nickname": None,
    "pronunciation": None,
    "relationship": "friend",
    "photo_url": "https://example.com/photo.jpg",
    "category": None,
    "first_letter": "J",
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

SAMPLE_ITEM = {
    "id": "item-456",
    "user_id": "user-123",
    "name": "Coffee Mug",
    "photo_url": "https://example.com/mug.jpg",
    "purpose": "Drinking coffee",
    "features": "Blue ceramic",
    "category": "kitchen",
    "size": "medium",
    "shape": "cylindrical",
    "color": "blue",
    "weight": "light",
    "location": "kitchen counter",
    "associated_with": "morning routine",
    "is_active": True,
    "is_complete": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

SAMPLE_SESSION = {
    "id": "session-789",
    "user_id": "user-123",
    "contact_ids": ["contact-123", "item-456"],
    "is_completed": False,
    "started_at": datetime.now(timezone.utc).isoformat(),
    "completed_at": None,
    "total_correct": 0,
    "total_incorrect": 0,
    "average_cues_used": 0,
    "average_response_time": 0,
    "statistics": None,
}

SAMPLE_RESPONSE = {
    "id": "response-001",
    "session_id": "session-789",
    "contact_id": "contact-123",
    "user_id": "user-123",
    "is_correct": True,
    "cues_used": 1,
    "response_time": 3.5,
    "user_answer": "John",
    "correct_answer": "John",
    "speech_confidence": 0.95,
    "completed_at": datetime.now(timezone.utc).isoformat(),
}


# ---- get_status ----


@pytest.mark.asyncio
async def test_get_status_with_contacts_and_items(mock_db):
    """Test get_status counts both contacts and items."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.side_effect = [
        [{"id": "c1"}, {"id": "c2"}],  # contacts
        [{"id": "i1"}],                 # items
    ]

    service = LifeWordsService(mock_db)
    result = await service.get_status("user-123")

    assert result["contact_count"] == 2
    assert result["item_count"] == 1
    assert result["total_count"] == 3
    assert result["can_start_session"] is True
    assert result["min_contacts_required"] == 2


@pytest.mark.asyncio
async def test_get_status_empty(mock_db):
    """Test get_status when user has no contacts or items."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.side_effect = [
        [],    # contacts
        None,  # items (None also handled)
    ]

    service = LifeWordsService(mock_db)
    result = await service.get_status("user-123")

    assert result["contact_count"] == 0
    assert result["item_count"] == 0
    assert result["total_count"] == 0
    assert result["can_start_session"] is False


@pytest.mark.asyncio
async def test_get_status_below_minimum(mock_db):
    """Test get_status when count is below minimum required."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.side_effect = [
        [{"id": "c1"}],  # 1 contact
        [],               # 0 items
    ]

    service = LifeWordsService(mock_db)
    result = await service.get_status("user-123")

    assert result["contact_count"] == 1
    assert result["item_count"] == 0
    assert result["total_count"] == 1
    assert result["can_start_session"] is False


# ---- create_contact ----


@pytest.mark.asyncio
async def test_create_contact(mock_db):
    """Test creating a personal contact."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import PersonalContactCreate

    mock_db.insert.return_value = [SAMPLE_CONTACT]

    service = LifeWordsService(mock_db)
    result = await service.create_contact(
        "user-123",
        PersonalContactCreate(
            name="John",
            relationship="friend",
            photo_url="https://example.com/photo.jpg",
        )
    )

    assert result["name"] == "John"
    assert result["relationship"] == "friend"
    mock_db.insert.assert_called_once()
    call_data = mock_db.insert.call_args.args[1]
    assert call_data["user_id"] == "user-123"
    assert call_data["name"] == "John"


@pytest.mark.asyncio
async def test_create_contact_empty_strings_converted(mock_db):
    """Test that empty optional strings are converted to None."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import PersonalContactCreate

    mock_db.insert.return_value = [SAMPLE_CONTACT]

    service = LifeWordsService(mock_db)
    await service.create_contact(
        "user-123",
        PersonalContactCreate(
            name="John",
            relationship="friend",
            photo_url="https://example.com/photo.jpg",
            nickname="",
            pronunciation="",
            description="",
        )
    )

    call_data = mock_db.insert.call_args.args[1]
    assert call_data["nickname"] is None
    assert call_data["pronunciation"] is None
    assert call_data["description"] is None


# ---- quick_add_contact ----


@pytest.mark.asyncio
async def test_quick_add_contact(mock_db):
    """Test quick adding a contact with just a photo."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import QuickAddContactCreate

    draft = {**SAMPLE_CONTACT, "name": "", "is_complete": False}
    mock_db.insert.return_value = [draft]

    service = LifeWordsService(mock_db)
    result = await service.quick_add_contact(
        "user-123",
        QuickAddContactCreate(photo_url="https://example.com/photo.jpg", category="family")
    )

    assert result["name"] == ""
    call_data = mock_db.insert.call_args.args[1]
    assert call_data["name"] == ""
    assert call_data["relationship"] == ""
    assert call_data["photo_url"] == "https://example.com/photo.jpg"
    assert call_data["category"] == "family"


# ---- list_contacts ----


@pytest.mark.asyncio
async def test_list_contacts_active_only(mock_db):
    """Test listing contacts filters to active by default."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = [SAMPLE_CONTACT, {**SAMPLE_CONTACT, "id": "contact-456"}]

    service = LifeWordsService(mock_db)
    result = await service.list_contacts("user-123")

    assert len(result) == 2
    call_kwargs = mock_db.query.call_args.kwargs
    assert call_kwargs["filters"]["is_active"] is True


@pytest.mark.asyncio
async def test_list_contacts_include_inactive(mock_db):
    """Test listing contacts including inactive ones."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = [SAMPLE_CONTACT]

    service = LifeWordsService(mock_db)
    await service.list_contacts("user-123", include_inactive=True)

    call_kwargs = mock_db.query.call_args.kwargs
    assert "is_active" not in call_kwargs["filters"]


@pytest.mark.asyncio
async def test_list_contacts_empty(mock_db):
    """Test listing contacts when none exist returns empty list."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = None

    service = LifeWordsService(mock_db)
    result = await service.list_contacts("user-123")

    assert result == []


# ---- get_contact ----


@pytest.mark.asyncio
async def test_get_contact(mock_db):
    """Test getting a specific contact."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = [SAMPLE_CONTACT]

    service = LifeWordsService(mock_db)
    result = await service.get_contact("contact-123", "user-123")

    assert result["id"] == "contact-123"
    assert result["name"] == "John"


@pytest.mark.asyncio
async def test_get_contact_not_found(mock_db):
    """Test getting a non-existent contact raises 404."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = []

    service = LifeWordsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_contact("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


# ---- update_contact ----


@pytest.mark.asyncio
async def test_update_contact(mock_db):
    """Test updating a contact."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import PersonalContactUpdate

    mock_db.query.return_value = [{"id": "contact-123"}]
    updated = {**SAMPLE_CONTACT, "name": "Jane"}
    mock_db.update.return_value = [updated]

    service = LifeWordsService(mock_db)
    result = await service.update_contact(
        "contact-123", "user-123",
        PersonalContactUpdate(name="Jane")
    )

    assert result["name"] == "Jane"


@pytest.mark.asyncio
async def test_update_contact_not_found(mock_db):
    """Test updating a non-existent contact raises 404."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import PersonalContactUpdate

    mock_db.query.return_value = []

    service = LifeWordsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_contact(
            "nonexistent", "user-123",
            PersonalContactUpdate(name="Jane")
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_contact_no_fields(mock_db):
    """Test updating a contact with no fields raises 400."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import PersonalContactUpdate

    mock_db.query.return_value = [{"id": "contact-123"}]

    service = LifeWordsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_contact(
            "contact-123", "user-123",
            PersonalContactUpdate()
        )

    assert exc_info.value.status_code == 400


# ---- delete_contact ----


@pytest.mark.asyncio
async def test_delete_contact(mock_db):
    """Test soft deleting a contact."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = [{"id": "contact-123"}]

    service = LifeWordsService(mock_db)
    result = await service.delete_contact("contact-123", "user-123")

    assert result["success"] is True
    mock_db.update.assert_called_once_with(
        "personal_contacts",
        {"id": "contact-123"},
        {"is_active": False}
    )


@pytest.mark.asyncio
async def test_delete_contact_not_found(mock_db):
    """Test deleting a non-existent contact raises 404."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = []

    service = LifeWordsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_contact("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


# ---- create_session ----


@pytest.mark.asyncio
async def test_create_session_with_contacts_and_items(mock_db):
    """Test creating a session with both contacts and items."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsSessionCreate

    mock_db.query.side_effect = [
        [SAMPLE_CONTACT],   # contacts query (with contact_ids filter)
        [SAMPLE_ITEM],      # items query
    ]
    mock_db.insert.return_value = [SAMPLE_SESSION]

    service = LifeWordsService(mock_db)
    result = await service.create_session(
        "user-123",
        LifeWordsSessionCreate(contact_ids=["contact-123"])
    )

    assert "session" in result
    assert "contacts" in result
    assert len(result["contacts"]) == 2  # 1 contact + 1 item converted
    mock_db.insert.assert_called_once()


@pytest.mark.asyncio
async def test_create_session_all_contacts(mock_db):
    """Test creating a session using all active contacts (no contact_ids)."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsSessionCreate

    contact2 = {**SAMPLE_CONTACT, "id": "contact-456", "name": "Jane"}
    mock_db.query.side_effect = [
        [SAMPLE_CONTACT, contact2],  # all active contacts
        [],                           # no items
    ]
    mock_db.insert.return_value = [SAMPLE_SESSION]

    service = LifeWordsService(mock_db)
    result = await service.create_session(
        "user-123",
        LifeWordsSessionCreate()
    )

    assert "session" in result
    assert len(result["contacts"]) == 2


@pytest.mark.asyncio
async def test_create_session_not_enough_entries(mock_db):
    """Test creating a session with fewer than minimum entries raises 400."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsSessionCreate

    mock_db.query.side_effect = [
        [SAMPLE_CONTACT],  # only 1 contact
        [],                 # no items
    ]

    service = LifeWordsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_session(
            "user-123",
            LifeWordsSessionCreate()
        )

    assert exc_info.value.status_code == 400
    assert "At least" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_session_category_people(mock_db):
    """Test creating a session with category='people' only fetches contacts."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsSessionCreate

    contact2 = {**SAMPLE_CONTACT, "id": "contact-456", "name": "Jane"}
    mock_db.query.side_effect = [
        [SAMPLE_CONTACT, contact2],  # contacts query
        # no items query — should not be called
    ]
    mock_db.insert.return_value = [SAMPLE_SESSION]

    service = LifeWordsService(mock_db)
    result = await service.create_session(
        "user-123",
        LifeWordsSessionCreate(category="people")
    )

    assert "session" in result
    # Only contacts, no items
    assert len(result["contacts"]) == 2
    for entry in result["contacts"]:
        assert entry["relationship"] != "item"
    # Items table should not have been queried
    assert mock_db.query.call_count == 1


@pytest.mark.asyncio
async def test_create_session_category_items(mock_db):
    """Test creating a session with category='items' only fetches items."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsSessionCreate

    item2 = {**SAMPLE_ITEM, "id": "item-789", "name": "Wallet"}
    mock_db.query.side_effect = [
        [SAMPLE_ITEM, item2],  # items query
        # no contacts query — should not be called
    ]
    mock_db.insert.return_value = [SAMPLE_SESSION]

    service = LifeWordsService(mock_db)
    result = await service.create_session(
        "user-123",
        LifeWordsSessionCreate(category="items")
    )

    assert "session" in result
    # Only items (converted to contact format), no contacts
    assert len(result["contacts"]) == 2
    for entry in result["contacts"]:
        assert entry["relationship"] == "item"
    # Contacts table should not have been queried
    assert mock_db.query.call_count == 1


@pytest.mark.asyncio
async def test_create_session_limits_to_six_entries(mock_db):
    """Test creating a session limits entries to 6."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsSessionCreate

    # Create 10 contacts
    contacts = [
        {**SAMPLE_CONTACT, "id": f"contact-{i}", "name": f"Person {i}"}
        for i in range(10)
    ]
    mock_db.query.side_effect = [
        contacts,  # contacts query
        [],        # items query
    ]
    mock_db.insert.return_value = [SAMPLE_SESSION]

    service = LifeWordsService(mock_db)
    result = await service.create_session(
        "user-123",
        LifeWordsSessionCreate()
    )

    assert len(result["contacts"]) == 6
    # Verify the IDs in the insert call are also limited to 6
    insert_data = mock_db.insert.call_args.args[1]
    assert len(insert_data["contact_ids"]) == 6


@pytest.mark.asyncio
async def test_create_session_shuffles_entries(mock_db, mocker):
    """Test creating a session shuffles entries."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsSessionCreate

    contacts = [
        {**SAMPLE_CONTACT, "id": f"contact-{i}", "name": f"Person {i}"}
        for i in range(3)
    ]
    mock_db.query.side_effect = [
        contacts,  # contacts query
        [],        # items query
    ]
    mock_db.insert.return_value = [SAMPLE_SESSION]

    mock_shuffle = mocker.patch("app.services.life_words_service.random.shuffle")

    service = LifeWordsService(mock_db)
    await service.create_session(
        "user-123",
        LifeWordsSessionCreate()
    )

    mock_shuffle.assert_called_once()


# ---- get_session ----


@pytest.mark.asyncio
async def test_get_session(mock_db):
    """Test getting a session with contacts, items, and responses."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],    # session query
        [SAMPLE_CONTACT],    # contacts query
        [SAMPLE_ITEM],       # items query
        [SAMPLE_RESPONSE],   # responses query
    ]

    service = LifeWordsService(mock_db)
    result = await service.get_session("session-789", "user-123")

    assert result["session"]["id"] == "session-789"
    assert len(result["contacts"]) == 2  # 1 contact + 1 item
    assert len(result["responses"]) == 1


@pytest.mark.asyncio
async def test_get_session_not_found(mock_db):
    """Test getting a non-existent session raises 404."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = []

    service = LifeWordsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_session("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


# ---- save_response ----


@pytest.mark.asyncio
async def test_save_response(mock_db):
    """Test saving a response for a session."""
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsResponseCreate

    mock_db.query.return_value = [SAMPLE_SESSION]
    mock_db.insert.return_value = [SAMPLE_RESPONSE]

    service = LifeWordsService(mock_db)
    result = await service.save_response(
        "session-789", "user-123",
        LifeWordsResponseCreate(
            contact_id="contact-123",
            is_correct=True,
            cues_used=1,
            response_time=3.5,
            user_answer="John",
            correct_answer="John",
            speech_confidence=0.95,
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
    from app.services.life_words_service import LifeWordsService
    from app.models.life_words import LifeWordsResponseCreate

    mock_db.query.return_value = []

    service = LifeWordsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.save_response(
            "nonexistent", "user-123",
            LifeWordsResponseCreate(
                contact_id="contact-123",
                is_correct=True,
                correct_answer="John",
            )
        )

    assert exc_info.value.status_code == 404


# ---- complete_session ----


@pytest.mark.asyncio
async def test_complete_session(mock_db):
    """Test completing a session calculates statistics correctly."""
    from app.services.life_words_service import LifeWordsService

    response2 = {
        **SAMPLE_RESPONSE,
        "id": "response-002",
        "contact_id": "contact-456",
        "is_correct": False,
        "cues_used": 3,
        "response_time": 5.0,
    }

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],                    # session query
        [SAMPLE_RESPONSE, response2],        # responses query
    ]
    updated_session = {**SAMPLE_SESSION, "is_completed": True}
    mock_db.update.return_value = [updated_session]

    service = LifeWordsService(mock_db)
    result = await service.complete_session("session-789", "user-123")

    assert "session" in result
    mock_db.update.assert_called_once()
    update_data = mock_db.update.call_args.args[2]
    assert update_data["is_completed"] is True
    assert update_data["total_correct"] == 1
    assert update_data["total_incorrect"] == 1
    assert update_data["statistics"]["responses_count"] == 2
    assert update_data["statistics"]["accuracy_percentage"] == 50.0


@pytest.mark.asyncio
async def test_complete_session_no_responses(mock_db):
    """Test completing a session with no responses still succeeds with zero stats."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.side_effect = [
        [SAMPLE_SESSION],  # session found
        [],                 # no responses
    ]
    mock_db.update.return_value = {**SAMPLE_SESSION, "is_completed": True}

    service = LifeWordsService(mock_db)
    result = await service.complete_session("session-789", "user-123")
    assert "session" in result


@pytest.mark.asyncio
async def test_complete_session_not_found(mock_db):
    """Test completing a non-existent session raises 404."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = []

    service = LifeWordsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.complete_session("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


# ---- convert_items_to_contacts ----


@pytest.mark.asyncio
async def test_convert_items_to_contacts():
    """Test converting personal items to contact-like format."""
    from app.services.life_words_service import convert_items_to_contacts

    result = convert_items_to_contacts([SAMPLE_ITEM])

    assert len(result) == 1
    converted = result[0]
    assert converted["id"] == "item-456"
    assert converted["name"] == "Coffee Mug"
    assert converted["nickname"] is None
    assert converted["relationship"] == "item"
    assert converted["photo_url"] == "https://example.com/mug.jpg"
    assert converted["first_letter"] == "C"
    assert converted["category"] == "kitchen"
    assert converted["description"] == "Drinking coffee"
    assert converted["association"] == "morning routine"
    assert converted["location_context"] == "kitchen counter"
    assert converted["item_features"] == "Blue ceramic"
    assert converted["item_size"] == "medium"
    assert converted["item_shape"] == "cylindrical"
    assert converted["item_color"] == "blue"
    assert converted["item_weight"] == "light"


@pytest.mark.asyncio
async def test_convert_items_to_contacts_empty():
    """Test converting an empty list of items returns empty list."""
    from app.services.life_words_service import convert_items_to_contacts

    result = convert_items_to_contacts([])

    assert result == []


@pytest.mark.asyncio
async def test_convert_items_to_contacts_missing_optional_fields():
    """Test converting items with missing optional fields."""
    from app.services.life_words_service import convert_items_to_contacts

    minimal_item = {
        "id": "item-min",
        "name": "Keys",
        "photo_url": "https://example.com/keys.jpg",
    }

    result = convert_items_to_contacts([minimal_item])

    assert len(result) == 1
    converted = result[0]
    assert converted["id"] == "item-min"
    assert converted["name"] == "Keys"
    assert converted["first_letter"] == "K"
    assert converted["category"] is None
    assert converted["description"] is None
    assert converted["item_features"] is None


# ---- get_progress ----


@pytest.mark.asyncio
async def test_get_progress_with_data(mock_db):
    """Test get_progress aggregates data from all session types."""
    from app.services.life_words_service import LifeWordsService

    name_sessions = [
        {"id": "ns-1", "completed_at": "2026-02-28T10:00:00Z", "total_correct": 4, "total_incorrect": 1, "average_response_time": 3.5, "average_cues_used": 1.2},
    ]
    question_sessions = [
        {"id": "qs-1", "completed_at": "2026-02-27T10:00:00Z", "total_correct": 3, "total_questions": 5, "average_response_time": 2.5, "average_clarity_score": 0.85},
    ]
    info_sessions = [
        {"id": "is-1", "completed_at": "2026-02-26T10:00:00Z", "total_correct": 4, "total_questions": 5, "average_response_time": 5.0, "hints_used": 1},
    ]
    name_responses = [
        {"is_correct": True, "response_time": 3.0, "speech_confidence": 0.9, "contact_id": "c1"},
        {"is_correct": False, "response_time": 5.0, "speech_confidence": 0.7, "contact_id": "c2"},
    ]
    question_responses = [
        {"is_correct": True, "response_time": 2000, "clarity_score": 0.9},
        {"is_correct": True, "response_time": 3000, "clarity_score": 0.8},
        {"is_correct": False, "response_time": 4000, "clarity_score": 0.6},
    ]
    info_responses = [
        {"is_correct": True, "response_time": 5000, "used_hint": False},
        {"is_correct": True, "response_time": 3000, "used_hint": True},
        {"is_correct": False, "response_time": 8000, "used_hint": False},
    ]

    mock_db.query.side_effect = [
        name_sessions, question_sessions, info_sessions,
        name_responses, question_responses, info_responses,
    ]

    service = LifeWordsService(mock_db)
    result = await service.get_progress("user-123")

    assert "summary" in result
    assert "session_history" in result

    summary = result["summary"]
    assert summary["total_sessions"] == 3

    # Name practice stats
    np = summary["name_practice"]
    assert np["sessions"] == 1
    assert np["correct"] == 1
    assert np["total"] == 2
    assert np["accuracy"] == 50.0

    # Question practice stats
    qp = summary["question_practice"]
    assert qp["sessions"] == 1
    assert qp["correct"] == 2
    assert qp["total"] == 3

    # Information practice stats
    ip = summary["information_practice"]
    assert ip["sessions"] == 1
    assert ip["correct"] == 2
    assert ip["total"] == 3

    # Session history
    assert len(result["session_history"]) == 3
    # Should be sorted by date desc
    assert result["session_history"][0]["type"] == "name"


@pytest.mark.asyncio
async def test_get_progress_empty(mock_db):
    """Test get_progress with no sessions returns zeroed stats."""
    from app.services.life_words_service import LifeWordsService

    mock_db.query.return_value = None

    service = LifeWordsService(mock_db)
    result = await service.get_progress("user-123")

    summary = result["summary"]
    assert summary["total_sessions"] == 0
    assert summary["name_practice"]["sessions"] == 0
    assert summary["name_practice"]["accuracy"] == 0
    assert summary["question_practice"]["sessions"] == 0
    assert summary["information_practice"]["sessions"] == 0
    assert result["session_history"] == []
