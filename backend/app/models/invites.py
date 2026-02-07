"""Contact Invite Pydantic models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class ContactInviteCreate(BaseModel):
    """Create contact invite request."""
    recipient_email: EmailStr
    recipient_name: str
    custom_message: Optional[str] = None


class ContactInviteResponse(BaseModel):
    """Contact invite response."""
    id: str
    user_id: str
    recipient_email: str
    recipient_name: str
    custom_message: Optional[str] = None
    status: str
    created_at: datetime
    expires_at: datetime
    completed_at: Optional[datetime] = None
    contact_id: Optional[str] = None


class InviteVerifyResponse(BaseModel):
    """Verify invite token response."""
    valid: bool
    status: str  # 'pending', 'completed', 'expired', 'not_found'
    inviter_name: Optional[str] = None
    recipient_name: Optional[str] = None
    contact_name: Optional[str] = None


class InviteSubmitRequest(BaseModel):
    """Submit invite form request (public endpoint)."""
    name: str
    nickname: Optional[str] = None
    relationship: str
    photo_url: str
    category: Optional[str] = None
    description: Optional[str] = None
    association: Optional[str] = None
    location_context: Optional[str] = None
    # Personal characteristics
    interests: Optional[str] = None
    personality: Optional[str] = None
    values: Optional[str] = None
    social_behavior: Optional[str] = None


class InviteSubmitResponse(BaseModel):
    """Submit invite form response."""
    success: bool
    message: str
    contact_name: Optional[str] = None
