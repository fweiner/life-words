"""Amazon Polly Text-to-Speech service."""
import boto3
from typing import Optional
from app.config import settings
from app.core.error_logger import log_error


class PollyService:
    """Service for Amazon Polly text-to-speech."""

    def __init__(self):
        """Initialize Polly client."""
        self._client = None

    def _get_client(self):
        """Get or create Polly client."""
        if self._client is None:
            self._client = boto3.client(
                'polly',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
        return self._client

    async def synthesize_speech(
        self,
        text: str,
        voice_id: str = "Matthew",
        language_code: str = "en-US",
        engine: str = "neural"
    ) -> bytes:
        """
        Convert text to speech using Amazon Polly.

        Args:
            text: Text to convert to speech
            voice_id: Polly voice ID (default: Matthew - neural male voice)
                     Other options: Joanna (female), Ruth (female), Stephen (male)
            language_code: Language code (default: en-US)
            engine: Engine type - 'neural' or 'standard' (default: neural)

        Returns:
            Audio content as bytes (MP3 format)
        """
        client = self._get_client()

        try:
            response = client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                LanguageCode=language_code,
                Engine=engine
            )

            # Read the audio stream
            audio_stream = response['AudioStream']
            return audio_stream.read()

        except Exception as e:
            log_error(
                error=e,
                source="swallowed",
                service_name="PollyService",
                function_name="synthesize_speech",
            )
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail="Text-to-speech failed")

    def get_voice_for_gender(self, gender: str) -> str:
        """
        Get appropriate Polly voice ID based on gender preference.

        Args:
            gender: 'male', 'female', or 'neutral'

        Returns:
            Polly voice ID
        """
        # Neural voices for US English
        voice_map = {
            'male': 'Matthew',
            'female': 'Joanna',
            'neutral': 'Matthew'  # Default to Matthew for neutral
        }
        return voice_map.get(gender, 'Matthew')

    async def synthesize_for_gender(self, text: str, gender: str = "neutral") -> bytes:
        """Synthesize speech with automatic voice selection based on gender."""
        voice_id = self.get_voice_for_gender(gender or "neutral")
        return await self.synthesize_speech(text=text, voice_id=voice_id)


# Global Polly service instance
polly_service = PollyService()
