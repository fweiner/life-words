"""Unit tests for invite service."""
import pytest
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from app.services.invite_service import InviteService
from app.models.invites import ContactInviteCreate, InviteSubmitRequest


SAMPLE_USER = {
    "id": "user-123",
    "email": "user@example.com",
}

SAMPLE_PROFILE = {
    "id": "user-123",
    "email": "user@example.com",
    "full_name": "Test User",
}

SAMPLE_INVITE = {
    "id": "invite-001",
    "user_id": "user-123",
    "recipient_email": "friend@example.com",
    "recipient_name": "Friend Name",
    "token": "mock-token-abc123",
    "custom_message": "Please help me!",
    "status": "pending",
    "contact_id": None,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    "completed_at": None,
}

SAMPLE_INVITE_DATA = ContactInviteCreate(
    recipient_email="friend@example.com",
    recipient_name="Friend Name",
    custom_message="Please help me!",
)

SAMPLE_CONTACT_DATA = InviteSubmitRequest(
    name="Friend Name",
    nickname="Buddy",
    relationship="friend",
    photo_url="https://example.com/photo.jpg",
    category="friends",
    description="A good friend",
    association="college",
    location_context="New York",
    interests="hiking",
    personality="friendly",
    values="honesty",
    social_behavior="outgoing",
)

SAMPLE_CREATED_CONTACT = {
    "id": "contact-999",
    "user_id": "user-123",
    "name": "Friend Name",
    "relationship": "friend",
    "photo_url": "https://example.com/photo.jpg",
}


# ---- create_invite ----


@pytest.mark.asyncio
async def test_create_invite_success(mock_db, mocker):
    """Test creating an invite successfully with email sent."""
    # Mock ProfileService.get_or_create_profile
    mocker.patch(
        "app.services.invite_service.ProfileService"
    ).return_value.get_or_create_profile = mocker.AsyncMock(return_value=SAMPLE_PROFILE)

    # Mock token generation
    mocker.patch(
        "app.services.invite_service.generate_secure_token",
        return_value="mock-token-abc123",
    )

    # Mock email sending
    mock_send_email = mocker.patch(
        "app.services.invite_service.send_invite_email",
        new_callable=mocker.AsyncMock,
        return_value=(True, None),
    )

    mock_db.insert.return_value = [SAMPLE_INVITE]

    service = InviteService(mock_db)
    result = await service.create_invite(SAMPLE_USER, SAMPLE_INVITE_DATA)

    assert result["id"] == "invite-001"
    assert result["status"] == "pending"
    mock_db.insert.assert_called_once()
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
async def test_create_invite_no_profile_name(mock_db, mocker):
    """Test creating an invite when user has no full_name set raises 400."""
    profile_no_name = {**SAMPLE_PROFILE, "full_name": None}
    mocker.patch(
        "app.services.invite_service.ProfileService"
    ).return_value.get_or_create_profile = mocker.AsyncMock(return_value=profile_no_name)

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_invite(SAMPLE_USER, SAMPLE_INVITE_DATA)

    assert exc_info.value.status_code == 400
    assert "name" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_create_invite_email_failure(mock_db, mocker):
    """Test that email send failure deletes invite and raises 500."""
    mocker.patch(
        "app.services.invite_service.ProfileService"
    ).return_value.get_or_create_profile = mocker.AsyncMock(return_value=SAMPLE_PROFILE)

    mocker.patch(
        "app.services.invite_service.generate_secure_token",
        return_value="mock-token-abc123",
    )

    mocker.patch(
        "app.services.invite_service.send_invite_email",
        new_callable=mocker.AsyncMock,
        return_value=(False, "SMTP error"),
    )

    mock_db.insert.return_value = [SAMPLE_INVITE]

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_invite(SAMPLE_USER, SAMPLE_INVITE_DATA)

    assert exc_info.value.status_code == 500
    assert "SMTP error" in exc_info.value.detail
    # Invite should be deleted on email failure
    mock_db.delete.assert_called_once_with(
        "contact_invites", {"id": "invite-001"}
    )


# ---- list_invites ----


@pytest.mark.asyncio
async def test_list_invites_success(mock_db):
    """Test listing invites returns list of invites."""
    invite2 = {**SAMPLE_INVITE, "id": "invite-002", "recipient_name": "Another Friend"}
    mock_db.query.return_value = [SAMPLE_INVITE, invite2]

    service = InviteService(mock_db)
    result = await service.list_invites("user-123")

    assert len(result) == 2
    assert result[0]["id"] == "invite-001"
    assert result[1]["id"] == "invite-002"
    mock_db.query.assert_called_once_with(
        "contact_invites",
        select="*",
        filters={"user_id": "user-123"},
        order="created_at.desc",
    )


@pytest.mark.asyncio
async def test_list_invites_empty(mock_db):
    """Test listing invites when none exist returns empty list."""
    mock_db.query.return_value = None

    service = InviteService(mock_db)
    result = await service.list_invites("user-123")

    assert result == []


# ---- cancel_invite ----


@pytest.mark.asyncio
async def test_cancel_invite_success(mock_db):
    """Test cancelling a pending invite."""
    mock_db.query.return_value = [SAMPLE_INVITE]

    service = InviteService(mock_db)
    result = await service.cancel_invite("invite-001", "user-123")

    assert result["success"] is True
    mock_db.delete.assert_called_once_with("contact_invites", {"id": "invite-001"})


@pytest.mark.asyncio
async def test_cancel_invite_not_found(mock_db):
    """Test cancelling a non-existent invite raises 404."""
    mock_db.query.return_value = []

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.cancel_invite("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_cancel_invite_already_completed(mock_db):
    """Test cancelling a completed invite raises 400."""
    completed_invite = {**SAMPLE_INVITE, "status": "completed"}
    mock_db.query.return_value = [completed_invite]

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.cancel_invite("invite-001", "user-123")

    assert exc_info.value.status_code == 400
    assert "pending" in exc_info.value.detail.lower()


# ---- verify_invite ----


@pytest.mark.asyncio
async def test_verify_invite_valid(mock_db):
    """Test verifying a valid pending invite."""
    mock_db.query.side_effect = [
        [SAMPLE_INVITE],  # invite query
        [SAMPLE_PROFILE],  # profile query for inviter's name
    ]

    service = InviteService(mock_db)
    result = await service.verify_invite("mock-token-abc123")

    assert result["valid"] is True
    assert result["status"] == "pending"
    assert result["inviter_name"] == "Test User"
    assert result["recipient_name"] == "Friend Name"


@pytest.mark.asyncio
async def test_verify_invite_not_found(mock_db):
    """Test verifying a token that doesn't exist."""
    mock_db.query.return_value = []

    service = InviteService(mock_db)
    result = await service.verify_invite("bad-token")

    assert result["valid"] is False
    assert result["status"] == "not_found"


@pytest.mark.asyncio
async def test_verify_invite_expired(mock_db):
    """Test verifying an expired invite."""
    expired_invite = {
        **SAMPLE_INVITE,
        "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    }
    mock_db.query.return_value = [expired_invite]

    service = InviteService(mock_db)
    result = await service.verify_invite("mock-token-abc123")

    assert result["valid"] is False
    assert result["status"] == "expired"


@pytest.mark.asyncio
async def test_verify_invite_completed(mock_db):
    """Test verifying a completed invite returns contact name."""
    completed_invite = {
        **SAMPLE_INVITE,
        "status": "completed",
        "contact_id": "contact-999",
    }
    mock_db.query.side_effect = [
        [completed_invite],  # invite query
        [{"name": "Friend Name"}],  # contact query
    ]

    service = InviteService(mock_db)
    result = await service.verify_invite("mock-token-abc123")

    assert result["valid"] is False
    assert result["status"] == "completed"
    assert result["contact_name"] == "Friend Name"


# ---- submit_invite ----


@pytest.mark.asyncio
async def test_submit_invite_success(mock_db, mocker):
    """Test submitting an invite successfully creates contact."""
    mock_db.query.side_effect = [
        [SAMPLE_INVITE],  # invite query
        [SAMPLE_PROFILE],  # profile query for inviter's name
    ]
    mock_db.insert.return_value = [SAMPLE_CREATED_CONTACT]

    mock_send_thank_you = mocker.patch(
        "app.services.invite_service.send_thank_you_email",
        new_callable=mocker.AsyncMock,
        return_value=True,
    )

    service = InviteService(mock_db)
    result = await service.submit_invite("mock-token-abc123", SAMPLE_CONTACT_DATA)

    assert result["success"] is True
    assert result["contact_name"] == "Friend Name"
    mock_db.insert.assert_called_once()
    mock_db.update.assert_called_once()
    # Check the update sets status to completed
    update_data = mock_db.update.call_args.args[2]
    assert update_data["status"] == "completed"
    assert update_data["contact_id"] == "contact-999"
    mock_send_thank_you.assert_called_once()


@pytest.mark.asyncio
async def test_submit_invite_not_found(mock_db):
    """Test submitting with an invalid token raises 404."""
    mock_db.query.return_value = []

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.submit_invite("bad-token", SAMPLE_CONTACT_DATA)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_submit_invite_expired(mock_db):
    """Test submitting an expired invite raises 400."""
    expired_invite = {
        **SAMPLE_INVITE,
        "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    }
    mock_db.query.return_value = [expired_invite]

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.submit_invite("mock-token-abc123", SAMPLE_CONTACT_DATA)

    assert exc_info.value.status_code == 400
    assert "expired" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_submit_invite_already_completed(mock_db):
    """Test submitting an already completed invite raises 400."""
    completed_invite = {**SAMPLE_INVITE, "status": "completed"}
    mock_db.query.return_value = [completed_invite]

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.submit_invite("mock-token-abc123", SAMPLE_CONTACT_DATA)

    assert exc_info.value.status_code == 400
    assert "already been used" in exc_info.value.detail.lower()


# ---- verify_invite_token_for_upload ----


@pytest.mark.asyncio
async def test_verify_invite_token_for_upload_valid(mock_db):
    """Test verifying a valid invite token for upload."""
    mock_db.query.return_value = [SAMPLE_INVITE]

    service = InviteService(mock_db)
    # Should not raise
    await service.verify_invite_token_for_upload("mock-token-abc123")


@pytest.mark.asyncio
async def test_verify_invite_token_for_upload_invalid(mock_db):
    """Test verifying an invalid invite token for upload."""
    mock_db.query.return_value = []

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.verify_invite_token_for_upload("bad-token")

    assert exc_info.value.status_code == 403
    assert "invalid" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_invite_token_for_upload_expired(mock_db):
    """Test verifying an expired invite token for upload."""
    expired_invite = {
        **SAMPLE_INVITE,
        "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    }
    mock_db.query.return_value = [expired_invite]

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.verify_invite_token_for_upload("mock-token-abc123")

    assert exc_info.value.status_code == 403
    assert "expired" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_invite_token_for_upload_completed(mock_db):
    """Test verifying a completed invite token for upload."""
    completed_invite = {**SAMPLE_INVITE, "status": "completed"}
    mock_db.query.return_value = [completed_invite]

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.verify_invite_token_for_upload("mock-token-abc123")

    assert exc_info.value.status_code == 403
    assert "already been used" in exc_info.value.detail.lower()


# ---- upload_photo ----


@pytest.mark.asyncio
async def test_upload_photo_success(mock_db, mocker):
    """Test uploading a photo successfully."""
    mock_file = mocker.MagicMock()
    mock_file.content_type = "image/jpeg"
    mock_file.filename = "photo.jpg"
    mock_file.read = mocker.AsyncMock(return_value=b"fake-image-data")

    # Mock httpx.AsyncClient
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_client_instance = mocker.AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__ = mocker.AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = mocker.AsyncMock(return_value=False)
    mocker.patch(
        "app.services.utils.httpx.AsyncClient",
        return_value=mock_client_instance,
    )

    service = InviteService(mock_db)
    result = await service.upload_photo(mock_file)

    assert "photo_url" in result
    assert "user-uploads" in result["photo_url"]


@pytest.mark.asyncio
async def test_upload_photo_invalid_type(mock_db, mocker):
    """Test uploading a non-image file raises 400."""
    mock_file = mocker.MagicMock()
    mock_file.content_type = "application/pdf"
    mock_file.filename = "document.pdf"

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.upload_photo(mock_file)

    assert exc_info.value.status_code == 400
    assert "image" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_upload_photo_too_large(mock_db, mocker):
    """Test uploading a file over 5MB raises 400."""
    mock_file = mocker.MagicMock()
    mock_file.content_type = "image/jpeg"
    mock_file.filename = "large_photo.jpg"
    # 6MB of data
    mock_file.read = mocker.AsyncMock(return_value=b"x" * (6 * 1024 * 1024))

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.upload_photo(mock_file)

    assert exc_info.value.status_code == 400
    assert "5MB" in exc_info.value.detail


@pytest.mark.asyncio
async def test_upload_photo_no_content_type(mock_db, mocker):
    """Test uploading a file with no content type raises 400."""
    mock_file = mocker.MagicMock()
    mock_file.content_type = None
    mock_file.filename = "unknown"

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.upload_photo(mock_file)

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_upload_photo_storage_failure(mock_db, mocker):
    """Test upload failure from storage returns 500."""
    mock_file = mocker.MagicMock()
    mock_file.content_type = "image/png"
    mock_file.filename = "photo.png"
    mock_file.read = mocker.AsyncMock(return_value=b"fake-image-data")

    mock_response = mocker.MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_client_instance = mocker.AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__ = mocker.AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = mocker.AsyncMock(return_value=False)
    mocker.patch(
        "app.services.utils.httpx.AsyncClient",
        return_value=mock_client_instance,
    )

    service = InviteService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.upload_photo(mock_file)

    assert exc_info.value.status_code == 500
    assert "Upload failed" in exc_info.value.detail
