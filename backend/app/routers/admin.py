"""Admin management endpoints."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.core.dependencies import AdminUser, Database
from app.models.admin import (
    AdminUserStats,
    AdminDeleteResponse,
    AdminUpdateAccountStatus,
    AdminUpdateAccountStatusResponse,
    ErrorLogListResponse,
    ResolveRequest,
)
from app.services.admin_service import AdminService


router = APIRouter()


@router.get("/users", response_model=List[AdminUserStats])
async def list_users(
    user: AdminUser,
    db: Database,
):
    """List all users with usage stats. Admin only."""
    service = AdminService(db)
    return await service.list_users_with_stats()


@router.delete("/users/{user_id}", response_model=AdminDeleteResponse)
async def delete_user(
    user_id: str,
    user: AdminUser,
    db: Database,
):
    """Delete a user and all their data. Admin only."""
    service = AdminService(db)
    await service.delete_user(user_id)
    return AdminDeleteResponse(
        success=True,
        message="User deleted successfully",
        deleted_user_id=user_id,
    )


@router.patch(
    "/users/{user_id}/account-status",
    response_model=AdminUpdateAccountStatusResponse,
)
async def update_account_status(
    user_id: str,
    body: AdminUpdateAccountStatus,
    user: AdminUser,
    db: Database,
):
    """Update a user's account status. Admin only."""
    service = AdminService(db)
    result = await service.update_account_status(
        user_id, body.account_status, body.trial_ends_at
    )
    return AdminUpdateAccountStatusResponse(
        success=True,
        message=f"Account status updated to '{body.account_status}'",
        account_status=result.get("account_status", body.account_status),
        trial_ends_at=result.get("trial_ends_at"),
    )


@router.get("/errors", response_model=ErrorLogListResponse)
async def list_errors(
    user: AdminUser,
    db: Database,
    search: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
):
    """List error logs with search, filtering, and pagination. Admin only."""
    service = AdminService(db)
    return await service.list_error_logs(
        search=search,
        source=source,
        resolved=resolved,
        page=page,
        per_page=per_page,
    )


@router.post("/errors/{error_id}/resolve")
async def resolve_error(
    error_id: str,
    body: ResolveRequest,
    user: AdminUser,
    db: Database,
):
    """Mark an error as resolved. Admin only."""
    service = AdminService(db)
    admin_email = user.get("email", "unknown")
    result = await service.resolve_error(error_id, admin_email, body.notes)
    if not result:
        raise HTTPException(status_code=404, detail="Error not found")
    return result


@router.post("/errors/{error_id}/unresolve")
async def unresolve_error(
    error_id: str,
    user: AdminUser,
    db: Database,
):
    """Reopen a resolved error. Admin only."""
    service = AdminService(db)
    result = await service.unresolve_error(error_id)
    if not result:
        raise HTTPException(status_code=404, detail="Error not found")
    return result
