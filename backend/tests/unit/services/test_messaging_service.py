"""Unit tests for messaging service."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


SAMPLE_CONTACT = {
    "id": "contact-123",
    "user_id": "user-123",
    "name": "John",
    "photo_url": "https://example.com/photo.jpg",
    "relationship": "friend",
    "is_active": True,
}

SAMPLE_MESSAGE = {
    "id": "msg-001",
    "user_id": "user-123",
    "contact_id": "contact-123",
    "direction": "user_to_contact",
    "text_content": "Hello!",
    "photo_url": None,
    "voice_url": None,
    "voice_duration_seconds": None,
    "is_read": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
}

SAMPLE_TOKEN_DATA = {
    "id": "token-001",
    "user_id": "user-123",
    "contact_id": "contact-123",
    "token": "abc123tokenvalue",
    "is_active": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "last_used_at": None,
}


# ---- list_conversations ----


@pytest.mark.asyncio
async def test_list_conversations_success(mock_db):
    """Test listing conversations returns sorted conversation summaries."""
    from app.services.messaging_service import MessagingService

    contact2 = {**SAMPLE_CONTACT, "id": "contact-456", "name": "Jane"}

    # First call: contacts query
    # Second call: tokens query
    # Then for each contact: unread messages query, then latest message query
    mock_db.query.side_effect = [
        [SAMPLE_CONTACT, contact2],                                # contacts
        [{"contact_id": "contact-123"}],                           # tokens
        [{"id": "unread-1"}],                                      # unread for contact-123
        [{"text_content": "Hello!", "created_at": "2024-01-02T00:00:00Z", "direction": "user_to_contact"}],  # latest msg for contact-123
        [],                                                        # unread for contact-456
        [{"text_content": "Hi!", "created_at": "2024-01-03T00:00:00Z", "direction": "contact_to_user"}],     # latest msg for contact-456
    ]

    service = MessagingService(mock_db)
    result = await service.list_conversations("user-123")

    assert len(result) == 2
    # contact-456 should be first (more recent last_message_at)
    assert result[0]["contact_id"] == "contact-456"
    assert result[0]["unread_count"] == 0
    assert result[0]["last_message_text"] == "Hi!"
    assert result[1]["contact_id"] == "contact-123"
    assert result[1]["unread_count"] == 1
    assert result[1]["has_messaging_token"] is True


@pytest.mark.asyncio
async def test_list_conversations_no_contacts(mock_db):
    """Test listing conversations returns empty list when no contacts."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = []

    service = MessagingService(mock_db)
    result = await service.list_conversations("user-123")

    assert result == []


# ---- get_conversation ----


@pytest.mark.asyncio
async def test_get_conversation_success(mock_db):
    """Test getting a conversation returns contact and messages."""
    from app.services.messaging_service import MessagingService

    mock_db.query.side_effect = [
        [SAMPLE_CONTACT],                  # contact lookup
        [SAMPLE_MESSAGE],                  # messages query
    ]

    service = MessagingService(mock_db)
    result = await service.get_conversation("contact-123", "user-123")

    assert result["contact"]["id"] == "contact-123"
    assert len(result["messages"]) == 1
    assert result["messages"][0]["text_content"] == "Hello!"


@pytest.mark.asyncio
async def test_get_conversation_not_found(mock_db):
    """Test getting conversation for non-existent contact raises 404."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = []

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_conversation("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


# ---- send_message ----


@pytest.mark.asyncio
async def test_send_message_success(mock_db):
    """Test sending a text message succeeds."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = [{"id": "contact-123"}]
    mock_db.insert.return_value = [SAMPLE_MESSAGE]

    message_data = MagicMock()
    message_data.text_content = "Hello!"
    message_data.photo_url = None
    message_data.voice_url = None
    message_data.voice_duration_seconds = None

    service = MessagingService(mock_db)
    result = await service.send_message("contact-123", "user-123", message_data)

    assert result["text_content"] == "Hello!"
    mock_db.insert.assert_called_once()
    call_data = mock_db.insert.call_args.args[1]
    assert call_data["direction"] == "user_to_contact"
    assert call_data["is_read"] is True


@pytest.mark.asyncio
async def test_send_message_no_content(mock_db):
    """Test sending a message with no content raises 400."""
    from app.services.messaging_service import MessagingService

    message_data = MagicMock()
    message_data.text_content = None
    message_data.photo_url = None
    message_data.voice_url = None

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.send_message("contact-123", "user-123", message_data)

    assert exc_info.value.status_code == 400
    assert "content" in exc_info.value.detail


@pytest.mark.asyncio
async def test_send_message_contact_not_found(mock_db):
    """Test sending a message to non-existent contact raises 404."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = []

    message_data = MagicMock()
    message_data.text_content = "Hello!"
    message_data.photo_url = None
    message_data.voice_url = None

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.send_message("nonexistent", "user-123", message_data)

    assert exc_info.value.status_code == 404


# ---- mark_messages_read ----


@pytest.mark.asyncio
async def test_mark_messages_read_success(mock_db):
    """Test marking messages as read succeeds using raw httpx."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = [{"id": "contact-123"}]

    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client_instance = AsyncMock()
    mock_client_instance.patch.return_value = mock_response
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.messaging_service.httpx.AsyncClient", return_value=mock_client_instance):
        service = MessagingService(mock_db)
        result = await service.mark_messages_read("contact-123", "user-123")

    assert result["success"] is True
    mock_client_instance.patch.assert_called_once()
    call_kwargs = mock_client_instance.patch.call_args
    assert "is_read" in call_kwargs.kwargs["json"]
    assert call_kwargs.kwargs["json"]["is_read"] is True


@pytest.mark.asyncio
async def test_mark_messages_read_contact_not_found(mock_db):
    """Test marking messages read for non-existent contact raises 404."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = []

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.mark_messages_read("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


# ---- get_or_create_messaging_token ----


@pytest.mark.asyncio
async def test_get_or_create_messaging_token_existing(mock_db):
    """Test getting an existing messaging token returns it."""
    from app.services.messaging_service import MessagingService

    mock_db.query.side_effect = [
        [{"id": "contact-123"}],    # contact lookup
        [SAMPLE_TOKEN_DATA],        # existing token
    ]

    service = MessagingService(mock_db)
    result = await service.get_or_create_messaging_token("contact-123", "user-123")

    assert result["token"] == "abc123tokenvalue"
    assert result["contact_id"] == "contact-123"
    assert "messaging_url" in result
    assert result["is_active"] is True
    mock_db.insert.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_messaging_token_new(mock_db):
    """Test creating a new messaging token when none exists."""
    from app.services.messaging_service import MessagingService

    new_token_data = {**SAMPLE_TOKEN_DATA, "token": "new-generated-token"}

    mock_db.query.side_effect = [
        [{"id": "contact-123"}],    # contact lookup
        [],                         # no existing token
    ]
    mock_db.insert.return_value = [new_token_data]

    with patch("app.services.messaging_service.generate_secure_token", return_value="new-generated-token"):
        service = MessagingService(mock_db)
        result = await service.get_or_create_messaging_token("contact-123", "user-123")

    assert result["token"] == "new-generated-token"
    assert "messaging_url" in result
    mock_db.insert.assert_called_once()
    call_data = mock_db.insert.call_args.args[1]
    assert call_data["token"] == "new-generated-token"
    assert call_data["is_active"] is True


@pytest.mark.asyncio
async def test_get_or_create_messaging_token_contact_not_found(mock_db):
    """Test getting token for non-existent contact raises 404."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = []

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_or_create_messaging_token("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


# ---- regenerate_messaging_token ----


@pytest.mark.asyncio
async def test_regenerate_messaging_token_success(mock_db):
    """Test regenerating a token deletes old and creates new."""
    from app.services.messaging_service import MessagingService

    new_token_data = {**SAMPLE_TOKEN_DATA, "token": "regenerated-token"}

    mock_db.query.return_value = [{"id": "contact-123"}]
    mock_db.insert.return_value = [new_token_data]

    with patch("app.services.messaging_service.generate_secure_token", return_value="regenerated-token"):
        service = MessagingService(mock_db)
        result = await service.regenerate_messaging_token("contact-123", "user-123")

    assert result["token"] == "regenerated-token"
    assert result["last_used_at"] is None
    mock_db.delete.assert_called_once_with(
        "contact_messaging_tokens",
        {"contact_id": "contact-123", "user_id": "user-123"}
    )
    mock_db.insert.assert_called_once()


# ---- get_unread_count ----


@pytest.mark.asyncio
async def test_get_unread_count(mock_db):
    """Test getting unread count returns correct number."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = [{"id": "msg-1"}, {"id": "msg-2"}, {"id": "msg-3"}]

    service = MessagingService(mock_db)
    result = await service.get_unread_count("user-123")

    assert result["count"] == 3
    call_kwargs = mock_db.query.call_args.kwargs
    assert call_kwargs["filters"]["direction"] == "contact_to_user"
    assert call_kwargs["filters"]["is_read"] is False


# ---- verify_messaging_token ----


@pytest.mark.asyncio
async def test_verify_messaging_token_valid(mock_db):
    """Test verifying a valid active token returns contact and user info."""
    from app.services.messaging_service import MessagingService

    mock_db.query.side_effect = [
        [SAMPLE_TOKEN_DATA],                                    # token lookup
        [{"name": "John", "photo_url": "https://example.com/photo.jpg"}],  # contact
        [{"full_name": "Test User"}],                           # profile
    ]

    service = MessagingService(mock_db)
    result = await service.verify_messaging_token("abc123tokenvalue")

    assert result["valid"] is True
    assert result["status"] == "active"
    assert result["user_name"] == "Test User"
    assert result["contact_name"] == "John"
    assert result["contact_photo_url"] == "https://example.com/photo.jpg"
    mock_db.update.assert_called_once()  # last_used_at updated


@pytest.mark.asyncio
async def test_verify_messaging_token_not_found(mock_db):
    """Test verifying a non-existent token returns not_found."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = []

    service = MessagingService(mock_db)
    result = await service.verify_messaging_token("nonexistent-token")

    assert result["valid"] is False
    assert result["status"] == "not_found"


@pytest.mark.asyncio
async def test_verify_messaging_token_inactive(mock_db):
    """Test verifying an inactive token returns inactive."""
    from app.services.messaging_service import MessagingService

    inactive_token = {**SAMPLE_TOKEN_DATA, "is_active": False}
    mock_db.query.return_value = [inactive_token]

    service = MessagingService(mock_db)
    result = await service.verify_messaging_token("abc123tokenvalue")

    assert result["valid"] is False
    assert result["status"] == "inactive"


# ---- get_public_messages ----


@pytest.mark.asyncio
async def test_get_public_messages_success(mock_db):
    """Test getting public messages via token returns messages."""
    from app.services.messaging_service import MessagingService

    msg_from_contact = {
        **SAMPLE_MESSAGE,
        "direction": "contact_to_user",
        "text_content": "Hi there!",
    }

    mock_db.query.side_effect = [
        [SAMPLE_TOKEN_DATA],                      # token lookup
        [SAMPLE_MESSAGE, msg_from_contact],        # messages
    ]

    service = MessagingService(mock_db)
    result = await service.get_public_messages("abc123tokenvalue")

    assert len(result["messages"]) == 2


@pytest.mark.asyncio
async def test_get_public_messages_invalid_token(mock_db):
    """Test getting public messages with invalid token raises 404."""
    from app.services.messaging_service import MessagingService

    mock_db.query.return_value = []

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_public_messages("invalid-token")

    assert exc_info.value.status_code == 404


# ---- send_public_message ----


@pytest.mark.asyncio
async def test_send_public_message_success(mock_db):
    """Test sending a public message from contact to user."""
    from app.services.messaging_service import MessagingService

    public_msg = {
        **SAMPLE_MESSAGE,
        "direction": "contact_to_user",
        "is_read": False,
    }

    mock_db.query.return_value = [SAMPLE_TOKEN_DATA]
    mock_db.insert.return_value = [public_msg]

    message_data = MagicMock()
    message_data.text_content = "Hello from contact!"
    message_data.photo_url = None
    message_data.voice_url = None
    message_data.voice_duration_seconds = None

    service = MessagingService(mock_db)
    result = await service.send_public_message("abc123tokenvalue", message_data)

    assert result["direction"] == "contact_to_user"
    assert result["is_read"] is False
    call_data = mock_db.insert.call_args.args[1]
    assert call_data["direction"] == "contact_to_user"
    assert call_data["is_read"] is False


@pytest.mark.asyncio
async def test_send_public_message_no_content(mock_db):
    """Test sending a public message with no content raises 400."""
    from app.services.messaging_service import MessagingService

    message_data = MagicMock()
    message_data.text_content = None
    message_data.photo_url = None
    message_data.voice_url = None

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.send_public_message("abc123tokenvalue", message_data)

    assert exc_info.value.status_code == 400
    assert "content" in exc_info.value.detail


# ---- upload_media ----


@pytest.mark.asyncio
async def test_upload_media_photo_success(mock_db):
    """Test uploading a photo succeeds."""
    from app.services.messaging_service import MessagingService

    mock_file = MagicMock()
    mock_file.content_type = "image/jpeg"
    mock_file.filename = "photo.jpg"
    mock_file.read = AsyncMock(return_value=b"fake-image-data")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.utils.httpx.AsyncClient", return_value=mock_client_instance):
        service = MessagingService(mock_db)
        result = await service.upload_media(mock_file, media_type="photo")

    assert result["media_type"] == "photo"
    assert "url" in result
    assert "message-photos" in result["url"]
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_upload_media_voice_success(mock_db):
    """Test uploading a voice message succeeds."""
    from app.services.messaging_service import MessagingService

    mock_file = MagicMock()
    mock_file.content_type = "audio/webm"
    mock_file.filename = "recording.webm"
    mock_file.read = AsyncMock(return_value=b"fake-audio-data")

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.text = "Created"

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.utils.httpx.AsyncClient", return_value=mock_client_instance):
        service = MessagingService(mock_db)
        result = await service.upload_media(mock_file, media_type="voice")

    assert result["media_type"] == "voice"
    assert "url" in result
    assert "message-voice" in result["url"]


@pytest.mark.asyncio
async def test_upload_media_invalid_type(mock_db):
    """Test uploading with invalid media_type raises 400."""
    from app.services.messaging_service import MessagingService

    mock_file = MagicMock()
    mock_file.content_type = "image/jpeg"
    mock_file.filename = "photo.jpg"

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.upload_media(mock_file, media_type="video")

    assert exc_info.value.status_code == 400
    assert "Invalid media type" in exc_info.value.detail


@pytest.mark.asyncio
async def test_upload_media_invalid_content_type(mock_db):
    """Test uploading a photo with wrong content type raises 400."""
    from app.services.messaging_service import MessagingService

    mock_file = MagicMock()
    mock_file.content_type = "application/pdf"
    mock_file.filename = "document.pdf"

    service = MessagingService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.upload_media(mock_file, media_type="photo")

    assert exc_info.value.status_code == 400
    assert "image" in exc_info.value.detail
