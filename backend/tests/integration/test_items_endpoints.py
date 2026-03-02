"""Integration tests for personal items (My Stuff) endpoints."""


def _setup_auth(app, mock_user_id, mock_db):
    """Helper to set up auth and db overrides."""
    from app.core.auth import get_current_user_id
    from app.core.dependencies import get_db

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db] = override_get_db


# ============== POST /api/life-words/items ==============


def test_create_item_unauthorized(client):
    """Test creating an item without authentication."""
    response = client.post("/api/life-words/items", json={"name": "Test Item", "photo_url": "https://example.com/test.jpg"})
    assert response.status_code == 401


def test_create_item_success(app, client, mock_user_id, mock_db):
    """Test creating a personal item successfully."""
    _setup_auth(app, mock_user_id, mock_db)

    mock_db.insert.return_value = [{
        "id": "item-1",
        "user_id": mock_user_id,
        "name": "My Coffee Mug",
        "category": "kitchen",
        "photo_url": "https://example.com/mug.jpg",
        "is_active": True,
        "is_complete": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }]

    response = client.post(
        "/api/life-words/items",
        json={"name": "My Coffee Mug", "photo_url": "https://example.com/mug.jpg", "category": "kitchen"},
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Coffee Mug"
    assert data["category"] == "kitchen"


# ============== POST /api/life-words/items/quick-add ==============


def test_quick_add_item_unauthorized(client):
    """Test quick-adding an item without authentication."""
    response = client.post("/api/life-words/items/quick-add", json={"photo_url": "https://example.com/photo.jpg"})
    assert response.status_code == 401


def test_quick_add_item_success(app, client, mock_user_id, mock_db):
    """Test quick-adding a personal item successfully."""
    _setup_auth(app, mock_user_id, mock_db)

    mock_db.insert.return_value = [{
        "id": "item-2",
        "user_id": mock_user_id,
        "name": "",
        "photo_url": "https://example.com/photo.jpg",
        "is_active": True,
        "is_complete": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }]

    response = client.post(
        "/api/life-words/items/quick-add",
        json={"photo_url": "https://example.com/photo.jpg"},
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["photo_url"] == "https://example.com/photo.jpg"


# ============== GET /api/life-words/items ==============


def test_list_items_unauthorized(client):
    """Test listing items without authentication."""
    response = client.get("/api/life-words/items")
    assert response.status_code == 401


def test_list_items_success(app, client, mock_user_id, mock_db):
    """Test listing personal items successfully."""
    _setup_auth(app, mock_user_id, mock_db)

    mock_db.query.return_value = [
        {
            "id": "item-1",
            "user_id": mock_user_id,
            "name": "Coffee Mug",
            "photo_url": "https://example.com/mug.jpg",
            "is_active": True,
            "is_complete": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "id": "item-2",
            "user_id": mock_user_id,
            "name": "Laptop",
            "photo_url": "https://example.com/laptop.jpg",
            "is_active": True,
            "is_complete": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
    ]

    response = client.get(
        "/api/life-words/items",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Coffee Mug"


# ============== GET /api/life-words/items/{item_id} ==============


def test_get_item_unauthorized(client):
    """Test getting an item without authentication."""
    response = client.get("/api/life-words/items/item-1")
    assert response.status_code == 401


def test_get_item_success(app, client, mock_user_id, mock_db):
    """Test getting a specific personal item."""
    _setup_auth(app, mock_user_id, mock_db)

    mock_db.query.return_value = [{
        "id": "item-1",
        "user_id": mock_user_id,
        "name": "Coffee Mug",
        "photo_url": "https://example.com/mug.jpg",
        "is_active": True,
        "is_complete": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }]

    response = client.get(
        "/api/life-words/items/item-1",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "item-1"
    assert data["name"] == "Coffee Mug"


# ============== PUT /api/life-words/items/{item_id} ==============


def test_update_item_unauthorized(client):
    """Test updating an item without authentication."""
    response = client.put("/api/life-words/items/item-1", json={"name": "Updated"})
    assert response.status_code == 401


def test_update_item_success(app, client, mock_user_id, mock_db):
    """Test updating a personal item successfully."""
    _setup_auth(app, mock_user_id, mock_db)

    # verify_ownership query
    mock_db.query.return_value = [{"id": "item-1", "user_id": mock_user_id}]
    mock_db.update.return_value = [{
        "id": "item-1",
        "user_id": mock_user_id,
        "name": "Updated Mug",
        "photo_url": "https://example.com/mug.jpg",
        "is_active": True,
        "is_complete": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }]

    response = client.put(
        "/api/life-words/items/item-1",
        json={"name": "Updated Mug", "notes": "Now it's red"},
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Mug"


# ============== DELETE /api/life-words/items/{item_id} ==============


def test_delete_item_unauthorized(client):
    """Test deleting an item without authentication."""
    response = client.delete("/api/life-words/items/item-1")
    assert response.status_code == 401


def test_delete_item_success(app, client, mock_user_id, mock_db):
    """Test soft-deleting a personal item."""
    _setup_auth(app, mock_user_id, mock_db)

    # verify_ownership query
    mock_db.query.return_value = [{"id": "item-1", "user_id": mock_user_id}]
    mock_db.update.return_value = [{"id": "item-1", "is_active": False}]

    response = client.delete(
        "/api/life-words/items/item-1",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
