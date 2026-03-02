"""Admin service for user management and error log management."""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

import httpx
from fastapi import HTTPException

from app.config import settings
from app.core.database import SupabaseClient
from app.core.error_logger import log_error
from app.services.utils import get_profile_or_404

VALID_ACCOUNT_STATUSES = {"trial", "paid", "cancelled", "past_due", "admin_disabled"}
VALID_ERROR_SOURCES = {"unhandled", "swallowed", "manual"}

AUTH_ADMIN_URL = f"{settings.supabase_url}/auth/v1/admin"
AUTH_HEADERS = {
    "apikey": settings.supabase_secret_key,
    "Authorization": f"Bearer {settings.supabase_secret_key}",
}


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
        url = f"{AUTH_ADMIN_URL}/users/{user_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=AUTH_HEADERS)

        if response.status_code in (200, 204):
            return
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {response.text}",
        )

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        account_status: str = "trial",
        subscription_plan: Optional[str] = None,
        trial_days: Optional[int] = 14,
    ) -> str:
        """Create a new user via Supabase Auth Admin API, then set profile fields.

        Returns the new user's ID.
        """
        if account_status not in VALID_ACCOUNT_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid account status. Must be one of: {', '.join(VALID_ACCOUNT_STATUSES)}",
            )

        # Create user in Supabase Auth
        url = f"{AUTH_ADMIN_URL}/users"
        body: Dict[str, Any] = {
            "email": email,
            "password": password,
            "email_confirm": True,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, headers={**AUTH_HEADERS, "Content-Type": "application/json"}, json=body
            )

        if response.status_code == 422:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        if response.status_code not in (200, 201):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create user: {response.text}",
            )

        user_data = response.json()
        user_id = user_data["id"]

        # Update profile with admin-specified settings
        profile_data: Dict[str, Any] = {"account_status": account_status}
        if full_name:
            profile_data["full_name"] = full_name
        if subscription_plan:
            profile_data["subscription_plan"] = subscription_plan

        if account_status == "trial" and trial_days:
            profile_data["trial_ends_at"] = (
                datetime.now(timezone.utc) + timedelta(days=trial_days)
            ).isoformat()
        elif account_status == "paid":
            profile_data["trial_ends_at"] = None

        await self.db.update("profiles", filters={"id": user_id}, data=profile_data)

        return user_id

    async def update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
        account_status: Optional[str] = None,
        subscription_plan: Optional[str] = None,
        trial_ends_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Update a user's auth fields and/or profile fields.

        Returns refreshed user stats via RPC.
        """
        # Verify user exists
        await get_profile_or_404(self.db, user_id)

        if account_status and account_status not in VALID_ACCOUNT_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid account status. Must be one of: {', '.join(VALID_ACCOUNT_STATUSES)}",
            )

        # Update auth fields (email/password) if provided
        if email or password:
            auth_body: Dict[str, Any] = {}
            if email:
                auth_body["email"] = email
            if password:
                auth_body["password"] = password

            url = f"{AUTH_ADMIN_URL}/users/{user_id}"
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    headers={**AUTH_HEADERS, "Content-Type": "application/json"},
                    json=auth_body,
                )

            if response.status_code == 422:
                raise HTTPException(status_code=400, detail="Email already in use by another user")
            if response.status_code not in (200, 201):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to update user auth: {response.text}",
                )

        # Update profile fields
        profile_data: Dict[str, Any] = {}
        if full_name is not None:
            profile_data["full_name"] = full_name
        if account_status:
            profile_data["account_status"] = account_status
        if subscription_plan is not None:
            profile_data["subscription_plan"] = subscription_plan
        if trial_ends_at is not None:
            profile_data["trial_ends_at"] = trial_ends_at.isoformat()
        elif account_status == "paid":
            profile_data["trial_ends_at"] = None

        if profile_data:
            await self.db.update("profiles", filters={"id": user_id}, data=profile_data)

        # Return refreshed stats
        all_stats = await self.db.rpc("get_admin_user_stats")
        user_stats = next((u for u in all_stats if u["id"] == user_id), None)
        if not user_stats:
            raise HTTPException(status_code=404, detail="User not found after update")
        return user_stats

    async def toggle_user(self, user_id: str) -> Dict[str, str]:
        """Toggle a user between their current status and admin_disabled.

        Uses Auth Admin API ban_duration to prevent login when disabling.
        Returns dict with user_id and new_status.
        """
        profile = await get_profile_or_404(self.db, user_id)

        current_status = profile.get("account_status", "trial")

        if current_status == "admin_disabled":
            # Re-enable: restore previous status from metadata or default to trial
            previous_status = profile.get("previous_status", "trial")
            new_status = previous_status

            # Unban in Auth
            url = f"{AUTH_ADMIN_URL}/users/{user_id}"
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    headers={**AUTH_HEADERS, "Content-Type": "application/json"},
                    json={"ban_duration": "none"},
                )
            if response.status_code not in (200, 201):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to unban user: {response.text}",
                )

            await self.db.update(
                "profiles",
                filters={"id": user_id},
                data={"account_status": new_status, "previous_status": None},
            )
        else:
            # Disable: save current status and ban
            new_status = "admin_disabled"

            url = f"{AUTH_ADMIN_URL}/users/{user_id}"
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    headers={**AUTH_HEADERS, "Content-Type": "application/json"},
                    json={"ban_duration": "876000h"},  # ~100 years
                )
            if response.status_code not in (200, 201):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to ban user: {response.text}",
                )

            await self.db.update(
                "profiles",
                filters={"id": user_id},
                data={"account_status": "admin_disabled", "previous_status": current_status},
            )

        action = "enabled" if new_status != "admin_disabled" else "disabled"
        return {
            "user_id": user_id,
            "new_status": new_status,
            "action": action,
            "message": f"User {action} successfully",
        }

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
            safe_search = search.replace("*", "").replace(".", "")[:200]
            params["error_message"] = f"ilike.*{safe_search}*"
        if source and source in VALID_ERROR_SOURCES:
            params["source"] = f"eq.{source}"
        if resolved is not None:
            params["is_resolved"] = f"eq.{str(resolved).lower()}"

        url = f"{settings.supabase_url}/rest/v1/error_logs"

        async with httpx.AsyncClient() as client:
            # Fetch errors
            try:
                resp = await client.get(url, headers=AUTH_HEADERS, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                log_error(
                    error=e,
                    source="swallowed",
                    service_name="AdminService",
                    function_name="list_error_logs",
                    status_code=e.response.status_code,
                )
                raise HTTPException(status_code=500, detail="Failed to fetch error logs")
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
                    **AUTH_HEADERS,
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
    ) -> Dict[str, Any]:
        """Mark an error as resolved. Raises 404 if not found."""
        url = f"{settings.supabase_url}/rest/v1/error_logs"
        headers = {
            **AUTH_HEADERS,
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
            try:
                resp = await client.patch(
                    url, headers=headers, params=params, json=data
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                log_error(
                    error=e,
                    source="swallowed",
                    service_name="AdminService",
                    function_name="resolve_error",
                    status_code=e.response.status_code,
                )
                raise HTTPException(status_code=500, detail="Failed to resolve error")
            rows = resp.json()
            if not rows:
                raise HTTPException(status_code=404, detail="Error not found")
            return rows[0]

    async def unresolve_error(
        self, error_id: str
    ) -> Dict[str, Any]:
        """Reopen a resolved error. Raises 404 if not found."""
        url = f"{settings.supabase_url}/rest/v1/error_logs"
        headers = {
            **AUTH_HEADERS,
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
            try:
                resp = await client.patch(
                    url, headers=headers, params=params, json=data
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                log_error(
                    error=e,
                    source="swallowed",
                    service_name="AdminService",
                    function_name="unresolve_error",
                    status_code=e.response.status_code,
                )
                raise HTTPException(status_code=500, detail="Failed to unresolve error")
            rows = resp.json()
            if not rows:
                raise HTTPException(status_code=404, detail="Error not found")
            return rows[0]
