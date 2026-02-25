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
    account_status: str = "trial"
    trial_ends_at: Optional[datetime] = None


class AdminDeleteResponse(BaseModel):
    """Response for admin user deletion."""
    success: bool
    message: str
    deleted_user_id: str


class AdminUpdateAccountStatus(BaseModel):
    """Request to update a user's account status."""
    account_status: str
    trial_ends_at: Optional[datetime] = None


class AdminUpdateAccountStatusResponse(BaseModel):
    """Response for account status update."""
    success: bool
    message: str
    account_status: str
    trial_ends_at: Optional[datetime] = None


class ErrorLogResponse(BaseModel):
    """Response for an error log entry."""
    id: str
    timestamp: datetime
    endpoint: str
    method: str
    status_code: int
    error_message: str
    traceback: Optional[str] = None
    user_id: Optional[str] = None
