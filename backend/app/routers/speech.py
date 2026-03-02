"""Speech endpoints for text-to-speech using Amazon Polly."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.core.error_logger import log_error
from app.models.speech import PollyTTSRequest
from app.services.polly_service import polly_service

router = APIRouter()


@router.post("/tts")
async def text_to_speech(request: PollyTTSRequest) -> Response:
    """Convert text to speech using Amazon Polly. Public endpoint for frontend TTS."""
    try:
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
    except Exception as e:
        log_error(
            error=e,
            source="swallowed",
            service_name="PollyService",
            function_name="synthesize_for_gender",
            endpoint="/api/speech/tts",
            http_method="POST",
            status_code=500,
        )
        raise HTTPException(status_code=500, detail="Text-to-speech failed")
