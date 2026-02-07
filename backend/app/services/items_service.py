"""Items service for managing personal items (My Stuff)."""
from typing import List, Dict, Any
from app.core.database import SupabaseClient
from app.models.items import PersonalItemCreate, PersonalItemUpdate, QuickAddItemCreate
from app.services.utils import (
    empty_to_none,
    verify_ownership,
    build_update_data,
    soft_delete_entity,
    list_user_entities,
)

TABLE = "personal_items"


class ItemsService:
    """Service for personal item operations."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def create_item(
        self, user_id: str, item_data: PersonalItemCreate
    ) -> Dict[str, Any]:
        """Create a new personal item."""
        item = await self.db.insert(
            TABLE,
            {
                "user_id": user_id,
                "name": item_data.name,
                "pronunciation": empty_to_none(item_data.pronunciation),
                "photo_url": item_data.photo_url,
                "purpose": empty_to_none(item_data.purpose),
                "features": empty_to_none(item_data.features),
                "category": empty_to_none(item_data.category),
                "size": empty_to_none(item_data.size),
                "shape": empty_to_none(item_data.shape),
                "color": empty_to_none(item_data.color),
                "weight": empty_to_none(item_data.weight),
                "location": empty_to_none(item_data.location),
                "associated_with": empty_to_none(item_data.associated_with),
            }
        )
        return item[0]

    async def quick_add_item(
        self, user_id: str, data: QuickAddItemCreate
    ) -> Dict[str, Any]:
        """Quick add an item with just a photo - creates an incomplete draft entry."""
        item = await self.db.insert(
            TABLE,
            {
                "user_id": user_id,
                "name": "",  # Empty triggers is_complete = FALSE
                "photo_url": data.photo_url,
            }
        )
        return item[0]

    async def list_items(
        self, user_id: str, include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """List user's personal items."""
        return await list_user_entities(self.db, TABLE, user_id, include_inactive)

    async def get_item(self, item_id: str, user_id: str) -> Dict[str, Any]:
        """Get a specific personal item."""
        items = await self.db.query(
            TABLE,
            select="*",
            filters={"id": item_id, "user_id": user_id}
        )
        if not items:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Item not found")
        return items[0]

    async def update_item(
        self, item_id: str, user_id: str, item_data: PersonalItemUpdate
    ) -> Dict[str, Any]:
        """Update a personal item."""
        await verify_ownership(self.db, TABLE, item_id, user_id, "Item")
        update_data = build_update_data(item_data)

        updated = await self.db.update(
            TABLE,
            {"id": item_id},
            update_data
        )
        # Handle both list (from test mocks) and dict (from actual db.update)
        return updated[0] if isinstance(updated, list) else updated

    async def delete_item(self, item_id: str, user_id: str) -> Dict[str, Any]:
        """Soft delete a personal item (set is_active=false)."""
        return await soft_delete_entity(self.db, TABLE, item_id, user_id, "Item")
