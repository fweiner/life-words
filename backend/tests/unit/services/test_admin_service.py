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
