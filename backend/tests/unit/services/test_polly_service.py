"""Unit tests for Amazon Polly TTS service."""
import pytest
from fastapi import HTTPException

from app.services.polly_service import PollyService


def test_get_voice_for_gender_male():
    """Test male voice selection."""
    service = PollyService()
    assert service.get_voice_for_gender("male") == "Matthew"


def test_get_voice_for_gender_female():
    """Test female voice selection."""
    service = PollyService()
    assert service.get_voice_for_gender("female") == "Joanna"


def test_get_voice_for_gender_neutral():
    """Test neutral voice selection."""
    service = PollyService()
    assert service.get_voice_for_gender("neutral") == "Matthew"


def test_get_voice_for_gender_unknown():
    """Test unknown gender defaults to Matthew."""
    service = PollyService()
    assert service.get_voice_for_gender("other") == "Matthew"


def test_get_client_creates_boto3_client(mocker):
    """Test _get_client creates a boto3 Polly client."""
    mock_boto = mocker.patch("app.services.polly_service.boto3.client")
    mock_boto.return_value = mocker.MagicMock()

    service = PollyService()
    client = service._get_client()

    mock_boto.assert_called_once_with(
        "polly",
        aws_access_key_id=mocker.ANY,
        aws_secret_access_key=mocker.ANY,
        region_name=mocker.ANY,
    )
    assert client is mock_boto.return_value


def test_get_client_returns_cached(mocker):
    """Test _get_client returns cached client on second call."""
    mock_boto = mocker.patch("app.services.polly_service.boto3.client")
    mock_boto.return_value = mocker.MagicMock()

    service = PollyService()
    client1 = service._get_client()
    client2 = service._get_client()

    assert client1 is client2
    mock_boto.assert_called_once()  # Only created once


@pytest.mark.asyncio
async def test_synthesize_speech_success(mocker):
    """Test successful speech synthesis returns audio bytes."""
    mock_stream = mocker.MagicMock()
    mock_stream.read.return_value = b"fake-audio-bytes"

    mock_client = mocker.MagicMock()
    mock_client.synthesize_speech.return_value = {"AudioStream": mock_stream}

    service = PollyService()
    mocker.patch.object(service, "_get_client", return_value=mock_client)

    result = await service.synthesize_speech("Hello world")

    assert result == b"fake-audio-bytes"
    mock_client.synthesize_speech.assert_called_once_with(
        Text="Hello world",
        OutputFormat="mp3",
        VoiceId="Matthew",
        LanguageCode="en-US",
        Engine="neural",
    )


@pytest.mark.asyncio
async def test_synthesize_speech_custom_params(mocker):
    """Test speech synthesis with custom parameters."""
    mock_stream = mocker.MagicMock()
    mock_stream.read.return_value = b"audio"

    mock_client = mocker.MagicMock()
    mock_client.synthesize_speech.return_value = {"AudioStream": mock_stream}

    service = PollyService()
    mocker.patch.object(service, "_get_client", return_value=mock_client)

    await service.synthesize_speech(
        "Test", voice_id="Joanna", language_code="en-GB", engine="standard"
    )

    mock_client.synthesize_speech.assert_called_once_with(
        Text="Test",
        OutputFormat="mp3",
        VoiceId="Joanna",
        LanguageCode="en-GB",
        Engine="standard",
    )


@pytest.mark.asyncio
async def test_synthesize_speech_error(mocker):
    """Test speech synthesis error raises HTTPException and logs."""
    mock_client = mocker.MagicMock()
    mock_client.synthesize_speech.side_effect = RuntimeError("AWS error")

    service = PollyService()
    mocker.patch.object(service, "_get_client", return_value=mock_client)
    mock_log = mocker.patch("app.services.polly_service.log_error")

    with pytest.raises(HTTPException) as exc_info:
        await service.synthesize_speech("Hello")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Text-to-speech failed"
    mock_log.assert_called_once()
    assert mock_log.call_args[1]["source"] == "swallowed"


@pytest.mark.asyncio
async def test_synthesize_for_gender_calls_correct_voice(mocker):
    """Test synthesize_for_gender picks the right voice and delegates."""
    mock_stream = mocker.MagicMock()
    mock_stream.read.return_value = b"audio"

    mock_client = mocker.MagicMock()
    mock_client.synthesize_speech.return_value = {"AudioStream": mock_stream}

    service = PollyService()
    mocker.patch.object(service, "_get_client", return_value=mock_client)

    result = await service.synthesize_for_gender("Hello", "female")

    assert result == b"audio"
    assert mock_client.synthesize_speech.call_args[1]["VoiceId"] == "Joanna"


@pytest.mark.asyncio
async def test_synthesize_for_gender_none_defaults_neutral(mocker):
    """Test synthesize_for_gender defaults to neutral when None."""
    mock_stream = mocker.MagicMock()
    mock_stream.read.return_value = b"audio"

    mock_client = mocker.MagicMock()
    mock_client.synthesize_speech.return_value = {"AudioStream": mock_stream}

    service = PollyService()
    mocker.patch.object(service, "_get_client", return_value=mock_client)

    await service.synthesize_for_gender("Hello", None)

    assert mock_client.synthesize_speech.call_args[1]["VoiceId"] == "Matthew"
