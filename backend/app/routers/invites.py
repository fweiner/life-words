"""Contact invite endpoints for Life Words treatment."""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from app.core.dependencies import CurrentUser, CurrentUserId, Database
from app.models.schemas import (
    ContactInviteCreate,
    ContactInviteResponse,
    InviteVerifyResponse,
    InviteSubmitRequest,
    InviteSubmitResponse,
)
from app.services.invite_service import InviteService

router = APIRouter()


# ============== Authenticated Endpoints ==============

@router.post("/invites")
async def create_invite(
    invite_data: ContactInviteCreate,
    user: CurrentUser,
    db: Database
) -> ContactInviteResponse:
    """Create and send an invite to a contact."""
    service = InviteService(db)
    result = await service.create_invite(user, invite_data)
    return ContactInviteResponse(**result)


@router.get("/invites")
async def list_invites(
    user_id: CurrentUserId,
    db: Database
) -> List[ContactInviteResponse]:
    """List all invites sent by the current user."""
    service = InviteService(db)
    invites = await service.list_invites(user_id)
    return [ContactInviteResponse(**inv) for inv in invites]


@router.delete("/invites/{invite_id}")
async def cancel_invite(
    invite_id: str,
    user_id: CurrentUserId,
    db: Database
) -> Dict[str, Any]:
    """Cancel a pending invite."""
    service = InviteService(db)
    return await service.cancel_invite(invite_id, user_id)


# ============== Public Endpoints (no auth required) ==============

@router.get("/invites/verify/{token}")
async def verify_invite(token: str, db: Database) -> InviteVerifyResponse:
    """Verify an invite token and return its status (public endpoint)."""
    service = InviteService(db)
    result = await service.verify_invite(token)
    return InviteVerifyResponse(**result)


@router.post("/invites/submit/{token}")
async def submit_invite(
    token: str,
    contact_data: InviteSubmitRequest,
    db: Database
) -> InviteSubmitResponse:
    """Submit contact information from an invite (public endpoint)."""
    service = InviteService(db)
    result = await service.submit_invite(token, contact_data)
    return InviteSubmitResponse(**result)


@router.post("/invites/upload-photo")
async def upload_invite_photo(
    token: str = Query(..., description="Invite token for authorization"),
    file: UploadFile = File(...),
    db: Database = None,
) -> Dict[str, str]:
    """Upload a photo for an invite submission (public, token-validated)."""
    service = InviteService(db)
    await service.verify_invite_token_for_upload(token)
    return await service.upload_photo(file)
