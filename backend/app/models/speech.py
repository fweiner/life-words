"""Speech-related Pydantic models."""
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class SpeechTranscribeResponse(BaseModel):
    """Speech transcription response."""
    text: str
    confidence: Optional[float] = None


class TextToSpeechRequest(BaseModel):
    """Text to speech request."""
    text: str
    language_code: str = "en-US"
    voice_name: Optional[str] = None


class PollyTTSRequest(BaseModel):
    """Amazon Polly text-to-speech request."""
    text: str = Field(..., max_length=3000)
    gender: Optional[Literal["male", "female", "neutral"]] = "neutral"

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text is required")
        return v
