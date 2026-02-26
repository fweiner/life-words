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
        "account_status": "trial",
        "trial_ends_at": "2026-06-01T00:00:00+00:00",
        "stripe_customer_id": None,
        "subscription_plan": None,
        "subscription_current_period_end": None,
    },
]


def _setup_admin_overrides(app, mock_db):
    """Helper to set up admin dependency overrides."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db


# --- List Users ---

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
    _setup_admin_overrides(app, mock_db)
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


# --- Delete User ---

def test_delete_user_unauthorized(client):
    """Test that deleting a user requires authentication."""
    response = client.delete("/api/admin/users/some-user-id")
    assert response.status_code == 401


def test_delete_user_success(app, client, mock_db, mocker):
    """Test admin can delete a user successfully."""
    _setup_admin_overrides(app, mock_db)

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
    _setup_admin_overrides(app, mock_db)

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


# --- Create User ---

def test_create_user_unauthorized(client):
    """Test that creating a user requires authentication."""
    response = client.post("/api/admin/users", json={
        "email": "new@example.com",
        "password": "password123",
    })
    assert response.status_code == 401


def test_create_user_success(app, client, mock_db, mocker):
    """Test admin can create a user successfully."""
    _setup_admin_overrides(app, mock_db)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "new-user-1"}

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.post.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.post(
        "/api/admin/users",
        json={
            "email": "new@example.com",
            "password": "password123",
            "full_name": "New User",
            "account_status": "trial",
            "trial_days": 30,
        },
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user_id"] == "new-user-1"


def test_create_user_duplicate_email(app, client, mock_db, mocker):
    """Test creating user with existing email returns 400."""
    _setup_admin_overrides(app, mock_db)

    mock_response = MagicMock()
    mock_response.status_code = 422

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.post.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.post(
        "/api/admin/users",
        json={
            "email": "existing@example.com",
            "password": "password123",
        },
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 400


# --- Update User ---

def test_update_user_unauthorized(client):
    """Test that updating a user requires authentication."""
    response = client.put("/api/admin/users/user-1", json={"full_name": "Test"})
    assert response.status_code == 401


def test_update_user_success(app, client, mock_db, mocker):
    """Test admin can update a user successfully."""
    _setup_admin_overrides(app, mock_db)
    mock_db.query.return_value = [{"id": "user-1", "account_status": "trial"}]
    mock_db.rpc.return_value = SAMPLE_USER_STATS

    response = client.put(
        "/api/admin/users/user-1",
        json={"full_name": "Updated Name", "account_status": "paid"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["id"] == "user-1"


def test_update_user_not_found(app, client, mock_db):
    """Test updating a nonexistent user returns 404."""
    _setup_admin_overrides(app, mock_db)
    mock_db.query.return_value = []

    response = client.put(
        "/api/admin/users/nonexistent",
        json={"full_name": "Test"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404


# --- Toggle User ---

def test_toggle_user_unauthorized(client):
    """Test that toggling a user requires authentication."""
    response = client.post("/api/admin/users/user-1/toggle")
    assert response.status_code == 401


def test_toggle_user_disable_success(app, client, mock_db, mocker):
    """Test admin can disable a user."""
    _setup_admin_overrides(app, mock_db)
    mock_db.query.return_value = [{"id": "user-1", "account_status": "paid"}]

    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.put.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.post(
        "/api/admin/users/user-1/toggle",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["new_status"] == "admin_disabled"
    assert "disabled" in data["message"]


def test_toggle_user_enable_success(app, client, mock_db, mocker):
    """Test admin can re-enable a disabled user."""
    _setup_admin_overrides(app, mock_db)
    mock_db.query.return_value = [
        {"id": "user-1", "account_status": "admin_disabled", "previous_status": "paid"}
    ]

    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.put.return_value = mock_response

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.post(
        "/api/admin/users/user-1/toggle",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["new_status"] == "paid"
    assert "enabled" in data["message"]


def test_toggle_user_not_found(app, client, mock_db):
    """Test toggling a nonexistent user returns 404."""
    _setup_admin_overrides(app, mock_db)
    mock_db.query.return_value = []

    response = client.post(
        "/api/admin/users/nonexistent/toggle",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404


# --- Error Logs ---

def test_list_error_logs_success(app, client, mocker):
    """Test admin can list error logs."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    mock_db = mocker.AsyncMock()
    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    sample_error = {
        "id": "log-1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": "/api/test",
        "http_method": "GET",
        "status_code": 500,
        "error_message": "Test error",
        "error_type": "ValueError",
        "stacktrace": None,
        "request_body": None,
        "query_params": None,
        "user_id": None,
        "user_email": None,
        "source": "unhandled",
        "service_name": None,
        "function_name": None,
        "environment": "test",
        "is_resolved": False,
        "resolved_at": None,
        "resolved_by": None,
        "notes": None,
    }

    # Mock the httpx calls used by AdminService.list_error_logs
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

    response = client.get(
        "/api/admin/errors",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["errors"]) == 1
    assert data["errors"][0]["endpoint"] == "/api/test"
    assert data["total"] == 1


def test_list_error_logs_unauthorized(client):
    """Test listing error logs requires authentication."""
    response = client.get("/api/admin/errors")
    assert response.status_code == 401


def test_resolve_error_success(app, client, mocker):
    """Test admin can resolve an error."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    mock_db = mocker.AsyncMock()

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    resolved_error = {
        "id": "log-1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "error_message": "Test error",
        "error_type": "ValueError",
        "stacktrace": None,
        "endpoint": "/api/test",
        "http_method": "GET",
        "request_body": None,
        "query_params": None,
        "status_code": 500,
        "user_id": None,
        "user_email": None,
        "source": "unhandled",
        "service_name": None,
        "function_name": None,
        "environment": "test",
        "is_resolved": True,
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "resolved_by": "weiner@parrotsoftware.com",
        "notes": "Fixed it",
    }

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = [resolved_error]
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.patch = mocker.AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.post(
        "/api/admin/errors/log-1/resolve",
        json={"notes": "Fixed it"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_resolved"] is True
    assert data["resolved_by"] == "weiner@parrotsoftware.com"
    assert data["notes"] == "Fixed it"


def test_resolve_error_not_found(app, client, mocker):
    """Test resolving a nonexistent error returns 404."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    mock_db = mocker.AsyncMock()

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.patch = mocker.AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.post(
        "/api/admin/errors/nonexistent/resolve",
        json={"notes": "test"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404


def test_resolve_error_unauthorized(client):
    """Test resolving an error requires authentication."""
    response = client.post("/api/admin/errors/log-1/resolve", json={})
    assert response.status_code == 401


def test_unresolve_error_success(app, client, mocker):
    """Test admin can unresolve an error."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    mock_db = mocker.AsyncMock()

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    unresolved_error = {
        "id": "log-1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "error_message": "Test error",
        "error_type": "ValueError",
        "stacktrace": None,
        "endpoint": "/api/test",
        "http_method": "GET",
        "request_body": None,
        "query_params": None,
        "status_code": 500,
        "user_id": None,
        "user_email": None,
        "source": "unhandled",
        "service_name": None,
        "function_name": None,
        "environment": "test",
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

    response = client.post(
        "/api/admin/errors/log-1/unresolve",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_resolved"] is False


def test_unresolve_error_not_found(app, client, mocker):
    """Test unresolving a nonexistent error returns 404."""
    from app.core.auth import require_admin
    from app.core.dependencies import get_db

    async def override_require_admin():
        return SAMPLE_ADMIN_USER

    mock_db = mocker.AsyncMock()

    async def override_get_db():
        return mock_db

    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[get_db] = override_get_db

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.patch = mocker.AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)

    mocker.patch("app.services.admin_service.httpx.AsyncClient", return_value=mock_client)

    response = client.post(
        "/api/admin/errors/nonexistent/unresolve",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404


def test_unresolve_error_unauthorized(client):
    """Test unresolving an error requires authentication."""
    response = client.post("/api/admin/errors/log-1/unresolve")
    assert response.status_code == 401
