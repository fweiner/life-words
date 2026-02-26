"""Unit tests for admin service."""
import pytest
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
    },
]


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


@pytest.mark.asyncio
async def test_delete_user_success(mock_db, mocker):
    """Test successful user deletion."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.delete.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    await service.delete_user("user-1")

    mock_client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_204_success(mock_db, mocker):
    """Test successful user deletion with 204 No Content response."""
    mock_response = MagicMock()
    mock_response.status_code = 204

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.delete.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    await service.delete_user("user-1")

    mock_client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_not_found(mock_db, mocker):
    """Test deleting a nonexistent user raises 404."""
    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.delete.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_user("nonexistent-user")

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_user_api_error(mock_db, mocker):
    """Test API error during deletion raises 500."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.delete.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_user("user-1")

    assert exc_info.value.status_code == 500
    assert "Failed to delete user" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_account_status_to_paid(mock_db):
    """Test setting account status to paid clears trial_ends_at."""
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    mock_db.update.return_value = {"account_status": "paid", "trial_ends_at": None}

    service = AdminService(mock_db)
    result = await service.update_account_status("user-1", "paid")

    assert result["account_status"] == "paid"
    assert result["trial_ends_at"] is None
    mock_db.update.assert_called_once_with(
        "profiles",
        filters={"id": "user-1"},
        data={"account_status": "paid", "trial_ends_at": None},
    )


@pytest.mark.asyncio
async def test_update_account_status_to_trial(mock_db):
    """Test setting account status to trial with end date."""
    from datetime import datetime, timezone

    trial_end = datetime(2026, 3, 15, tzinfo=timezone.utc)
    mock_db.query.return_value = [{"id": "user-1", "account_status": "paid"}]
    mock_db.update.return_value = {
        "account_status": "trial",
        "trial_ends_at": trial_end.isoformat(),
    }

    service = AdminService(mock_db)
    result = await service.update_account_status("user-1", "trial", trial_end)

    assert result["account_status"] == "trial"
    mock_db.update.assert_called_once_with(
        "profiles",
        filters={"id": "user-1"},
        data={"account_status": "trial", "trial_ends_at": trial_end.isoformat()},
    )


@pytest.mark.asyncio
async def test_update_account_status_invalid(mock_db):
    """Test rejecting an invalid account status."""
    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_account_status("user-1", "premium")

    assert exc_info.value.status_code == 400
    assert "Invalid account status" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_account_status_trial_without_end_date(mock_db):
    """Test trial status requires trial_ends_at."""
    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_account_status("user-1", "trial")

    assert exc_info.value.status_code == 400
    assert "trial_ends_at is required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_account_status_user_not_found(mock_db):
    """Test updating status for nonexistent user raises 404."""
    mock_db.query.return_value = []

    service = AdminService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_account_status("nonexistent", "paid")

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail


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
