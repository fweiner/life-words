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
    created_at: datetime
    error_message: str
    error_type: Optional[str] = None
    stacktrace: Optional[str] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    request_body: Optional[dict] = None
    query_params: Optional[dict] = None
    status_code: Optional[int] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    source: str = "unhandled"
    service_name: Optional[str] = None
    function_name: Optional[str] = None
    environment: Optional[str] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None


class ErrorLogListResponse(BaseModel):
    """Paginated error log list response."""
    errors: list[ErrorLogResponse]
    total: int
    page: int
    per_page: int


class ResolveRequest(BaseModel):
    """Request to resolve an error."""
    notes: Optional[str] = None
