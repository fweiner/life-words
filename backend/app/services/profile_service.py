"""Profile service for managing user profiles."""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from app.core.database import SupabaseClient
from app.models.profile import ProfileUpdate


class ProfileService:
    """Service for user profile operations."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def get_or_create_profile(self, user_id: str, email: str) -> Dict[str, Any]:
        """Get profile, creating it if it doesn't exist."""
        profiles = await self.db.query(
            "profiles",
            filters={"id": user_id}
        )

        if profiles:
            return profiles[0]

        trial_end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        new_profile = await self.db.insert(
            "profiles",
            {
                "id": user_id,
                "email": email,
                "full_name": None,
                "account_status": "trial",
                "trial_ends_at": trial_end,
            }
        )
        return new_profile[0] if isinstance(new_profile, list) else new_profile

    async def get_profile(self, user_id: str, email: str) -> Dict[str, Any]:
        """Get current user's profile (creates if needed)."""
        return await self.get_or_create_profile(user_id, email)

    async def update_profile(
        self,
        user_id: str,
        email: str,
        profile_data: ProfileUpdate
    ) -> Dict[str, Any]:
        """Update user's profile."""
        await self.get_or_create_profile(user_id, email)

        update_data = profile_data.model_dump(exclude_none=True)

        # Convert date to ISO string for DB
        if "date_of_birth" in update_data:
            update_data["date_of_birth"] = update_data["date_of_birth"].isoformat()

        if not update_data:
            profiles = await self.db.query("profiles", filters={"id": user_id})
            return profiles[0]

        updated = await self.db.update(
            "profiles",
            filters={"id": user_id},
            data=update_data
        )

        return updated
