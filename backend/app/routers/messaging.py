"""Direct Messaging endpoints for Life Words treatment."""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.dependencies import CurrentUser, CurrentUserId, Database
from app.models.schemas import (
    MessageCreate,
    MessageResponse,
    ConversationSummary,
    MessagingTokenResponse,
    MessagingTokenVerifyResponse,
    PublicMessageCreate,
)
from app.services.messaging_service import MessagingService

router = APIRouter()


# ============== Authenticated Endpoints (for user) ==============

@router.get("/conversations")
async def list_conversations(
    user_id: CurrentUserId,
    db: Database
) -> List[ConversationSummary]:
    """List all contacts with message counts and latest message preview."""
    service = MessagingService(db)
    summaries = await service.list_conversations(user_id)
    return [ConversationSummary(**s) for s in summaries]


@router.get("/conversations/{contact_id}")
async def get_conversation(
    contact_id: str,
    user_id: CurrentUserId,
    db: Database,
    limit: int = 50
) -> Dict[str, Any]:
    """Get messages for a specific contact."""
    service = MessagingService(db)
    result = await service.get_conversation(contact_id, user_id, limit)
    result["messages"] = [MessageResponse(**msg) for msg in result["messages"]]
    return result


@router.post("/conversations/{contact_id}/messages")
async def send_message(
    contact_id: str,
    message_data: MessageCreate,
    user_id: CurrentUserId,
    db: Database
) -> MessageResponse:
    """Send a message to a contact (from user)."""
    service = MessagingService(db)
    result = await service.send_message(contact_id, user_id, message_data)
    return MessageResponse(**result)


@router.put("/conversations/{contact_id}/read")
async def mark_messages_read(
    contact_id: str,
    user_id: CurrentUserId,
    db: Database
) -> Dict[str, Any]:
    """Mark all messages from a contact as read."""
    service = MessagingService(db)
    return await service.mark_messages_read(contact_id, user_id)


@router.get("/conversations/{contact_id}/token")
async def get_or_create_messaging_token(
    contact_id: str,
    user_id: CurrentUserId,
    db: Database
) -> MessagingTokenResponse:
    """Get or create a messaging token for a contact."""
    service = MessagingService(db)
    result = await service.get_or_create_messaging_token(contact_id, user_id)
    return MessagingTokenResponse(**result)


@router.post("/conversations/{contact_id}/token/regenerate")
async def regenerate_messaging_token(
    contact_id: str,
    user_id: CurrentUserId,
    db: Database
) -> MessagingTokenResponse:
    """Regenerate the messaging token (invalidates old link)."""
    service = MessagingService(db)
    result = await service.regenerate_messaging_token(contact_id, user_id)
    return MessagingTokenResponse(**result)


@router.get("/unread-count")
async def get_unread_count(
    user_id: CurrentUserId,
    db: Database
) -> Dict[str, int]:
    """Get total unread message count for notification badge."""
    service = MessagingService(db)
    return await service.get_unread_count(user_id)


# ============== Public Endpoints (for contacts via token) ==============

@router.get("/public/verify/{token}")
async def verify_messaging_token(
    token: str, db: Database
) -> MessagingTokenVerifyResponse:
    """Verify a messaging token and return contact/user info."""
    service = MessagingService(db)
    result = await service.verify_messaging_token(token)
    return MessagingTokenVerifyResponse(**result)


@router.get("/public/{token}/messages")
async def get_public_messages(
    token: str, db: Database, limit: int = 50
) -> Dict[str, Any]:
    """Get conversation history (public endpoint for contacts)."""
    service = MessagingService(db)
    result = await service.get_public_messages(token, limit)
    result["messages"] = [MessageResponse(**msg) for msg in result["messages"]]
    return result


@router.post("/public/{token}/messages")
async def send_public_message(
    token: str,
    message_data: PublicMessageCreate,
    db: Database
) -> MessageResponse:
    """Send a message from contact to user (public endpoint)."""
    service = MessagingService(db)
    result = await service.send_public_message(token, message_data)
    return MessageResponse(**result)


@router.post("/public/upload-media")
async def upload_public_media(
    file: UploadFile = File(...),
    media_type: str = "photo",
    db: Database = None
) -> Dict[str, str]:
    """Upload photo or voice message (public endpoint)."""
    service = MessagingService(db)
    return await service.upload_media(file, media_type)


@router.post("/upload-media")
async def upload_authenticated_media(
    user_id: CurrentUserId,
    db: Database,
    file: UploadFile = File(...),
    media_type: str = "photo"
) -> Dict[str, str]:
    """Upload photo or voice message (authenticated endpoint)."""
    service = MessagingService(db)
    return await service.upload_media(file, media_type)
