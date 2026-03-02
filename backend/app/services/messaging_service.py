"""Messaging service for direct messaging between users and contacts."""
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import HTTPException, UploadFile
from app.core.database import SupabaseClient
from app.config import settings
from app.services.utils import (
    generate_secure_token,
    upload_to_storage,
    verify_ownership,
    safe_file_extension,
    FRONTEND_URL,
)
import httpx


class MessagingService:
    """Service for direct messaging operations."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def list_conversations(
        self, user_id: str
    ) -> List[Dict[str, Any]]:
        """List all contacts with message counts and latest message preview."""
        contacts = await self.db.query(
            "personal_contacts",
            select="id, name, photo_url, relationship",
            filters={"user_id": user_id, "is_active": True}
        )

        if not contacts:
            return []

        # Get messaging tokens for this user
        tokens = await self.db.query(
            "contact_messaging_tokens",
            select="contact_id",
            filters={"user_id": user_id, "is_active": True}
        )
        token_contact_ids = {t["contact_id"] for t in tokens} if tokens else set()

        summaries = []
        for contact in contacts:
            # Get unread count
            unread_messages = await self.db.query(
                "messages",
                select="id",
                filters={
                    "user_id": user_id,
                    "contact_id": contact["id"],
                    "direction": "contact_to_user",
                    "is_read": False
                }
            )
            unread_count = len(unread_messages) if unread_messages else 0

            # Get latest message
            messages = await self.db.query(
                "messages",
                select="text_content, created_at, direction",
                filters={"user_id": user_id, "contact_id": contact["id"]},
                order="created_at.desc",
                limit=1
            )

            last_msg = messages[0] if messages else None

            summaries.append({
                "contact_id": contact["id"],
                "contact_name": contact["name"],
                "contact_photo_url": contact["photo_url"],
                "contact_relationship": contact["relationship"],
                "last_message_text": last_msg["text_content"] if last_msg else None,
                "last_message_at": last_msg["created_at"] if last_msg else None,
                "last_message_direction": last_msg["direction"] if last_msg else None,
                "unread_count": unread_count,
                "has_messaging_token": contact["id"] in token_contact_ids
            })

        # Sort by last message time (most recent first)
        summaries.sort(
            key=lambda x: x["last_message_at"] or datetime.min.replace(tzinfo=timezone.utc).isoformat(),
            reverse=True
        )

        return summaries

    async def get_conversation(
        self, contact_id: str, user_id: str, limit: int = 50
    ) -> Dict[str, Any]:
        """Get messages for a specific contact."""
        contacts = await self.db.query(
            "personal_contacts",
            select="id, name, photo_url, relationship",
            filters={"id": contact_id, "user_id": user_id}
        )
        if not contacts:
            raise HTTPException(status_code=404, detail="Contact not found")

        messages = await self.db.query(
            "messages",
            select="*",
            filters={"user_id": user_id, "contact_id": contact_id},
            order="created_at.asc",
            limit=limit
        )

        return {
            "contact": contacts[0],
            "messages": messages if messages else []
        }

    async def send_message(
        self, contact_id: str, user_id: str, message_data
    ) -> Dict[str, Any]:
        """Send a message to a contact (from user)."""
        if not any([message_data.text_content, message_data.photo_url, message_data.voice_url]):
            raise HTTPException(status_code=400, detail="Message must have content")

        await verify_ownership(self.db, "personal_contacts", contact_id, user_id, "Contact")

        message = await self.db.insert(
            "messages",
            {
                "user_id": user_id,
                "contact_id": contact_id,
                "direction": "user_to_contact",
                "text_content": message_data.text_content,
                "photo_url": message_data.photo_url,
                "voice_url": message_data.voice_url,
                "voice_duration_seconds": message_data.voice_duration_seconds,
                "is_read": True
            }
        )

        result = message[0] if isinstance(message, list) else message
        return result

    async def mark_messages_read(
        self, contact_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Mark all messages from a contact as read."""
        await verify_ownership(self.db, "personal_contacts", contact_id, user_id, "Contact")

        # Use raw httpx for multi-filter update (SupabaseClient.update doesn't
        # support filtering by direction + is_read booleans in compound form)
        headers = {
            "apikey": settings.supabase_secret_key,
            "Authorization": f"Bearer {settings.supabase_secret_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{settings.supabase_url}/rest/v1/messages",
                headers=headers,
                params={
                    "user_id": f"eq.{user_id}",
                    "contact_id": f"eq.{contact_id}",
                    "direction": "eq.contact_to_user",
                    "is_read": "eq.false"
                },
                json={
                    "is_read": True,
                    "read_at": datetime.now(timezone.utc).isoformat()
                }
            )

        return {"success": True}

    async def get_or_create_messaging_token(
        self, contact_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Get or create a messaging token for a contact."""
        await verify_ownership(self.db, "personal_contacts", contact_id, user_id, "Contact")

        tokens = await self.db.query(
            "contact_messaging_tokens",
            select="*",
            filters={"contact_id": contact_id, "user_id": user_id}
        )

        if tokens:
            token_data = tokens[0]
        else:
            new_token = generate_secure_token()
            token_result = await self.db.insert(
                "contact_messaging_tokens",
                {
                    "user_id": user_id,
                    "contact_id": contact_id,
                    "token": new_token,
                    "is_active": True
                }
            )
            token_data = token_result[0] if isinstance(token_result, list) else token_result

        return {
            "id": token_data["id"],
            "contact_id": token_data["contact_id"],
            "token": token_data["token"],
            "messaging_url": f"{FRONTEND_URL}/message/{token_data['token']}",
            "is_active": token_data["is_active"],
            "created_at": token_data["created_at"],
            "last_used_at": token_data.get("last_used_at")
        }

    async def regenerate_messaging_token(
        self, contact_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Regenerate the messaging token (invalidates old link)."""
        await verify_ownership(self.db, "personal_contacts", contact_id, user_id, "Contact")

        await self.db.delete(
            "contact_messaging_tokens",
            {"contact_id": contact_id, "user_id": user_id}
        )

        new_token = generate_secure_token()
        token_result = await self.db.insert(
            "contact_messaging_tokens",
            {
                "user_id": user_id,
                "contact_id": contact_id,
                "token": new_token,
                "is_active": True
            }
        )
        token_data = token_result[0] if isinstance(token_result, list) else token_result

        return {
            "id": token_data["id"],
            "contact_id": token_data["contact_id"],
            "token": token_data["token"],
            "messaging_url": f"{FRONTEND_URL}/message/{token_data['token']}",
            "is_active": token_data["is_active"],
            "created_at": token_data["created_at"],
            "last_used_at": None
        }

    async def get_unread_count(self, user_id: str) -> Dict[str, int]:
        """Get total unread message count for notification badge."""
        messages = await self.db.query(
            "messages",
            select="id",
            filters={
                "user_id": user_id,
                "direction": "contact_to_user",
                "is_read": False
            }
        )
        return {"count": len(messages) if messages else 0}

    # ============== Public operations (for contacts via token) ==============

    async def verify_messaging_token(self, token: str) -> Dict[str, Any]:
        """Verify a messaging token and return contact/user info."""
        tokens = await self.db.query(
            "contact_messaging_tokens",
            select="*",
            filters={"token": token}
        )

        if not tokens:
            return {"valid": False, "status": "not_found"}

        token_data = tokens[0]

        if not token_data["is_active"]:
            return {"valid": False, "status": "inactive"}

        # Get contact info
        contacts = await self.db.query(
            "personal_contacts",
            select="name, photo_url",
            filters={"id": token_data["contact_id"]}
        )
        contact = contacts[0] if contacts else {}

        # Get user's name
        profiles = await self.db.query(
            "profiles",
            select="full_name",
            filters={"id": token_data["user_id"]}
        )
        user_name = profiles[0]["full_name"] if profiles else None

        # Update last_used_at
        await self.db.update(
            "contact_messaging_tokens",
            {"id": token_data["id"]},
            {"last_used_at": datetime.now(timezone.utc).isoformat()}
        )

        return {
            "valid": True,
            "status": "active",
            "user_name": user_name,
            "contact_name": contact.get("name"),
            "contact_photo_url": contact.get("photo_url")
        }

    async def get_public_messages(
        self, token: str, limit: int = 50
    ) -> Dict[str, Any]:
        """Get conversation history (public endpoint for contacts)."""
        tokens = await self.db.query(
            "contact_messaging_tokens",
            select="*",
            filters={"token": token, "is_active": True}
        )

        if not tokens:
            raise HTTPException(
                status_code=404, detail="Invalid or inactive messaging link"
            )

        token_data = tokens[0]

        messages = await self.db.query(
            "messages",
            select="*",
            filters={
                "user_id": token_data["user_id"],
                "contact_id": token_data["contact_id"]
            },
            order="created_at.asc",
            limit=limit
        )

        return {"messages": messages if messages else []}

    async def send_public_message(
        self, token: str, message_data
    ) -> Dict[str, Any]:
        """Send a message from contact to user (public)."""
        if not any([message_data.text_content, message_data.photo_url, message_data.voice_url]):
            raise HTTPException(status_code=400, detail="Message must have content")

        tokens = await self.db.query(
            "contact_messaging_tokens",
            select="*",
            filters={"token": token, "is_active": True}
        )

        if not tokens:
            raise HTTPException(
                status_code=404, detail="Invalid or inactive messaging link"
            )

        token_data = tokens[0]

        message = await self.db.insert(
            "messages",
            {
                "user_id": token_data["user_id"],
                "contact_id": token_data["contact_id"],
                "direction": "contact_to_user",
                "text_content": message_data.text_content,
                "photo_url": message_data.photo_url,
                "voice_url": message_data.voice_url,
                "voice_duration_seconds": message_data.voice_duration_seconds,
                "is_read": False
            }
        )

        result = message[0] if isinstance(message, list) else message
        return result

    async def upload_media(
        self, file: UploadFile, media_type: str = "photo"
    ) -> Dict[str, str]:
        """Upload photo or voice message."""
        if media_type == "photo":
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="File must be an image")
            max_size = 5 * 1024 * 1024
            folder = "message-photos"
        elif media_type == "voice":
            allowed_types = [
                "audio/webm", "audio/mp3", "audio/mpeg",
                "audio/wav", "audio/ogg", "audio/mp4"
            ]
            if not file.content_type or file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="File must be an audio file")
            max_size = 10 * 1024 * 1024
            folder = "message-voice"
        else:
            raise HTTPException(status_code=400, detail="Invalid media type")

        content = await file.read()

        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size must be less than {max_size // (1024 * 1024)}MB"
            )

        ext = safe_file_extension(
            file.content_type or "",
            "jpg" if media_type == "photo" else "webm",
        )

        url = await upload_to_storage(
            content,
            file.content_type or "application/octet-stream",
            folder,
            ext,
        )
        return {"url": url, "media_type": media_type}
