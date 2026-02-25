"""Integration tests for admin endpoints."""
from datetime import datetime, timezone
from unittest.mock import MagicMock
from fastapi import HTTPException


SAMPLE_ADMIN_USER = {
    "id": "admin-user-123",
    "email": "weiner@parrotsoftware.com",
    "role": "authenticated",
}

SAMPLE_USER_STATS = [
    {
        "id": "user-1",
        "email": "user1@example.com",
        "full_name": "User One",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "contact_count": 5,
        "item_count": 3,
        "session_count": 10,
        "last_active_at": datetime.now(timezone.utc).isoformat(),
    },
]


def test_list_users_unauthorized(client):
    """Test that listing users requires authentication."""
    response = client.get("/api/admin/users")
    assert response.status_code == 401


def test_list_users_non_admin(app, client, mock_db):
    """Test that non-admin users get 403."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        raise HTTPException(status_code=403, detail="Admin access required")

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    response = client.get(
        "/api/admin/users",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 403


def test_list_users_success(app, client, mock_db):
    """Test admin can list users successfully."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    mock_db.rpc.return_value = SAMPLE_USER_STATS

    response = client.get(
        "/api/admin/users",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "user1@example.com"
    assert data[0]["contact_count"] == 5


def test_delete_user_unauthorized(client):
    """Test that deleting a user requires authentication."""
    response = client.delete("/api/admin/users/some-user-id")
    assert response.status_code == 401


def test_delete_user_success(app, client, mock_db, mocker):
    """Test admin can delete a user successfully."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.delete.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.delete(
        "/api/admin/users/user-1",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["deleted_user_id"] == "user-1"


def test_delete_user_not_found(app, client, mock_db, mocker):
    """Test deleting a nonexistent user returns 404."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.delete.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.delete(
        "/api/admin/users/nonexistent",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404


def test_update_account_status_success(app, client, mock_db):
    """Test admin can update a user's account status."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    mock_db.update.return_value = {"account_status": "paid", "trial_ends_at": None}

    response = client.patch(
        "/api/admin/users/user-1/account-status",
        json={"account_status": "paid"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["account_status"] == "paid"
    assert data["trial_ends_at"] is None


def test_update_account_status_unauthorized(client):
    """Test updating account status requires authentication."""
    response = client.patch(
        "/api/admin/users/user-1/account-status",
        json={"account_status": "paid"},
    )
    assert response.status_code == 401


def test_list_error_logs_success(app, client, mock_db):
    """Test admin can list error logs."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [
        {
            "id": "log-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": "/api/test",
            "method": "GET",
            "status_code": 500,
            "error_message": "Test error",
            "traceback": None,
            "user_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ]

    response = client.get(
        "/api/admin/error-logs",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["endpoint"] == "/api/test"


def test_list_error_logs_unauthorized(client):
    """Test listing error logs requires authentication."""
    response = client.get("/api/admin/error-logs")
    assert response.status_code == 401
