"""Integration tests for auth endpoints."""
import pytest


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_current_user_success(app, client, mock_user):
    """Test getting current user with valid token."""
    from app.core.auth import get_current_user

    # Override the dependency
    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_user["id"]
    assert data["email"] == mock_user["email"]
    assert data["role"] == mock_user["role"]


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


def test_logout_unauthorized(client):
    """Test logout endpoint without authentication."""
    response = client.post("/api/auth/logout")
    assert response.status_code == 401


def test_logout(app, client, mock_user):
    """Test logout endpoint."""
    from app.core.auth import get_current_user

    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "logged out" in data["message"].lower()
