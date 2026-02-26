"""Admin service for user management and error log management."""
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import httpx
from fastapi import HTTPException

from app.config import settings
from app.core.database import SupabaseClient

VALID_ACCOUNT_STATUSES = {"trial", "paid", "cancelled", "past_due"}
VALID_ERROR_SOURCES = {"unhandled", "swallowed", "manual"}


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

    async def list_error_logs(
        self,
        search: Optional[str] = None,
        source: Optional[str] = None,
        resolved: Optional[bool] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """List error logs with search, filtering, and pagination."""
        params: Dict[str, str] = {
            "select": "*",
            "order": "created_at.desc",
            "limit": str(per_page),
            "offset": str((page - 1) * per_page),
        }

        if search:
            params["error_message"] = f"ilike.*{search}*"
        if source and source in VALID_ERROR_SOURCES:
            params["source"] = f"eq.{source}"
        if resolved is not None:
            params["is_resolved"] = f"eq.{str(resolved).lower()}"

        url = f"{settings.supabase_url}/rest/v1/error_logs"
        headers = {
            "apikey": settings.supabase_secret_key,
            "Authorization": f"Bearer {settings.supabase_secret_key}",
        }

        async with httpx.AsyncClient() as client:
            # Fetch errors
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            errors = resp.json()

            # Fetch total count for pagination
            count_params = {
                k: v
                for k, v in params.items()
                if k not in ("order", "limit", "offset", "select")
            }
            count_params["select"] = "id"
            count_resp = await client.get(
                url,
                headers={
                    **headers,
                    "Prefer": "count=exact",
                },
                params=count_params,
            )
            total = int(
                count_resp.headers.get("content-range", "0/0").split("/")[-1]
            )

        return {
            "errors": errors,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def resolve_error(
        self, error_id: str, admin_email: str, notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Mark an error as resolved."""
        url = f"{settings.supabase_url}/rest/v1/error_logs"
        headers = {
            "apikey": settings.supabase_secret_key,
            "Authorization": f"Bearer {settings.supabase_secret_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        params = {"id": f"eq.{error_id}"}
        data = {
            "is_resolved": True,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolved_by": admin_email,
            "notes": notes,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                url, headers=headers, params=params, json=data
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else None

    async def unresolve_error(
        self, error_id: str
    ) -> Optional[Dict[str, Any]]:
        """Reopen a resolved error."""
        url = f"{settings.supabase_url}/rest/v1/error_logs"
        headers = {
            "apikey": settings.supabase_secret_key,
            "Authorization": f"Bearer {settings.supabase_secret_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        params = {"id": f"eq.{error_id}"}
        data = {
            "is_resolved": False,
            "resolved_at": None,
            "resolved_by": None,
            "notes": None,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                url, headers=headers, params=params, json=data
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else None
