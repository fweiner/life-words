"""Admin-related Pydantic models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AdminUserStats(BaseModel):
    """User stats for admin listing."""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    contact_count: int = 0
    item_count: int = 0
    session_count: int = 0
    last_active_at: Optional[datetime] = None


class AdminDeleteResponse(BaseModel):
    """Response for admin user deletion."""
    success: bool
    message: str
    deleted_user_id: str
