"""Invite service for managing contact invites."""
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import HTTPException, UploadFile
from app.core.database import SupabaseClient
from app.services.utils import empty_to_none, generate_secure_token, upload_to_storage, FRONTEND_URL
from app.services.email_service import send_invite_email, send_thank_you_email
from app.services.profile_service import ProfileService


class InviteService:
    """Service for contact invite operations."""

    def __init__(self, db: SupabaseClient):
        self.db = db
        self.profile_service = ProfileService(db)

    async def create_invite(
        self, user: dict, invite_data
    ) -> Dict[str, Any]:
        """Create and send an invite to a contact."""
        # Get or create the user's profile (reuses ProfileService)
        profile = await self.profile_service.get_or_create_profile(
            user["id"], user["email"]
        )

        if not profile.get("full_name"):
            raise HTTPException(
                status_code=400,
                detail="Please set your name in your profile before sending invites"
            )

        inviter_name = profile["full_name"]
        token = generate_secure_token()
        invite_url = f"{FRONTEND_URL}/invite/{token}"

        invite = await self.db.insert(
            "contact_invites",
            {
                "user_id": user["id"],
                "recipient_email": invite_data.recipient_email,
                "recipient_name": invite_data.recipient_name,
                "token": token,
                "custom_message": invite_data.custom_message,
                "status": "pending"
            }
        )

        # Send invite email
        email_sent, email_error = await send_invite_email(
            recipient_email=invite_data.recipient_email,
            recipient_name=invite_data.recipient_name,
            inviter_full_name=inviter_name,
            invite_url=invite_url,
            custom_message=invite_data.custom_message
        )

        if not email_sent:
            await self.db.delete("contact_invites", {"id": invite[0]["id"]})
            error_detail = (
                f"Failed to send invite email: {email_error}"
                if email_error
                else "Failed to send invite email. Please try again."
            )
            raise HTTPException(status_code=500, detail=error_detail)

        return invite[0]

    async def list_invites(self, user_id: str) -> List[Dict[str, Any]]:
        """List all invites sent by the current user."""
        invites = await self.db.query(
            "contact_invites",
            select="*",
            filters={"user_id": user_id},
            order="created_at.desc"
        )
        return invites if invites else []

    async def cancel_invite(
        self, invite_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Cancel a pending invite."""
        invites = await self.db.query(
            "contact_invites",
            select="*",
            filters={"id": invite_id, "user_id": user_id}
        )

        if not invites:
            raise HTTPException(status_code=404, detail="Invite not found")

        invite = invites[0]
        if invite["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail="Only pending invites can be cancelled"
            )

        await self.db.delete("contact_invites", {"id": invite_id})
        return {"success": True, "message": "Invite cancelled"}

    async def verify_invite(self, token: str) -> Dict[str, Any]:
        """Verify an invite token and return its status (public)."""
        invites = await self.db.query(
            "contact_invites",
            select="*",
            filters={"token": token}
        )

        if not invites:
            return {"valid": False, "status": "not_found"}

        invite = invites[0]

        # Check if expired
        expires_at = datetime.fromisoformat(
            invite["expires_at"].replace("Z", "+00:00")
        )
        if expires_at < datetime.now(timezone.utc):
            return {"valid": False, "status": "expired"}

        # Check if already completed
        if invite["status"] == "completed":
            contact_name = None
            if invite.get("contact_id"):
                contacts = await self.db.query(
                    "personal_contacts",
                    select="name",
                    filters={"id": invite["contact_id"]}
                )
                if contacts:
                    contact_name = contacts[0]["name"]

            return {
                "valid": False,
                "status": "completed",
                "contact_name": contact_name
            }

        # Get inviter's name
        profiles = await self.db.query(
            "profiles",
            select="full_name",
            filters={"id": invite["user_id"]}
        )
        inviter_name = profiles[0]["full_name"] if profiles else None

        return {
            "valid": True,
            "status": "pending",
            "inviter_name": inviter_name,
            "recipient_name": invite["recipient_name"]
        }

    async def submit_invite(
        self, token: str, contact_data
    ) -> Dict[str, Any]:
        """Submit contact information from an invite (public)."""
        invites = await self.db.query(
            "contact_invites",
            select="*",
            filters={"token": token}
        )

        if not invites:
            raise HTTPException(status_code=404, detail="Invite not found")

        invite = invites[0]

        # Check if expired
        expires_at = datetime.fromisoformat(
            invite["expires_at"].replace("Z", "+00:00")
        )
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="This invite has expired")

        if invite["status"] == "completed":
            raise HTTPException(
                status_code=400,
                detail="This invite has already been used"
            )

        # Create the contact
        contact_payload = {
            "user_id": invite["user_id"],
            "name": contact_data.name,
            "nickname": empty_to_none(contact_data.nickname),
            "relationship": contact_data.relationship,
            "photo_url": contact_data.photo_url,
            "category": empty_to_none(contact_data.category),
            "description": empty_to_none(contact_data.description),
            "association": empty_to_none(contact_data.association),
            "location_context": empty_to_none(contact_data.location_context),
            "interests": empty_to_none(contact_data.interests),
            "personality": empty_to_none(contact_data.personality),
            "values": empty_to_none(contact_data.values),
            "social_behavior": empty_to_none(contact_data.social_behavior)
        }

        contact = await self.db.insert("personal_contacts", contact_payload)
        contact_id = contact[0]["id"] if isinstance(contact, list) else contact["id"]

        # Update invite status
        await self.db.update(
            "contact_invites",
            {"id": invite["id"]},
            {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "contact_id": contact_id
            }
        )

        # Get inviter's name for thank you email
        profiles = await self.db.query(
            "profiles",
            select="full_name",
            filters={"id": invite["user_id"]}
        )
        inviter_name = profiles[0]["full_name"] if profiles else "the user"

        # Send thank you email
        await send_thank_you_email(
            recipient_email=invite["recipient_email"],
            recipient_name=contact_data.name,
            inviter_full_name=inviter_name
        )

        return {
            "success": True,
            "message": "Thank you! Your information has been added.",
            "contact_name": contact_data.name
        }

    async def upload_photo(self, file: UploadFile) -> Dict[str, str]:
        """Upload a photo for an invite submission (public)."""
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        content = await file.read()

        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400, detail="File size must be less than 5MB"
            )

        file_ext = (
            file.filename.split(".")[-1]
            if file.filename and "." in file.filename
            else "jpg"
        )

        photo_url = await upload_to_storage(
            content,
            file.content_type or "image/jpeg",
            "invite-uploads",
            file_ext,
        )
        return {"photo_url": photo_url}
