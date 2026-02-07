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
