"""Direct Messaging Pydantic models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MessageCreate(BaseModel):
    """Create message request (authenticated or public)."""
    text_content: Optional[str] = None
    photo_url: Optional[str] = None
    voice_url: Optional[str] = None
    voice_duration_seconds: Optional[int] = None


# Alias for backward compatibility — identical schema
PublicMessageCreate = MessageCreate


class MessageResponse(BaseModel):
    """Message response."""
    id: str
    user_id: str
    contact_id: str
    direction: str  # 'user_to_contact' or 'contact_to_user'
    text_content: Optional[str] = None
    photo_url: Optional[str] = None
    voice_url: Optional[str] = None
    voice_duration_seconds: Optional[int] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime


class ConversationSummary(BaseModel):
    """Conversation summary for inbox list."""
    contact_id: str
    contact_name: str
    contact_photo_url: str
    contact_relationship: str
    last_message_text: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_direction: Optional[str] = None
    unread_count: int
    has_messaging_token: bool


class MessagingTokenResponse(BaseModel):
    """Messaging token response."""
    id: str
    contact_id: str
    token: str
    messaging_url: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None


class MessagingTokenVerifyResponse(BaseModel):
    """Verify messaging token response (public)."""
    valid: bool
    status: str  # 'active', 'inactive', 'not_found'
    user_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_photo_url: Optional[str] = None
