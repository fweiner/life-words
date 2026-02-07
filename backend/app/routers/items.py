"""Personal Items (My Stuff) endpoints for Life Words."""
from typing import List, Dict, Any
from fastapi import APIRouter
from app.core.dependencies import CurrentUserId, Database
from app.models.items import (
    PersonalItemCreate,
    PersonalItemUpdate,
    PersonalItemResponse,
    QuickAddItemCreate,
)
from app.services.items_service import ItemsService

router = APIRouter()


@router.post("")
async def create_personal_item(
    item_data: PersonalItemCreate, user_id: CurrentUserId, db: Database
) -> PersonalItemResponse:
    """Create a new personal item."""
    service = ItemsService(db)
    item = await service.create_item(user_id, item_data)
    return PersonalItemResponse(**item)


@router.post("/quick-add")
async def quick_add_item(
    data: QuickAddItemCreate, user_id: CurrentUserId, db: Database
) -> PersonalItemResponse:
    """Quick add an item with just a photo - creates an incomplete draft entry."""
    service = ItemsService(db)
    item = await service.quick_add_item(user_id, data)
    return PersonalItemResponse(**item)


@router.get("")
async def list_personal_items(
    user_id: CurrentUserId, db: Database, include_inactive: bool = False
) -> List[PersonalItemResponse]:
    """List user's personal items."""
    service = ItemsService(db)
    items = await service.list_items(user_id, include_inactive)
    return [PersonalItemResponse(**i) for i in items]


@router.get("/{item_id}")
async def get_personal_item(
    item_id: str, user_id: CurrentUserId, db: Database
) -> PersonalItemResponse:
    """Get a specific personal item."""
    service = ItemsService(db)
    item = await service.get_item(item_id, user_id)
    return PersonalItemResponse(**item)


@router.put("/{item_id}")
async def update_personal_item(
    item_id: str, item_data: PersonalItemUpdate, user_id: CurrentUserId, db: Database
) -> PersonalItemResponse:
    """Update a personal item."""
    service = ItemsService(db)
    updated = await service.update_item(item_id, user_id, item_data)
    return PersonalItemResponse(**updated)


@router.delete("/{item_id}")
async def delete_personal_item(
    item_id: str, user_id: CurrentUserId, db: Database
) -> Dict[str, Any]:
    """Soft delete a personal item (set is_active=false)."""
    service = ItemsService(db)
    return await service.delete_item(item_id, user_id)
