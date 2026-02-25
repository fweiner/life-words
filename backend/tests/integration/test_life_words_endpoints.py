"""Integration tests for Find My Life Words treatment endpoints."""
import pytest
from datetime import datetime


# ============== Status Tests ==============

def test_get_status_unauthorized(client):
    """Test getting status without authentication."""
    response = client.get("/api/life-words/status")
    assert response.status_code == 401


def test_get_status_success(app, client, mock_user_id, mock_db):
    """Test getting status successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # Mock DB response: 2 contacts + 1 item = 3 total
    mock_db.query.side_effect = [
        [{"id": "contact-1"}, {"id": "contact-2"}],  # contacts query
        [{"id": "item-1"}],  # items query
    ]

    response = client.get(
        "/api/life-words/status",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["contact_count"] == 2
    assert data["item_count"] == 1
    assert data["total_count"] == 3
    assert data["can_start_session"] is True
    assert data["min_contacts_required"] == 2


def test_get_status_not_enough_contacts(app, client, mock_user_id, mock_db):
    """Test status shows can't start session with insufficient contacts."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # Mock DB response: 1 contact + 0 items = 1 total (not enough)
    mock_db.query.side_effect = [
        [{"id": "contact-1"}],  # contacts query
        [],  # items query (empty)
    ]

    response = client.get(
        "/api/life-words/status",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["contact_count"] == 1
    assert data["item_count"] == 0
    assert data["total_count"] == 1
    assert data["can_start_session"] is False


def test_get_status_no_contacts(app, client, mock_user_id, mock_db):
    """Test status with no contacts."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # Mock DB response: no contacts, no items
    mock_db.query.side_effect = [
        None,  # contacts query
        None,  # items query
    ]

    response = client.get(
        "/api/life-words/status",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["contact_count"] == 0
    assert data["item_count"] == 0
    assert data["total_count"] == 0
    assert data["can_start_session"] is False


# ============== Contact CRUD Tests ==============

def test_create_contact_unauthorized(client):
    """Test creating contact without authentication."""
    response = client.post("/api/life-words/contacts", json={
        "name": "Barbara",
        "relationship": "spouse",
        "photo_url": "https://example.com/photo.jpg"
    })
    assert response.status_code == 401


def test_create_contact_success(app, client, mock_user_id, mock_db):
    """Test creating a contact successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.insert.return_value = [{
        "id": "contact-123",
        "user_id": mock_user_id,
        "name": "Barbara",
        "nickname": "Barb",
        "relationship": "spouse",
        "photo_url": "https://example.com/photo.jpg",
        "category": "family",
        "first_letter": "B",
        "description": "My wife of 42 years",
        "association": "Makes the best apple pie",
        "location_context": "Lives with me",
        "interests": None,
        "personality": None,
        "values": None,
        "social_behavior": None,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }]

    response = client.post(
        "/api/life-words/contacts",
        json={
            "name": "Barbara",
            "nickname": "Barb",
            "relationship": "spouse",
            "photo_url": "https://example.com/photo.jpg",
            "category": "family",
            "description": "My wife of 42 years",
            "association": "Makes the best apple pie",
            "location_context": "Lives with me"
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "contact-123"
    assert data["name"] == "Barbara"
    assert data["relationship"] == "spouse"


def test_create_contact_minimal(app, client, mock_user_id, mock_db):
    """Test creating a contact with minimal data."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.insert.return_value = [{
        "id": "contact-456",
        "user_id": mock_user_id,
        "name": "Max",
        "nickname": None,
        "relationship": "pet",
        "photo_url": "https://example.com/max.jpg",
        "category": None,
        "first_letter": "M",
        "description": None,
        "association": None,
        "location_context": None,
        "interests": None,
        "personality": None,
        "values": None,
        "social_behavior": None,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }]

    response = client.post(
        "/api/life-words/contacts",
        json={
            "name": "Max",
            "relationship": "pet",
            "photo_url": "https://example.com/max.jpg"
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Max"
    assert data["relationship"] == "pet"


def test_list_contacts_unauthorized(client):
    """Test listing contacts without authentication."""
    response = client.get("/api/life-words/contacts")
    assert response.status_code == 401


def test_list_contacts_success(app, client, mock_user_id, mock_db):
    """Test listing contacts successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [
        {
            "id": "contact-1",
            "user_id": mock_user_id,
            "name": "Barbara",
            "nickname": None,
            "relationship": "spouse",
            "photo_url": "https://example.com/barbara.jpg",
            "category": None,
            "first_letter": "B",
            "description": None,
            "association": None,
            "location_context": None,
            "interests": None,
            "personality": None,
            "values": None,
            "social_behavior": None,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "contact-2",
            "user_id": mock_user_id,
            "name": "Max",
            "nickname": None,
            "relationship": "pet",
            "photo_url": "https://example.com/max.jpg",
            "category": None,
            "first_letter": "M",
            "description": None,
            "association": None,
            "location_context": None,
            "interests": None,
            "personality": None,
            "values": None,
            "social_behavior": None,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]

    response = client.get(
        "/api/life-words/contacts",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Barbara"
    assert data[1]["name"] == "Max"


def test_list_contacts_empty(app, client, mock_user_id, mock_db):
    """Test listing contacts when none exist."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = None

    response = client.get(
        "/api/life-words/contacts",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_contact_unauthorized(client):
    """Test getting a single contact without authentication."""
    response = client.get("/api/life-words/contacts/contact-123")
    assert response.status_code == 401


def test_get_contact_success(app, client, mock_user_id, mock_db):
    """Test getting a single contact successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{
        "id": "contact-123",
        "user_id": mock_user_id,
        "name": "Barbara",
        "nickname": "Barb",
        "relationship": "spouse",
        "photo_url": "https://example.com/barbara.jpg",
        "category": "family",
        "first_letter": "B",
        "description": "My wife",
        "association": None,
        "location_context": None,
        "interests": None,
        "personality": None,
        "values": None,
        "social_behavior": None,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }]

    response = client.get(
        "/api/life-words/contacts/contact-123",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "contact-123"
    assert data["name"] == "Barbara"


def test_get_contact_not_found(app, client, mock_user_id, mock_db):
    """Test getting a non-existent contact."""
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
        "/api/life-words/contacts/nonexistent",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


def test_update_contact_unauthorized(client):
    """Test updating a contact without authentication."""
    response = client.put("/api/life-words/contacts/contact-123", json={
        "name": "Barbara Updated"
    })
    assert response.status_code == 401


def test_update_contact_success(app, client, mock_user_id, mock_db):
    """Test updating a contact successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # First query verifies ownership
    mock_db.query.return_value = [{"id": "contact-123"}]

    mock_db.update.return_value = [{
        "id": "contact-123",
        "user_id": mock_user_id,
        "name": "Barbara Updated",
        "nickname": "Barb",
        "relationship": "spouse",
        "photo_url": "https://example.com/barbara.jpg",
        "category": "family",
        "first_letter": "B",
        "description": "My wife",
        "association": None,
        "location_context": None,
        "interests": None,
        "personality": None,
        "values": None,
        "social_behavior": None,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }]

    response = client.put(
        "/api/life-words/contacts/contact-123",
        json={"name": "Barbara Updated"},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Barbara Updated"


def test_update_contact_not_found(app, client, mock_user_id, mock_db):
    """Test updating a non-existent contact."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.put(
        "/api/life-words/contacts/nonexistent",
        json={"name": "Updated"},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


def test_update_contact_no_fields(app, client, mock_user_id, mock_db):
    """Test updating a contact with no fields to update."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "contact-123"}]

    response = client.put(
        "/api/life-words/contacts/contact-123",
        json={},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 400
    assert "No fields to update" in response.json()["detail"]


def test_delete_contact_unauthorized(client):
    """Test deleting a contact without authentication."""
    response = client.delete("/api/life-words/contacts/contact-123")
    assert response.status_code == 401


def test_delete_contact_success(app, client, mock_user_id, mock_db):
    """Test soft-deleting a contact successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = [{"id": "contact-123"}]
    mock_db.update.return_value = [{"id": "contact-123", "is_active": False}]

    response = client.delete(
        "/api/life-words/contacts/contact-123",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "deactivated" in data["message"]


def test_delete_contact_not_found(app, client, mock_user_id, mock_db):
    """Test deleting a non-existent contact."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.delete(
        "/api/life-words/contacts/nonexistent",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


# ============== Session Tests ==============

def test_create_session_unauthorized(client):
    """Test creating a session without authentication."""
    response = client.post("/api/life-words/sessions", json={})
    assert response.status_code == 401


def test_create_session_success(app, client, mock_user_id, mock_db):
    """Test creating a session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    contacts = [
        {"id": "contact-1", "name": "Barbara", "relationship": "spouse", "photo_url": "url1"},
        {"id": "contact-2", "name": "Max", "relationship": "pet", "photo_url": "url2"}
    ]
    # First query is for contacts, second is for items (empty)
    mock_db.query.side_effect = [contacts, []]
    mock_db.insert.return_value = [{
        "id": "session-123",
        "user_id": mock_user_id,
        "contact_ids": ["contact-1", "contact-2"],
        "is_completed": False,
        "started_at": datetime.utcnow().isoformat()
    }]

    response = client.post(
        "/api/life-words/sessions",
        json={},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session"]["id"] == "session-123"
    assert len(data["contacts"]) == 2


def test_create_session_with_specific_contacts(app, client, mock_user_id, mock_db):
    """Test creating a session with specific contact IDs."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    contacts = [
        {"id": "contact-1", "name": "Barbara", "relationship": "spouse", "photo_url": "url1"},
        {"id": "contact-2", "name": "Max", "relationship": "pet", "photo_url": "url2"},
        {"id": "contact-3", "name": "John", "relationship": "friend", "photo_url": "url3"}
    ]
    # First query is for contacts, second is for items (empty)
    mock_db.query.side_effect = [contacts, []]
    mock_db.insert.return_value = [{
        "id": "session-456",
        "user_id": mock_user_id,
        "contact_ids": ["contact-1", "contact-2"],
        "is_completed": False,
        "started_at": datetime.utcnow().isoformat()
    }]

    response = client.post(
        "/api/life-words/sessions",
        json={"contact_ids": ["contact-1", "contact-2"]},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session"]["id"] == "session-456"


def test_create_session_insufficient_contacts(app, client, mock_user_id, mock_db):
    """Test creating a session with insufficient contacts."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # First query is for contacts (1 contact), second is for items (empty)
    mock_db.query.side_effect = [[{"id": "contact-1", "name": "Barbara"}], []]

    response = client.post(
        "/api/life-words/sessions",
        json={},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 400
    assert "At least 2" in response.json()["detail"]


def test_create_session_no_contacts(app, client, mock_user_id, mock_db):
    """Test creating a session with no contacts."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    # First query is for contacts (empty), second is for items (empty)
    mock_db.query.side_effect = [[], []]

    response = client.post(
        "/api/life-words/sessions",
        json={},
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 400


def test_get_session_unauthorized(client):
    """Test getting a session without authentication."""
    response = client.get("/api/life-words/sessions/session-123")
    assert response.status_code == 401


def test_get_session_success(app, client, mock_user_id, mock_db):
    """Test getting a session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    def mock_query(table, select=None, filters=None, order=None):
        if table == "life_words_sessions":
            return [{
                "id": "session-123",
                "user_id": mock_user_id,
                "contact_ids": ["contact-1", "contact-2"],
                "is_completed": False
            }]
        elif table == "personal_contacts":
            return [
                {"id": "contact-1", "name": "Barbara"},
                {"id": "contact-2", "name": "Max"}
            ]
        elif table == "life_words_responses":
            return []
        return []

    mock_db.query.side_effect = mock_query

    response = client.get(
        "/api/life-words/sessions/session-123",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session"]["id"] == "session-123"
    assert len(data["contacts"]) == 2
    assert data["responses"] == []


def test_get_session_not_found(app, client, mock_user_id, mock_db):
    """Test getting a non-existent session."""
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
        "/api/life-words/sessions/nonexistent",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


def test_save_response_unauthorized(client):
    """Test saving a response without authentication."""
    response = client.post("/api/life-words/sessions/session-123/responses", json={
        "contact_id": "contact-1",
        "is_correct": True,
        "cues_used": 0,
        "correct_answer": "Barbara"
    })
    assert response.status_code == 401


def test_save_response_success(app, client, mock_user_id, mock_db):
    """Test saving a response successfully."""
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
        "user_id": mock_user_id
    }]
    mock_db.insert.return_value = [{
        "id": "response-123",
        "session_id": "session-123",
        "contact_id": "contact-1",
        "user_id": mock_user_id,
        "is_correct": True,
        "cues_used": 2,
        "response_time": 5.5,
        "user_answer": "Barbara",
        "correct_answer": "Barbara",
        "speech_confidence": 0.95
    }]

    response = client.post(
        "/api/life-words/sessions/session-123/responses",
        json={
            "contact_id": "contact-1",
            "is_correct": True,
            "cues_used": 2,
            "response_time": 5.5,
            "user_answer": "Barbara",
            "correct_answer": "Barbara",
            "speech_confidence": 0.95
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["response"]["id"] == "response-123"
    assert data["response"]["is_correct"] is True


def test_save_response_session_not_found(app, client, mock_user_id, mock_db):
    """Test saving a response for non-existent session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.post(
        "/api/life-words/sessions/nonexistent/responses",
        json={
            "contact_id": "contact-1",
            "is_correct": True,
            "cues_used": 0,
            "correct_answer": "Barbara"
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


def test_complete_session_unauthorized(client):
    """Test completing a session without authentication."""
    response = client.put("/api/life-words/sessions/session-123/complete")
    assert response.status_code == 401


def test_complete_session_success(app, client, mock_user_id, mock_db):
    """Test completing a session successfully."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    def mock_query(table, select=None, filters=None, order=None):
        if table == "life_words_sessions":
            return [{"id": "session-123", "user_id": mock_user_id}]
        elif table == "life_words_responses":
            return [
                {"id": "r1", "contact_id": "c1", "is_correct": True, "cues_used": 0, "response_time": 3.5},
                {"id": "r2", "contact_id": "c2", "is_correct": False, "cues_used": 3, "response_time": 15.0}
            ]
        return []

    mock_db.query.side_effect = mock_query
    mock_db.update.return_value = [{
        "id": "session-123",
        "is_completed": True,
        "total_correct": 1,
        "total_incorrect": 1,
        "average_cues_used": 1.5,
        "average_response_time": 9.25
    }]

    response = client.put(
        "/api/life-words/sessions/session-123/complete",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session"][0]["is_completed"] is True


def test_complete_session_not_found(app, client, mock_user_id, mock_db):
    """Test completing a non-existent session."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    mock_db.query.return_value = []

    response = client.put(
        "/api/life-words/sessions/nonexistent/complete",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 404


def test_complete_session_no_responses(app, client, mock_user_id, mock_db):
    """Test completing a session with no responses."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db

    def mock_query(table, select=None, filters=None, order=None):
        if table == "life_words_sessions":
            return [{"id": "session-123", "user_id": mock_user_id}]
        elif table == "life_words_responses":
            return []
        return []

    mock_db.query.side_effect = mock_query

    response = client.put(
        "/api/life-words/sessions/session-123/complete",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 400
    assert "No responses found" in response.json()["detail"]
