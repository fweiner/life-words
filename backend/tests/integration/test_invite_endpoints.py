"""Integration tests for invite endpoints."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock


# Sample test data
SAMPLE_USER_ID = "test-user-123"
SAMPLE_INVITER_NAME = "John Doe"
SAMPLE_USER = {
    "id": SAMPLE_USER_ID,
    "email": "test@example.com",
    "role": "authenticated"
}
SAMPLE_INVITE = {
    "id": "invite-123",
    "user_id": SAMPLE_USER_ID,
    "recipient_email": "jane@example.com",
    "recipient_name": "Jane Smith",
    "token": "test-token-abc123",
    "custom_message": "Please help me!",
    "status": "pending",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    "completed_at": None,
    "contact_id": None
}
SAMPLE_PROFILE = {
    "id": SAMPLE_USER_ID,
    "full_name": SAMPLE_INVITER_NAME
}
SAMPLE_CONTACT = {
    "id": "contact-456",
    "user_id": SAMPLE_USER_ID,
    "name": "Jane Smith",
    "relationship": "friend",
    "photo_url": "https://example.com/photo.jpg",
    "is_active": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat()
}


# ============== Authenticated Endpoints ==============

def test_create_invite_unauthorized(client):
    """Test that creating an invite requires authentication."""
    response = client.post(
        "/api/life-words/invites",
        json={
            "recipient_email": "jane@example.com",
            "recipient_name": "Jane Smith"
        }
    )
    assert response.status_code == 401


@patch("app.services.invite_service.send_invite_email")
def test_create_invite_success(mock_send_email, app, client, mock_db):
    """Test successfully creating an invite."""
    from app.core.auth import get_current_user
    from app.core.dependencies import get_db

    mock_send_email.return_value = (True, None)

    async def override_get_current_user():
        return SAMPLE_USER

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [SAMPLE_PROFILE]
    mock_db.insert.return_value = [SAMPLE_INVITE]

    response = client.post(
        "/api/life-words/invites",
        json={
            "recipient_email": "jane@example.com",
            "recipient_name": "Jane Smith",
            "custom_message": "Please help me!"
        },
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["recipient_email"] == "jane@example.com"
    assert data["recipient_name"] == "Jane Smith"
    assert data["status"] == "pending"


def test_create_invite_no_profile_name(app, client, mock_db):
    """Test creating invite when user has no name set."""
    from app.core.auth import get_current_user
    from app.core.dependencies import get_db

    async def override_get_current_user():
        return SAMPLE_USER

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": SAMPLE_USER_ID, "full_name": None}]

    response = client.post(
        "/api/life-words/invites",
        json={
            "recipient_email": "jane@example.com",
            "recipient_name": "Jane Smith"
        },
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 400
    assert "name" in response.json()["detail"].lower()


def test_list_invites_unauthorized(client):
    """Test that listing invites requires authentication."""
    response = client.get("/api/life-words/invites")
    assert response.status_code == 401


def test_list_invites_success(app, client, mock_user_id, mock_db):
    """Test successfully listing invites."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [SAMPLE_INVITE]

    response = client.get(
        "/api/life-words/invites",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["recipient_email"] == "jane@example.com"


def test_list_invites_empty(app, client, mock_user_id, mock_db):
    """Test listing invites when user has none."""
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
        "/api/life-words/invites",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    assert response.json() == []


def test_cancel_invite_unauthorized(client):
    """Test that canceling an invite requires authentication."""
    response = client.delete("/api/life-words/invites/invite-123")
    assert response.status_code == 401


def test_cancel_invite_success(app, client, mock_user_id, mock_db):
    """Test successfully canceling an invite."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [SAMPLE_INVITE]
    mock_db.delete.return_value = True

    response = client.delete(
        "/api/life-words/invites/invite-123",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_cancel_invite_not_found(app, client, mock_user_id, mock_db):
    """Test canceling a non-existent invite."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.delete(
        "/api/life-words/invites/invite-123",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 404


def test_cancel_invite_already_completed(app, client, mock_user_id, mock_db):
    """Test canceling an already completed invite."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    completed_invite = {**SAMPLE_INVITE, "status": "completed"}
    mock_db.query.return_value = [completed_invite]

    response = client.delete(
        "/api/life-words/invites/invite-123",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 400
    assert "pending" in response.json()["detail"].lower()


# ============== Public Endpoints ==============

def test_verify_invite_valid(app, client, mock_db):
    """Test verifying a valid invite token."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_INVITE],    # invite lookup
        [SAMPLE_PROFILE],   # profile lookup
    ]

    response = client.get("/api/life-words/invites/verify/test-token-abc123")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["status"] == "pending"


def test_verify_invite_not_found(app, client, mock_db):
    """Test verifying a non-existent token."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.get("/api/life-words/invites/verify/invalid-token")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["status"] == "not_found"


def test_verify_invite_expired(app, client, mock_db):
    """Test verifying an expired invite."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    expired_invite = {
        **SAMPLE_INVITE,
        "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    }
    mock_db.query.return_value = [expired_invite]

    response = client.get("/api/life-words/invites/verify/expired-token")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["status"] == "expired"


@patch("app.services.invite_service.send_thank_you_email")
def test_submit_invite_success(mock_send_email, app, client, mock_db):
    """Test successfully submitting an invite form."""
    from app.core.dependencies import get_db

    mock_send_email.return_value = True

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.side_effect = [
        [SAMPLE_INVITE],    # invite lookup
        [SAMPLE_PROFILE],   # profile lookup for thank you email
    ]
    mock_db.insert.return_value = [SAMPLE_CONTACT]
    mock_db.update.return_value = {**SAMPLE_INVITE, "status": "completed"}

    response = client.post(
        "/api/life-words/invites/submit/test-token-abc123",
        json={
            "name": "Jane Smith",
            "relationship": "friend",
            "photo_url": "https://example.com/photo.jpg"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_submit_invite_not_found(app, client, mock_db):
    """Test submitting to a non-existent invite."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.post(
        "/api/life-words/invites/submit/invalid-token",
        json={
            "name": "Jane Smith",
            "relationship": "friend",
            "photo_url": "https://example.com/photo.jpg"
        }
    )

    assert response.status_code == 404


def test_submit_invite_expired(app, client, mock_db):
    """Test submitting to an expired invite."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    expired_invite = {
        **SAMPLE_INVITE,
        "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    }
    mock_db.query.return_value = [expired_invite]

    response = client.post(
        "/api/life-words/invites/submit/expired-token",
        json={
            "name": "Jane Smith",
            "relationship": "friend",
            "photo_url": "https://example.com/photo.jpg"
        }
    )

    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_submit_invite_already_completed(app, client, mock_db):
    """Test submitting to an already completed invite."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    completed_invite = {**SAMPLE_INVITE, "status": "completed"}
    mock_db.query.return_value = [completed_invite]

    response = client.post(
        "/api/life-words/invites/submit/completed-token",
        json={
            "name": "Jane Smith",
            "relationship": "friend",
            "photo_url": "https://example.com/photo.jpg"
        }
    )

    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_upload_photo_invalid_file(client):
    """Test uploading an invalid file type."""
    response = client.post(
        "/api/life-words/invites/upload-photo",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )

    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower()


@patch("app.services.utils.httpx.AsyncClient")
def test_upload_photo_success(mock_client_class, client):
    """Test successfully uploading a photo."""
    mock_async_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_async_client

    mock_response = MagicMock()
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
        "/api/life-words/invites/upload-photo",
        files={"file": ("test.png", png_data, "image/png")}
    )

    assert response.status_code == 200
    assert "photo_url" in response.json()
