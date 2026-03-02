"""Integration tests for treatment endpoints."""
import pytest
from datetime import datetime


def test_create_treatment_session_unauthorized(client):
    """Test creating session without authentication."""
    response = client.post("/api/treatments/sessions", json={
        "treatment_type": "word_finding",
        "data": {}
    })
    assert response.status_code == 401


def test_create_treatment_session_success(app, client, mock_user_id, mock_db):
    """Test creating a treatment session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    # Override dependencies
    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # Mock DB response
    mock_db.insert.return_value = {
        "id": "session-123",
        "user_id": mock_user_id,
        "treatment_type": "word_finding",
        "data": {},
        "started_at": datetime.utcnow().isoformat()
    }

    response = client.post(
        "/api/treatments/sessions",
        json={"treatment_type": "word_finding", "data": {}},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "session-123"
    assert data["treatment_type"] == "word_finding"


def test_get_user_sessions_unauthorized(client):
    """Test getting sessions without authentication."""
    response = client.get("/api/treatments/sessions")
    assert response.status_code == 401


def test_get_user_sessions_success(app, client, mock_user_id, mock_db):
    """Test getting user sessions successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # Mock DB response
    mock_db.query.return_value = [
        {"id": "session-1", "user_id": mock_user_id, "treatment_type": "word_finding"},
        {"id": "session-2", "user_id": mock_user_id, "treatment_type": "word_finding"}
    ]

    response = client.get(
        "/api/treatments/sessions",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "session-1"


def test_get_user_sessions_with_filter(app, client, mock_user_id, mock_db):
    """Test getting sessions with treatment type filter."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [
        {"id": "session-1", "treatment_type": "word_finding"}
    ]

    response = client.get(
        "/api/treatments/sessions?treatment_type=word_finding",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_session_by_id_unauthorized(client):
    """Test getting specific session without authentication."""
    response = client.get("/api/treatments/sessions/session-123")
    assert response.status_code == 401


def test_get_session_by_id_success(app, client, mock_user_id, mock_db):
    """Test getting specific session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "id": "session-123",
        "user_id": mock_user_id,
        "treatment_type": "word_finding"
    }]

    response = client.get(
        "/api/treatments/sessions/session-123",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "session-123"


def test_get_session_by_id_not_found(app, client, mock_user_id, mock_db):
    """Test getting non-existent session."""
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
        "/api/treatments/sessions/nonexistent",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


def test_update_session_success(app, client, mock_user_id, mock_db):
    """Test updating a session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.update.return_value = {
        "id": "session-123",
        "completed_at": datetime.utcnow().isoformat(),
        "data": {"result": "completed"}
    }

    response = client.patch(
        "/api/treatments/sessions/session-123",
        json={"data": {"result": "completed"}},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["completed_at"] is not None



