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
async def test_list_error_logs(mock_db):
    """Test listing error logs queries with correct params."""
    mock_db.query.return_value = [
        {
            "id": "log-1",
            "timestamp": "2026-02-25T00:00:00Z",
            "endpoint": "/api/test",
            "method": "GET",
            "status_code": 500,
            "error_message": "Test error",
            "traceback": "Traceback ...",
            "user_id": None,
        }
    ]

    service = AdminService(mock_db)
    result = await service.list_error_logs(limit=25)

    assert len(result) == 1
    assert result[0]["endpoint"] == "/api/test"
    mock_db.query.assert_called_once_with(
        "error_logs",
        order_by="timestamp",
        order_desc=True,
        limit=25,
    )


@pytest.mark.asyncio
async def test_list_error_logs_empty(mock_db):
    """Test listing error logs returns empty list when none exist."""
    mock_db.query.return_value = []

    service = AdminService(mock_db)
    result = await service.list_error_logs()

    assert result == []
    mock_db.query.assert_called_once_with(
        "error_logs",
        order_by="timestamp",
        order_desc=True,
        limit=50,
    )
