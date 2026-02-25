"""Admin service for user management."""
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import httpx
from fastapi import HTTPException

from app.config import settings
from app.core.database import SupabaseClient

VALID_ACCOUNT_STATUSES = {"trial", "paid"}


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

    async def update_account_status(
        self,
        user_id: str,
        account_status: str,
        trial_ends_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Update a user's account status (trial/paid)."""
        if account_status not in VALID_ACCOUNT_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid account status. Must be one of: {', '.join(VALID_ACCOUNT_STATUSES)}",
            )

        if account_status == "trial" and trial_ends_at is None:
            raise HTTPException(
                status_code=400,
                detail="trial_ends_at is required when setting account_status to 'trial'",
            )

        # Verify user exists
        profiles = await self.db.query("profiles", filters={"id": user_id})
        if not profiles:
            raise HTTPException(status_code=404, detail="User not found")

        update_data: Dict[str, Any] = {"account_status": account_status}
        if account_status == "paid":
            update_data["trial_ends_at"] = None
        else:
            update_data["trial_ends_at"] = trial_ends_at.isoformat()

        result = await self.db.update("profiles", filters={"id": user_id}, data=update_data)
        return result

    async def list_error_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent error logs."""
        return await self.db.query(
            "error_logs",
            order_by="timestamp",
            order_desc=True,
            limit=limit,
        )
