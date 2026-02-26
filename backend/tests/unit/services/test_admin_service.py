"""Unit tests for admin service."""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.services.admin_service import AdminService


SAMPLE_USER_STATS = [
    {
        "id": "user-1",
        "email": "user1@example.com",
        "full_name": "User One",
        "created_at": "2024-01-01T00:00:00Z",
        "contact_count": 5,
        "item_count": 3,
        "session_count": 10,
        "last_active_at": "2024-06-01T00:00:00Z",
        "account_status": "trial",
        "trial_ends_at": "2026-06-01T00:00:00Z",
        "stripe_customer_id": None,
        "subscription_plan": None,
        "subscription_current_period_end": None,
    },
    {
        "id": "user-2",
        "email": "user2@example.com",
        "full_name": None,
        "created_at": "2024-02-01T00:00:00Z",
        "contact_count": 0,
        "item_count": 0,
        "session_count": 0,
        "last_active_at": None,
        "account_status": "paid",
        "trial_ends_at": None,
        "stripe_customer_id": "cus_abc",
        "subscription_plan": "monthly",
        "subscription_current_period_end": "2026-03-01T00:00:00Z",
    },
]


def _mock_httpx_client(mocker, method="delete", status_code=200, json_data=None, text=""):
    """Helper to create a mock httpx AsyncClient."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.text = text
    if json_data is not None:
        mock_response.json.return_value = json_data

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    setattr(mock_client, method, mocker.AsyncMock(return_value=mock_response))

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)
    return mock_client


# --- list_users_with_stats ---

@pytest.mark.asyncio
async def test_list_users_with_stats(mock_db):
    """Test listing users with stats calls RPC correctly."""
    mock_db.rpc.return_value = SAMPLE_USER_STATS
    service = AdminService(mock_db)

    result = await service.list_users_with_stats()

    assert result == SAMPLE_USER_STATS
    mock_db.rpc.assert_called_once_with("get_admin_user_stats")


@pytest.mark.asyncio
async def test_list_users_empty(mock_db):
    """Test listing users returns empty list when no users exist."""
    mock_db.rpc.return_value = []
    service = AdminService(mock_db)

    result = await service.list_users_with_stats()

    assert result == []
    mock_db.rpc.assert_called_once_with("get_admin_user_stats")


# --- delete_user ---

@pytest.mark.asyncio
async def test_delete_user_success(mock_db, mocker):
    """Test successful user deletion."""
    mock_client = _mock_httpx_client(mocker, "delete", 200)

    service = AdminService(mock_db)
    await service.delete_user("user-1")

    mock_client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_204_success(mock_db, mocker):
    """Test successful user deletion with 204 No Content response."""
    mock_client = _mock_httpx_client(mocker, "delete", 204)

    service = AdminService(mock_db)
    await service.delete_user("user-1")

    mock_client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_not_found(mock_db, mocker):
    """Test deleting a nonexistent user raises 404."""
    _mock_httpx_client(mocker, "delete", 404)

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_user("nonexistent-user")

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_user_api_error(mock_db, mocker):
    """Test API error during deletion raises 500."""
    _mock_httpx_client(mocker, "delete", 500, text="Internal Server Error")

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_user("user-1")

    assert exc_info.value.status_code == 500
    assert "Failed to delete user" in exc_info.value.detail


# --- create_user ---

@pytest.mark.asyncio
async def test_create_user_success(mock_db, mocker):
    """Test successful user creation."""
    mock_client = _mock_httpx_client(
        mocker, "post", 200, json_data={"id": "new-user-1"}
    )

    service = AdminService(mock_db)
    user_id = await service.create_user(
        email="new@example.com",
        password="password123",
        full_name="New User",
        account_status="trial",
        trial_days=30,
    )

    assert user_id == "new-user-1"
    mock_client.post.assert_called_once()
    mock_db.update.assert_called_once()

    # Verify profile update includes trial_ends_at
    update_call = mock_db.update.call_args
    assert update_call.kwargs["filters"] == {"id": "new-user-1"}
    data = update_call.kwargs["data"]
    assert data["account_status"] == "trial"
    assert data["full_name"] == "New User"
    assert "trial_ends_at" in data


@pytest.mark.asyncio
async def test_create_user_paid_status(mock_db, mocker):
    """Test creating user with paid status clears trial_ends_at."""
    _mock_httpx_client(mocker, "post", 200, json_data={"id": "new-user-2"})

    service = AdminService(mock_db)
    user_id = await service.create_user(
        email="paid@example.com",
        password="password123",
        account_status="paid",
    )

    assert user_id == "new-user-2"
    update_call = mock_db.update.call_args
    data = update_call.kwargs["data"]
    assert data["account_status"] == "paid"
    assert data["trial_ends_at"] is None


@pytest.mark.asyncio
async def test_create_user_with_subscription_plan(mock_db, mocker):
    """Test creating user with subscription plan."""
    _mock_httpx_client(mocker, "post", 200, json_data={"id": "new-user-3"})

    service = AdminService(mock_db)
    await service.create_user(
        email="sub@example.com",
        password="password123",
        account_status="paid",
        subscription_plan="monthly",
    )

    update_call = mock_db.update.call_args
    data = update_call.kwargs["data"]
    assert data["subscription_plan"] == "monthly"


@pytest.mark.asyncio
async def test_create_user_invalid_status(mock_db, mocker):
    """Test creating user with invalid status raises 400."""
    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_user(
            email="bad@example.com",
            password="password123",
            account_status="premium",
        )

    assert exc_info.value.status_code == 400
    assert "Invalid account status" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_user_duplicate_email(mock_db, mocker):
    """Test creating user with existing email raises 400."""
    _mock_httpx_client(mocker, "post", 422)

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_user(
            email="existing@example.com",
            password="password123",
        )

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_user_api_error(mock_db, mocker):
    """Test Auth API error during creation raises 500."""
    _mock_httpx_client(mocker, "post", 500, text="Server error")

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_user(
            email="err@example.com",
            password="password123",
        )

    assert exc_info.value.status_code == 500
    assert "Failed to create user" in exc_info.value.detail


# --- update_user ---

@pytest.mark.asyncio
async def test_update_user_profile_only(mock_db, mocker):
    """Test updating only profile fields (no auth changes)."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    mock_db.rpc.return_value = [SAMPLE_USER_STATS[0]]

    service = AdminService(mock_db)
    result = await service.update_user(
        user_id="user-1",
        full_name="Updated Name",
        account_status="paid",
    )

    assert result["id"] == "user-1"
    mock_db.update.assert_called_once()
    update_data = mock_db.update.call_args.kwargs["data"]
    assert update_data["full_name"] == "Updated Name"
    assert update_data["account_status"] == "paid"
    assert update_data["trial_ends_at"] is None


@pytest.mark.asyncio
async def test_update_user_with_auth_changes(mock_db, mocker):
    """Test updating email and password via Auth Admin API."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    mock_db.rpc.return_value = [SAMPLE_USER_STATS[0]]
    mock_client = _mock_httpx_client(mocker, "put", 200)

    service = AdminService(mock_db)
    await service.update_user(
        user_id="user-1",
        email="newemail@example.com",
        password="newpassword123",
    )

    mock_client.put.assert_called_once()
    call_args = mock_client.put.call_args
    body = call_args.kwargs["json"]
    assert body["email"] == "newemail@example.com"
    assert body["password"] == "newpassword123"


@pytest.mark.asyncio
async def test_update_user_email_only(mock_db, mocker):
    """Test updating only email via Auth Admin API."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    mock_db.rpc.return_value = [SAMPLE_USER_STATS[0]]
    mock_client = _mock_httpx_client(mocker, "put", 200)

    service = AdminService(mock_db)
    await service.update_user(user_id="user-1", email="new@example.com")

    call_args = mock_client.put.call_args
    body = call_args.kwargs["json"]
    assert body["email"] == "new@example.com"
    assert "password" not in body


@pytest.mark.asyncio
async def test_update_user_not_found(mock_db, mocker):
    """Test updating nonexistent user raises 404."""
    mock_db.query.return_value = []

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_user(user_id="nonexistent", full_name="Test")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_user_invalid_status(mock_db, mocker):
    """Test updating with invalid status raises 400."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_user(user_id="user-1", account_status="premium")

    assert exc_info.value.status_code == 400
    assert "Invalid account status" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_user_duplicate_email(mock_db, mocker):
    """Test updating to an existing email raises 400."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    _mock_httpx_client(mocker, "put", 422)

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_user(user_id="user-1", email="taken@example.com")

    assert exc_info.value.status_code == 400
    assert "already in use" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_user_auth_api_error(mock_db, mocker):
    """Test Auth API error during update raises 500."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    _mock_httpx_client(mocker, "put", 500, text="Server error")

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_user(user_id="user-1", email="err@example.com")

    assert exc_info.value.status_code == 500
    assert "Failed to update user auth" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_user_with_trial_ends_at(mock_db, mocker):
    """Test updating trial_ends_at."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    trial_end = datetime(2026, 6, 15, tzinfo=timezone.utc)
    mock_db.rpc.return_value = [SAMPLE_USER_STATS[0]]

    service = AdminService(mock_db)
    await service.update_user(
        user_id="user-1",
        account_status="trial",
        trial_ends_at=trial_end,
    )

    update_data = mock_db.update.call_args.kwargs["data"]
    assert update_data["trial_ends_at"] == trial_end.isoformat()
    assert update_data["account_status"] == "trial"


# --- toggle_user ---

@pytest.mark.asyncio
async def test_toggle_user_disable(mock_db, mocker):
    """Test disabling an active user."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "paid"}]
    mock_client = _mock_httpx_client(mocker, "put", 200)

    service = AdminService(mock_db)
    result = await service.toggle_user("user-1")

    assert result["new_status"] == "admin_disabled"
    assert result["user_id"] == "user-1"

    # Verify ban was set
    call_args = mock_client.put.call_args
    assert call_args.kwargs["json"]["ban_duration"] == "876000h"

    # Verify profile update saved previous status
    update_data = mock_db.update.call_args.kwargs["data"]
    assert update_data["account_status"] == "admin_disabled"
    assert update_data["previous_status"] == "paid"


@pytest.mark.asyncio
async def test_toggle_user_enable(mock_db, mocker):
    """Test re-enabling a disabled user."""
    mock_db.query.return_value = [
        {"id": "user-1", "account_status": "admin_disabled", "previous_status": "trial"}
    ]
    mock_client = _mock_httpx_client(mocker, "put", 200)

    service = AdminService(mock_db)
    result = await service.toggle_user("user-1")

    assert result["new_status"] == "trial"
    assert result["user_id"] == "user-1"

    # Verify unban
    call_args = mock_client.put.call_args
    assert call_args.kwargs["json"]["ban_duration"] == "none"

    # Verify profile restored
    update_data = mock_db.update.call_args.kwargs["data"]
    assert update_data["account_status"] == "trial"
    assert update_data["previous_status"] is None


@pytest.mark.asyncio
async def test_toggle_user_enable_defaults_to_trial(mock_db, mocker):
    """Test re-enabling defaults to trial when no previous_status."""
    mock_db.query.return_value = [
        {"id": "user-1", "account_status": "admin_disabled"}
    ]
    _mock_httpx_client(mocker, "put", 200)

    service = AdminService(mock_db)
    result = await service.toggle_user("user-1")

    assert result["new_status"] == "trial"


@pytest.mark.asyncio
async def test_toggle_user_not_found(mock_db, mocker):
    """Test toggling a nonexistent user raises 404."""
    mock_db.query.return_value = []

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.toggle_user("nonexistent")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_toggle_user_ban_api_error(mock_db, mocker):
    """Test Auth API error during ban raises 500."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "paid"}]
    _mock_httpx_client(mocker, "put", 500, text="Server error")

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.toggle_user("user-1")

    assert exc_info.value.status_code == 500
    assert "Failed to ban user" in exc_info.value.detail


@pytest.mark.asyncio
async def test_toggle_user_unban_api_error(mock_db, mocker):
    """Test Auth API error during unban raises 500."""
    mock_db.query.return_value = [
        {"id": "user-1", "account_status": "admin_disabled", "previous_status": "paid"}
    ]
    _mock_httpx_client(mocker, "put", 500, text="Server error")

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.toggle_user("user-1")

    assert exc_info.value.status_code == 500
    assert "Failed to unban user" in exc_info.value.detail


# --- list_error_logs ---

@pytest.mark.asyncio
async def test_list_error_logs(mock_db, mocker):
    """Test listing error logs with pagination."""
    sample_error = {
        "id": "log-1",
        "created_at": "2026-02-25T00:00:00Z",
        "endpoint": "/api/test",
        "http_method": "GET",
        "status_code": 500,
        "error_message": "Test error",
        "source": "unhandled",
    }

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = [sample_error]
    mock_response.raise_for_status = mocker.MagicMock()

    mock_count_response = mocker.MagicMock()
    mock_count_response.json.return_value = []
    mock_count_response.headers = {"content-range": "0-0/1"}
    mock_count_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.get = mocker.AsyncMock(side_effect=[mock_response, mock_count_response])
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    result = await service.list_error_logs(page=1, per_page=25)

    assert len(result["errors"]) == 1
    assert result["errors"][0]["endpoint"] == "/api/test"
    assert result["total"] == 1
    assert result["page"] == 1
    assert result["per_page"] == 25


@pytest.mark.asyncio
async def test_list_error_logs_empty(mock_db, mocker):
    """Test listing error logs returns empty list when none exist."""
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = mocker.MagicMock()

    mock_count_response = mocker.MagicMock()
    mock_count_response.json.return_value = []
    mock_count_response.headers = {"content-range": "0-0/0"}
    mock_count_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.get = mocker.AsyncMock(side_effect=[mock_response, mock_count_response])
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    result = await service.list_error_logs()

    assert result["errors"] == []
    assert result["total"] == 0


@pytest.mark.asyncio
async def test_list_error_logs_with_search_filter(mock_db, mocker):
    """Test listing error logs with search filter passes ilike param."""
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = mocker.MagicMock()

    mock_count_response = mocker.MagicMock()
    mock_count_response.json.return_value = []
    mock_count_response.headers = {"content-range": "0-0/0"}
    mock_count_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.get = mocker.AsyncMock(side_effect=[mock_response, mock_count_response])
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    await service.list_error_logs(search="connection", source="unhandled", resolved=False)

    # Verify the GET call included filter params
    call_args = mock_client.get.call_args_list[0]
    params = call_args.kwargs.get("params", call_args[1].get("params", {}))
    assert params["error_message"] == "ilike.*connection*"
    assert params["source"] == "eq.unhandled"
    assert params["is_resolved"] == "eq.false"


@pytest.mark.asyncio
async def test_list_error_logs_ignores_invalid_source(mock_db, mocker):
    """Test listing error logs ignores an invalid source filter."""
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = mocker.MagicMock()

    mock_count_response = mocker.MagicMock()
    mock_count_response.json.return_value = []
    mock_count_response.headers = {"content-range": "0-0/0"}
    mock_count_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.get = mocker.AsyncMock(side_effect=[mock_response, mock_count_response])
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    await service.list_error_logs(source="invalid_source")

    call_args = mock_client.get.call_args_list[0]
    params = call_args.kwargs.get("params", call_args[1].get("params", {}))
    assert "source" not in params


# --- resolve/unresolve errors ---

@pytest.mark.asyncio
async def test_resolve_error(mock_db, mocker):
    """Test resolving an error log."""
    resolved_error = {
        "id": "log-1",
        "error_message": "Test error",
        "is_resolved": True,
        "resolved_by": "admin@example.com",
        "notes": "Fixed in deploy",
    }

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = [resolved_error]
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.patch = mocker.AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    result = await service.resolve_error("log-1", "admin@example.com", "Fixed in deploy")

    assert result["is_resolved"] is True
    assert result["resolved_by"] == "admin@example.com"
    assert result["notes"] == "Fixed in deploy"

    call_args = mock_client.patch.call_args
    assert call_args.kwargs["params"]["id"] == "eq.log-1"
    body = call_args.kwargs["json"]
    assert body["is_resolved"] is True
    assert body["resolved_by"] == "admin@example.com"


@pytest.mark.asyncio
async def test_resolve_error_not_found(mock_db, mocker):
    """Test resolving a nonexistent error returns None."""
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.patch = mocker.AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    result = await service.resolve_error("nonexistent", "admin@example.com")

    assert result is None


@pytest.mark.asyncio
async def test_unresolve_error(mock_db, mocker):
    """Test unresolving an error log."""
    unresolved_error = {
        "id": "log-1",
        "error_message": "Test error",
        "is_resolved": False,
        "resolved_at": None,
        "resolved_by": None,
        "notes": None,
    }

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = [unresolved_error]
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.patch = mocker.AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    result = await service.unresolve_error("log-1")

    assert result["is_resolved"] is False
    assert result["resolved_by"] is None
    assert result["notes"] is None

    call_args = mock_client.patch.call_args
    body = call_args.kwargs["json"]
    assert body["is_resolved"] is False
    assert body["resolved_at"] is None


@pytest.mark.asyncio
async def test_unresolve_error_not_found(mock_db, mocker):
    """Test unresolving a nonexistent error returns None."""
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.patch = mocker.AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    result = await service.unresolve_error("nonexistent")

    assert result is None
