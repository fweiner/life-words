"""Google Cloud Speech services."""
import base64
from typing import Optional
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech
from app.config import settings
from app.core.error_logger import log_error


class SpeechService:
    """Service for speech-to-text and text-to-speech."""

    def __init__(self):
        """Initialize Google Cloud clients."""
        # Clients will use GOOGLE_APPLICATION_CREDENTIALS env var
        self.speech_client = None
        self.tts_client = None

    def _get_speech_client(self) -> speech.SpeechClient:
        """Get or create speech client."""
        if self.speech_client is None:
            self.speech_client = speech.SpeechClient()
        return self.speech_client

    def _get_tts_client(self) -> texttospeech.TextToSpeechClient:
        """Get or create text-to-speech client."""
        if self.tts_client is None:
            self.tts_client = texttospeech.TextToSpeechClient()
        return self.tts_client

    async def speech_to_text(
        self,
        audio_content: bytes,
        language_code: str = "en-US"
    ) -> tuple[str, Optional[float]]:
        """
        Convert speech audio to text.

        Args:
            audio_content: Audio file content in bytes
            language_code: Language code (default: en-US)

        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        client = self._get_speech_client()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )

        try:
            response = client.recognize(config=config, audio=audio)

            if not response.results:
                return "", None

            # Get the first result (most confident)
            result = response.results[0]
            alternative = result.alternatives[0]

            return alternative.transcript, alternative.confidence

        except Exception as e:
            log_error(
                error=e,
                source="swallowed",
                service_name="SpeechService",
                function_name="speech_to_text",
            )
            raise

    async def text_to_speech(
        self,
        text: str,
        language_code: str = "en-US",
        voice_name: Optional[str] = None
    ) -> bytes:
        """
        Convert text to speech audio.

        Args:
            text: Text to convert to speech
            language_code: Language code (default: en-US)
            voice_name: Optional specific voice name

        Returns:
            Audio content as bytes (MP3 format)
        """
        client = self._get_tts_client()

        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Use default voice if not specified
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,  # Slightly slower for elderly users
            pitch=0.0
        )

        try:
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            return response.audio_content

        except Exception as e:
            log_error(
                error=e,
                source="swallowed",
                service_name="SpeechService",
                function_name="text_to_speech",
            )
            raise


# Global speech service instance
speech_service = SpeechService()
