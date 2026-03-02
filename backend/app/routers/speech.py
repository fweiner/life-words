"""Speech endpoints for text-to-speech using Amazon Polly."""
from fastapi import APIRouter
from fastapi.responses import Response
from app.core.dependencies import CurrentUserId
from app.models.speech import PollyTTSRequest
from app.services.polly_service import polly_service

router = APIRouter()


@router.post("/tts")
async def text_to_speech(request: PollyTTSRequest, user_id: CurrentUserId) -> Response:
    """Convert text to speech using Amazon Polly."""
    audio_content = await polly_service.synthesize_for_gender(
        request.text, request.gender
    )
    return Response(
        content=audio_content,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "public, max-age=86400",
        },
    )
