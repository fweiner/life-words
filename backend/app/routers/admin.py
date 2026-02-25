"""Admin management endpoints."""
from typing import List
from fastapi import APIRouter, Query
from app.core.dependencies import AdminUser, Database
from app.models.admin import (
    AdminUserStats,
    AdminDeleteResponse,
    AdminUpdateAccountStatus,
    AdminUpdateAccountStatusResponse,
    ErrorLogResponse,
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


@router.get("/error-logs", response_model=List[ErrorLogResponse])
async def list_error_logs(
    user: AdminUser,
    db: Database,
    limit: int = Query(default=50, ge=1, le=200),
):
    """List recent error logs. Admin only."""
    service = AdminService(db)
    return await service.list_error_logs(limit=limit)
