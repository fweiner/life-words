"""Shared utility functions for services."""
import secrets
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
import httpx

from app.config import settings


# Shared frontend URL for invite/messaging links
FRONTEND_URL = settings.cors_origins[0] if settings.cors_origins else "http://localhost:3000"


def empty_to_none(val: Any) -> Optional[Any]:
    """Convert empty strings to None, pass through everything else."""
    return None if val == "" else val


def generate_secure_token() -> str:
    """Generate a secure random token for invite/messaging links."""
    return secrets.token_urlsafe(32)


async def verify_ownership(
    db, table: str, entity_id: str, user_id: str, entity_name: str = "Entity"
) -> None:
    """Verify that an entity belongs to a user. Raises 404 if not found."""
    existing = await db.query(
        table, select="id", filters={"id": entity_id, "user_id": user_id}
    )
    if not existing:
        raise HTTPException(status_code=404, detail=f"{entity_name} not found")


async def verify_session(
    db, table: str, session_id: str, user_id: str
) -> Dict[str, Any]:
    """Verify a session belongs to a user and return it. Raises 404 if not found."""
    sessions = await db.query(
        table, select="*", filters={"id": session_id, "user_id": user_id}
    )
    if not sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[0]


def build_update_data(model_instance) -> Dict[str, Any]:
    """Build update dict from a Pydantic model: dump, filter None, apply empty_to_none.

    Raises 400 if no fields to update.
    """
    update_data = {}
    for k, v in model_instance.model_dump().items():
        if v is not None:
            update_data[k] = empty_to_none(v)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    return update_data


async def soft_delete_entity(
    db, table: str, entity_id: str, user_id: str, entity_name: str = "Entity"
) -> Dict[str, Any]:
    """Verify ownership then soft delete (set is_active=False). Returns success dict."""
    await verify_ownership(db, table, entity_id, user_id, entity_name)
    await db.update(table, {"id": entity_id}, {"is_active": False})
    return {"success": True, "message": f"{entity_name} deactivated"}


async def list_user_entities(
    db, table: str, user_id: str, include_inactive: bool = False
) -> List[Dict[str, Any]]:
    """List entities for a user with optional is_active filter."""
    filters: Dict[str, Any] = {"user_id": user_id}
    if not include_inactive:
        filters["is_active"] = True

    results = await db.query(
        table, select="*", filters=filters, order="created_at.desc"
    )
    return results or []


async def verify_can_practice(db, user_id: str) -> None:
    """Verify user can start a practice session. Raises 403 if expired/cancelled."""
    from datetime import datetime, timezone

    profiles = await db.query(
        "profiles",
        select="account_status,trial_ends_at",
        filters={"id": user_id},
    )
    if not profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = profiles[0]
    account_status = profile.get("account_status", "trial")

    if account_status == "paid":
        return

    if account_status == "trial":
        trial_ends_at = profile.get("trial_ends_at")
        if trial_ends_at:
            trial_end = (
                datetime.fromisoformat(trial_ends_at.replace("Z", "+00:00"))
                if isinstance(trial_ends_at, str)
                else trial_ends_at
            )
            if trial_end > datetime.now(timezone.utc):
                return

    raise HTTPException(
        status_code=403,
        detail="Your trial has expired. Please subscribe to continue practicing.",
    )


async def get_profile_or_404(db, user_id: str) -> Dict[str, Any]:
    """Get a user profile or raise 404 if not found."""
    profiles = await db.query("profiles", select="*", filters={"id": user_id})
    if not profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profiles[0]


async def list_complete_entities(
    db, table: str, user_id: str
) -> List[Dict[str, Any]]:
    """List active and complete entities for a user."""
    results = await db.query(
        table,
        select="*",
        filters={"user_id": user_id, "is_active": True, "is_complete": True},
    )
    return results or []


def calculate_session_accuracy(responses: list) -> tuple:
    """Calculate session accuracy stats.

    Returns (total_correct, accuracy_percentage).
    """
    if not responses:
        return 0, 0.0
    total_correct = sum(1 for r in responses if r["is_correct"])
    accuracy = round((total_correct / len(responses)) * 100, 1)
    return total_correct, accuracy


# File extension allowlist from content-type for secure uploads
EXTENSION_FROM_CONTENT_TYPE = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "audio/webm": "webm",
    "audio/mp3": "mp3",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
    "audio/ogg": "ogg",
    "audio/mp4": "m4a",
}


def safe_file_extension(content_type: str, default: str = "bin") -> str:
    """Get a safe file extension from content-type. Never trusts user-supplied filename."""
    return EXTENSION_FROM_CONTENT_TYPE.get(content_type, default)


async def upload_to_storage(
    content: bytes, content_type: str, folder: str, file_ext: str
) -> str:
    """Upload content to Supabase Storage and return the public URL."""
    filename = f"{folder}/{secrets.token_urlsafe(16)}.{file_ext}"

    headers = {
        "apikey": settings.supabase_secret_key,
        "Authorization": f"Bearer {settings.supabase_secret_key}",
        "Content-Type": content_type,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.supabase_url}/storage/v1/object/user-uploads/{filename}",
            headers=headers,
            content=content,
        )

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500, detail=f"Upload failed: {response.text}"
            )

    return f"{settings.supabase_url}/storage/v1/object/public/user-uploads/{filename}"
