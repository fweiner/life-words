"""Integration tests for results endpoints."""


def test_get_my_results_unauthorized(client):
    """Test getting own results without authentication."""
    response = client.get("/api/results/my-results")
    assert response.status_code == 401


def test_get_my_results_success(app, client, mock_user_id, mock_db):
    """Test getting own results successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [
        {"id": "result-1", "score": 85},
        {"id": "result-2", "score": 90}
    ]

    response = client.get(
        "/api/results/my-results",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_my_results_with_limit(app, client, mock_user_id, mock_db):
    """Test getting own results with limit parameter."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "result-1"}]

    response = client.get(
        "/api/results/my-results?limit=10",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200


def test_get_my_progress_unauthorized(client):
    """Test getting own progress without authentication."""
    response = client.get("/api/results/my-progress")
    assert response.status_code == 401


def test_get_my_progress_success(app, client, mock_user_id, mock_db):
    """Test getting own progress successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "id": "progress-1",
        "treatment_type": "word_finding",
        "total_sessions": 20,
        "average_score": 88.0
    }]

    response = client.get(
        "/api/results/my-progress",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["total_sessions"] == 20


def test_get_my_progress_with_filter(app, client, mock_user_id, mock_db):
    """Test getting own progress with treatment type filter."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "treatment_type": "word_finding",
        "total_sessions": 10
    }]

    response = client.get(
        "/api/results/my-progress?treatment_type=word_finding",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["treatment_type"] == "word_finding"
