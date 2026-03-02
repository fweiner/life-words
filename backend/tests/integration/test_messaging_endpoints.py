"""Integration tests for messaging endpoints."""
import pytest
from datetime import datetime, timezone


# Sample test data
SAMPLE_USER_ID = "test-user-123"
SAMPLE_CONTACT_ID = "contact-456"
SAMPLE_TOKEN = "test-messaging-token-abc123"

SAMPLE_USER = {
    "id": SAMPLE_USER_ID,
    "email": "test@example.com",
    "role": "authenticated"
}

SAMPLE_CONTACT = {
    "id": SAMPLE_CONTACT_ID,
    "user_id": SAMPLE_USER_ID,
    "name": "Jane Smith",
    "relationship": "friend",
    "photo_url": "https://example.com/photo.jpg",
    "is_active": True
}

SAMPLE_MESSAGE = {
    "id": "msg-123",
    "user_id": SAMPLE_USER_ID,
    "contact_id": SAMPLE_CONTACT_ID,
    "direction": "user_to_contact",
    "text_content": "Hello!",
    "photo_url": None,
    "voice_url": None,
    "voice_duration_seconds": None,
    "is_read": True,
    "read_at": None,
    "created_at": datetime.now(timezone.utc).isoformat()
}

SAMPLE_MESSAGING_TOKEN = {
    "id": "token-123",
    "user_id": SAMPLE_USER_ID,
    "contact_id": SAMPLE_CONTACT_ID,
    "token": SAMPLE_TOKEN,
    "is_active": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "last_used_at": None
}

SAMPLE_PROFILE = {
    "id": SAMPLE_USER_ID,
    "full_name": "John Doe"
}


# ============== Authenticated Endpoints ==============

def test_list_conversations_unauthorized(client):
    """Test that listing conversations requires authentication."""
    response = client.get("/api/life-words/messaging/conversations")
    assert response.status_code == 401


def test_list_conversations_empty(app, client, mock_user_id, mock_db):
    """Test listing conversations when user has no contacts."""
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
        "/api/life-words/messaging/conversations",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_conversations_success(app, client, mock_user_id, mock_db):
    """Test successfully listing conversations."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # First call returns contacts, subsequent calls return empty for tokens, messages
    mock_db.query.side_effect = [
        [SAMPLE_CONTACT],  # contacts
        [SAMPLE_MESSAGING_TOKEN],  # tokens
        [],  # unread messages
        [SAMPLE_MESSAGE]  # latest message
    ]

    response = client.get(
        "/api/life-words/messaging/conversations",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["contact_name"] == "Jane Smith"
    assert data[0]["has_messaging_token"] is True


def test_get_conversation_unauthorized(client):
    """Test that getting a conversation requires authentication."""
    response = client.get(f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}")
    assert response.status_code == 401


def test_get_conversation_not_found(app, client, mock_user_id, mock_db):
    """Test getting a non-existent conversation."""
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
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_get_conversation_success(app, client, mock_user_id, mock_db):
    """Test successfully getting a conversation."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_CONTACT],  # contact lookup
        [SAMPLE_MESSAGE]   # messages
    ]

    response = client.get(
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["contact"]["name"] == "Jane Smith"
    assert len(data["messages"]) == 1


def test_send_message_unauthorized(client):
    """Test that sending a message requires authentication."""
    response = client.post(
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/messages",
        json={"text_content": "Hello!"}
    )
    assert response.status_code == 401


def test_send_message_no_content(app, client, mock_user_id, mock_db):
    """Test sending a message without content fails."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    response = client.post(
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/messages",
        json={},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 400
    assert "content" in response.json()["detail"].lower()


def test_send_message_contact_not_found(app, client, mock_user_id, mock_db):
    """Test sending a message to non-existent contact."""
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
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/messages",
        json={"text_content": "Hello!"},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_send_message_success(app, client, mock_user_id, mock_db):
    """Test successfully sending a message."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [SAMPLE_CONTACT]
    mock_db.insert.return_value = [SAMPLE_MESSAGE]

    response = client.post(
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/messages",
        json={"text_content": "Hello!"},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text_content"] == "Hello!"
    assert data["direction"] == "user_to_contact"


def test_get_unread_count_unauthorized(client):
    """Test that getting unread count requires authentication."""
    response = client.get("/api/life-words/messaging/unread-count")
    assert response.status_code == 401


def test_get_unread_count_success(app, client, mock_user_id, mock_db):
    """Test successfully getting unread count."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "1"}, {"id": "2"}, {"id": "3"}]

    response = client.get(
        "/api/life-words/messaging/unread-count",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    assert response.json()["count"] == 3


def test_get_or_create_token_unauthorized(client):
    """Test that getting a token requires authentication."""
    response = client.get(f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/token")
    assert response.status_code == 401


def test_get_or_create_token_contact_not_found(app, client, mock_user_id, mock_db):
    """Test getting token for non-existent contact."""
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
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/token",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_get_existing_token_success(app, client, mock_user_id, mock_db):
    """Test getting an existing messaging token."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_CONTACT],  # contact lookup
        [SAMPLE_MESSAGING_TOKEN]  # existing token
    ]

    response = client.get(
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/token",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token"] == SAMPLE_TOKEN
    assert "messaging_url" in data


def test_create_new_token_success(app, client, mock_user_id, mock_db):
    """Test creating a new messaging token."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_CONTACT],  # contact lookup
        []  # no existing token
    ]
    mock_db.insert.return_value = [SAMPLE_MESSAGING_TOKEN]

    response = client.get(
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/token",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "messaging_url" in data


# ============== Public Endpoints ==============

def test_verify_token_not_found(app, client, mock_db):
    """Test verifying a non-existent token."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.get("/api/life-words/messaging/public/verify/invalid-token")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["status"] == "not_found"


def test_verify_token_inactive(app, client, mock_db):
    """Test verifying an inactive token."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    inactive_token = {**SAMPLE_MESSAGING_TOKEN, "is_active": False}
    mock_db.query.return_value = [inactive_token]

    response = client.get("/api/life-words/messaging/public/verify/inactive-token")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["status"] == "inactive"


def test_verify_token_valid(app, client, mock_db):
    """Test verifying a valid token."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_MESSAGING_TOKEN],  # token lookup
        [{"name": "Jane Smith", "photo_url": "https://example.com/photo.jpg"}],  # contact
        [SAMPLE_PROFILE],  # profile
    ]
    mock_db.update.return_value = SAMPLE_MESSAGING_TOKEN

    response = client.get(f"/api/life-words/messaging/public/verify/{SAMPLE_TOKEN}")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["status"] == "active"
    assert data["user_name"] == "John Doe"
    assert data["contact_name"] == "Jane Smith"


def test_get_public_messages_invalid_token(app, client, mock_db):
    """Test getting messages with invalid token."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.get("/api/life-words/messaging/public/invalid-token/messages")

    assert response.status_code == 404


def test_get_public_messages_success(app, client, mock_db):
    """Test successfully getting public messages."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_MESSAGING_TOKEN],  # token lookup
        [SAMPLE_MESSAGE],          # messages
    ]

    response = client.get(f"/api/life-words/messaging/public/{SAMPLE_TOKEN}/messages")

    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 1


def test_send_public_message_invalid_token(app, client, mock_db):
    """Test sending message with invalid token."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.post(
        "/api/life-words/messaging/public/invalid-token/messages",
        json={"text_content": "Hello!"}
    )

    assert response.status_code == 404


def test_send_public_message_no_content(client):
    """Test sending public message without content."""
    response = client.post(
        f"/api/life-words/messaging/public/{SAMPLE_TOKEN}/messages",
        json={}
    )

    assert response.status_code == 400
    assert "content" in response.json()["detail"].lower()


def test_send_public_message_success(app, client, mock_db):
    """Test successfully sending a public message."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    incoming_message = {
        **SAMPLE_MESSAGE,
        "direction": "contact_to_user",
        "is_read": False
    }

    mock_db.query.return_value = [SAMPLE_MESSAGING_TOKEN]
    mock_db.insert.return_value = [incoming_message]

    response = client.post(
        f"/api/life-words/messaging/public/{SAMPLE_TOKEN}/messages",
        json={"text_content": "Hello from contact!"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["direction"] == "contact_to_user"


def test_upload_public_media_invalid_type(app, client, mock_db):
    """Test uploading invalid file type."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "token-1"}]  # valid token

    response = client.post(
        "/api/life-words/messaging/public/upload-media?token=test-token&media_type=photo",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )

    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower()


def test_upload_public_photo_success(app, client, mock_db, mocker):
    """Test successfully uploading a photo."""
    from app.core.dependencies import get_db

    mock_client_class = mocker.patch("app.services.utils.httpx.AsyncClient")

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "token-1"}]  # valid token

    mock_async_client = mocker.AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_async_client

    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_async_client.post.return_value = mock_response

    # Create a small valid image (1x1 PNG)
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
        b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
        b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    response = client.post(
        "/api/life-words/messaging/public/upload-media?token=test-token&media_type=photo",
        files={"file": ("test.png", png_data, "image/png")}
    )

    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["media_type"] == "photo"


def test_upload_public_voice_success(app, client, mock_db, mocker):
    """Test successfully uploading a voice message."""
    from app.core.dependencies import get_db

    mock_client_class = mocker.patch("app.services.utils.httpx.AsyncClient")

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "token-1"}]  # valid token

    mock_async_client = mocker.AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_async_client

    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_async_client.post.return_value = mock_response

    # Create dummy audio data
    audio_data = b"dummy audio content"

    response = client.post(
        "/api/life-words/messaging/public/upload-media?token=test-token&media_type=voice",
        files={"file": ("test.webm", audio_data, "audio/webm")}
    )

    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["media_type"] == "voice"


# ============== Additional Tests for Coverage ==============

def test_mark_messages_read_unauthorized(client):
    """Test that marking messages read requires authentication."""
    response = client.put(f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/read")
    assert response.status_code == 401


def test_mark_messages_read_contact_not_found(app, client, mock_user_id, mock_db, mocker):
    """Test marking messages read for non-existent contact."""
    mock_client_class = mocker.patch("app.services.messaging_service.httpx.AsyncClient")
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
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/read",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_mark_messages_read_success(app, client, mock_user_id, mock_db, mocker):
    """Test successfully marking messages as read."""
    mock_client_class = mocker.patch("app.services.messaging_service.httpx.AsyncClient")
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    mock_async_client = mocker.AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_async_client

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [SAMPLE_CONTACT]
    mock_async_client.patch.return_value = mocker.MagicMock()

    response = client.put(
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/read",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_regenerate_token_unauthorized(client):
    """Test that regenerating token requires authentication."""
    response = client.post(f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/token/regenerate")
    assert response.status_code == 401


def test_regenerate_token_contact_not_found(app, client, mock_user_id, mock_db):
    """Test regenerating token for non-existent contact."""
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
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/token/regenerate",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_regenerate_token_success(app, client, mock_user_id, mock_db):
    """Test successfully regenerating a token."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [SAMPLE_CONTACT]
    mock_db.delete.return_value = True
    new_token = {**SAMPLE_MESSAGING_TOKEN, "token": "new-token-xyz"}
    mock_db.insert.return_value = [new_token]

    response = client.post(
        f"/api/life-words/messaging/conversations/{SAMPLE_CONTACT_ID}/token/regenerate",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "messaging_url" in data


def test_upload_public_media_invalid_media_type(app, client, mock_db):
    """Test uploading with invalid media type parameter."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "token-1"}]  # valid token

    response = client.post(
        "/api/life-words/messaging/public/upload-media?token=test-token&media_type=video",
        files={"file": ("test.mp4", b"video data", "video/mp4")}
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


def test_upload_public_voice_invalid_audio_type(app, client, mock_db):
    """Test uploading voice with invalid audio type."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "token-1"}]  # valid token

    response = client.post(
        "/api/life-words/messaging/public/upload-media?token=test-token&media_type=voice",
        files={"file": ("test.txt", b"not audio", "text/plain")}
    )

    assert response.status_code == 400
    assert "audio" in response.json()["detail"].lower()


def test_authenticated_upload_media_unauthorized(client):
    """Test that authenticated upload requires authentication."""
    response = client.post(
        "/api/life-words/messaging/upload-media?media_type=photo",
        files={"file": ("test.png", b"image data", "image/png")}
    )

    assert response.status_code == 401


def test_authenticated_upload_media_success(app, client, mock_user_id, mock_db, mocker):
    """Test authenticated media upload."""
    mock_client_class = mocker.patch("app.services.utils.httpx.AsyncClient")
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    mock_async_client = mocker.AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_async_client

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_async_client.post.return_value = mock_response

    # Create a small valid image (1x1 PNG)
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
        b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
        b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    response = client.post(
        "/api/life-words/messaging/upload-media?media_type=photo",
        files={"file": ("test.png", png_data, "image/png")},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    assert "url" in response.json()
