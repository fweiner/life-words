"""Admin service for user management."""
from typing import Dict, List, Any

import httpx
from fastapi import HTTPException

from app.config import settings
from app.core.database import SupabaseClient


class AdminService:
    """Service for admin operations."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def list_users_with_stats(self) -> List[Dict[str, Any]]:
        """List all users with usage statistics."""
        return await self.db.rpc("get_admin_user_stats")

    async def delete_user(self, user_id: str) -> None:
        """Delete a user via Supabase Auth Admin API.

        This cascades to all user data via foreign key constraints.
        """
        url = f"{settings.supabase_url}/auth/v1/admin/users/{user_id}"
        headers = {
            "apikey": settings.supabase_secret_key,
            "Authorization": f"Bearer {settings.supabase_secret_key}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)

        if response.status_code in (200, 204):
            return
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {response.text}",
        )
