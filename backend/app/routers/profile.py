"""Profile management endpoints."""
from fastapi import APIRouter
from app.core.dependencies import CurrentUser, Database
from app.models.profile import ProfileUpdate, ProfileResponse
from app.services.profile_service import ProfileService


router = APIRouter()


@router.get("", response_model=ProfileResponse)
async def get_profile(
    user: CurrentUser,
    db: Database
):
    """Get current user's profile."""
    service = ProfileService(db)
    return await service.get_profile(user["id"], user["email"])


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    user: CurrentUser,
    db: Database,
    profile_data: ProfileUpdate
):
    """Update current user's profile."""
    service = ProfileService(db)
    return await service.update_profile(user["id"], user["email"], profile_data)
