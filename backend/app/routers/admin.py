"""Admin management endpoints."""
from typing import List
from fastapi import APIRouter
from app.core.dependencies import AdminUser, Database
from app.models.admin import AdminUserStats, AdminDeleteResponse
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
