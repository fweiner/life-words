"""Unit tests for items service."""
import pytest
from datetime import datetime, timezone
from fastapi import HTTPException


SAMPLE_ITEM = {
    "id": "item-123",
    "user_id": "user-123",
    "name": "Coffee Mug",
    "pronunciation": None,
    "photo_url": "https://example.com/mug.jpg",
    "purpose": "Drinking coffee",
    "features": "Blue ceramic",
    "category": "kitchen",
    "size": "medium",
    "shape": "cylindrical",
    "color": "blue",
    "weight": "light",
    "location": "kitchen counter",
    "associated_with": "morning routine",
    "is_active": True,
    "is_complete": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
}


@pytest.mark.asyncio
async def test_create_item(mock_db):
    """Test creating a personal item."""
    from app.services.items_service import ItemsService
    from app.models.items import PersonalItemCreate

    mock_db.insert.return_value = [SAMPLE_ITEM]

    service = ItemsService(mock_db)
    result = await service.create_item(
        "user-123",
        PersonalItemCreate(
            name="Coffee Mug",
            photo_url="https://example.com/mug.jpg",
            purpose="Drinking coffee",
            features="Blue ceramic",
            category="kitchen",
        )
    )

    assert result["name"] == "Coffee Mug"
    assert result["purpose"] == "Drinking coffee"
    mock_db.insert.assert_called_once()


@pytest.mark.asyncio
async def test_create_item_empty_strings_converted(mock_db):
    """Test that empty strings are converted to None."""
    from app.services.items_service import ItemsService
    from app.models.items import PersonalItemCreate

    mock_db.insert.return_value = [SAMPLE_ITEM]

    service = ItemsService(mock_db)
    await service.create_item(
        "user-123",
        PersonalItemCreate(
            name="Mug",
            photo_url="https://example.com/mug.jpg",
            pronunciation="",
            purpose="",
        )
    )

    call_data = mock_db.insert.call_args.args[1]
    assert call_data["pronunciation"] is None
    assert call_data["purpose"] is None


@pytest.mark.asyncio
async def test_quick_add_item(mock_db):
    """Test quick adding an item with just a photo."""
    from app.services.items_service import ItemsService
    from app.models.items import QuickAddItemCreate

    draft = {**SAMPLE_ITEM, "name": "", "is_complete": False}
    mock_db.insert.return_value = [draft]

    service = ItemsService(mock_db)
    result = await service.quick_add_item(
        "user-123",
        QuickAddItemCreate(photo_url="https://example.com/photo.jpg")
    )

    assert result["name"] == ""
    call_data = mock_db.insert.call_args.args[1]
    assert call_data["name"] == ""


@pytest.mark.asyncio
async def test_list_items(mock_db):
    """Test listing items for a user."""
    from app.services.items_service import ItemsService

    mock_db.query.return_value = [SAMPLE_ITEM, {**SAMPLE_ITEM, "id": "item-456"}]

    service = ItemsService(mock_db)
    result = await service.list_items("user-123")

    assert len(result) == 2
    call_kwargs = mock_db.query.call_args.kwargs
    assert call_kwargs["filters"]["is_active"] is True


@pytest.mark.asyncio
async def test_list_items_include_inactive(mock_db):
    """Test listing items including inactive ones."""
    from app.services.items_service import ItemsService

    mock_db.query.return_value = [SAMPLE_ITEM]

    service = ItemsService(mock_db)
    await service.list_items("user-123", include_inactive=True)

    call_kwargs = mock_db.query.call_args.kwargs
    assert "is_active" not in call_kwargs["filters"]


@pytest.mark.asyncio
async def test_list_items_empty(mock_db):
    """Test listing items when none exist."""
    from app.services.items_service import ItemsService

    mock_db.query.return_value = []

    service = ItemsService(mock_db)
    result = await service.list_items("user-123")

    assert result == []


@pytest.mark.asyncio
async def test_get_item(mock_db):
    """Test getting a specific item."""
    from app.services.items_service import ItemsService

    mock_db.query.return_value = [SAMPLE_ITEM]

    service = ItemsService(mock_db)
    result = await service.get_item("item-123", "user-123")

    assert result["id"] == "item-123"


@pytest.mark.asyncio
async def test_get_item_not_found(mock_db):
    """Test getting a non-existent item."""
    from app.services.items_service import ItemsService

    mock_db.query.return_value = []

    service = ItemsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_item("nonexistent", "user-123")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_item(mock_db):
    """Test updating an item."""
    from app.services.items_service import ItemsService
    from app.models.items import PersonalItemUpdate

    mock_db.query.return_value = [{"id": "item-123"}]
    updated = {**SAMPLE_ITEM, "name": "Tea Mug"}
    mock_db.update.return_value = updated

    service = ItemsService(mock_db)
    result = await service.update_item(
        "item-123", "user-123",
        PersonalItemUpdate(name="Tea Mug")
    )

    assert result["name"] == "Tea Mug"


@pytest.mark.asyncio
async def test_update_item_not_found(mock_db):
    """Test updating a non-existent item."""
    from app.services.items_service import ItemsService
    from app.models.items import PersonalItemUpdate

    mock_db.query.return_value = []

    service = ItemsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_item(
            "nonexistent", "user-123",
            PersonalItemUpdate(name="Tea Mug")
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_item_no_fields(mock_db):
    """Test updating an item with no fields raises error."""
    from app.services.items_service import ItemsService
    from app.models.items import PersonalItemUpdate

    mock_db.query.return_value = [{"id": "item-123"}]

    service = ItemsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_item(
            "item-123", "user-123",
            PersonalItemUpdate()
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_delete_item(mock_db):
    """Test soft deleting an item."""
    from app.services.items_service import ItemsService

    mock_db.query.return_value = [{"id": "item-123"}]

    service = ItemsService(mock_db)
    result = await service.delete_item("item-123", "user-123")

    assert result["success"] is True
    mock_db.update.assert_called_once_with(
        "personal_items",
        {"id": "item-123"},
        {"is_active": False}
    )


@pytest.mark.asyncio
async def test_delete_item_not_found(mock_db):
    """Test deleting a non-existent item."""
    from app.services.items_service import ItemsService

    mock_db.query.return_value = []

    service = ItemsService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_item("nonexistent", "user-123")

    assert exc_info.value.status_code == 404
