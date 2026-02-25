"""FastAPI dependencies for dependency injection."""
from typing import Annotated
from fastapi import Depends
from app.core.auth import get_current_user, get_current_user_id, require_admin
from app.core.database import db, SupabaseClient


# Database dependency
async def get_db() -> SupabaseClient:
    """Get database client."""
    return db


# Type aliases for dependencies
CurrentUser = Annotated[dict, Depends(get_current_user)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
Database = Annotated[SupabaseClient, Depends(get_db)]
AdminUser = Annotated[dict, Depends(require_admin)]
