"""Authentication endpoints."""
from fastapi import APIRouter
from app.core.dependencies import CurrentUser


router = APIRouter()


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: CurrentUser
):
    """Get current user information."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "role": current_user.get("role", "authenticated")
    }


@router.post("/logout")
async def logout(current_user: CurrentUser):
    """
    Logout endpoint.
    Note: Actual logout is handled client-side by clearing the session.
    This endpoint is provided for API completeness.
    """
    return {"message": "Logged out successfully"}
