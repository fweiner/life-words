"""Integration tests for speech (Amazon Polly TTS) endpoints."""


def test_tts_empty_text(client):
    """Test TTS with empty text returns 422 (validation error)."""
    response = client.post("/api/speech/tts", json={"text": "", "gender": "neutral"})
    assert response.status_code == 422


def test_tts_missing_text(client):
    """Test TTS with missing text field returns 422."""
    response = client.post("/api/speech/tts", json={"gender": "neutral"})
    assert response.status_code == 422


def test_tts_whitespace_only_text(client):
    """Test TTS with whitespace-only text returns 422."""
    response = client.post("/api/speech/tts", json={"text": "   ", "gender": "neutral"})
    assert response.status_code == 422


def test_tts_success(client, mocker):
    """Test successful TTS request returns audio bytes."""
    fake_audio = b"fake-mp3-audio-content"

    async def mock_synthesize_for_gender(text, gender="neutral"):
        return fake_audio

    mocker.patch(
        "app.services.polly_service.polly_service.synthesize_for_gender",
        side_effect=mock_synthesize_for_gender,
    )

    response = client.post("/api/speech/tts", json={"text": "Hello world"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == fake_audio


def test_tts_with_gender(client, mocker):
    """Test TTS with specific gender preference."""
    fake_audio = b"fake-mp3-audio-content"

    async def mock_synthesize_for_gender(text, gender="neutral"):
        assert gender == "female"
        return fake_audio

    mocker.patch(
        "app.services.polly_service.polly_service.synthesize_for_gender",
        side_effect=mock_synthesize_for_gender,
    )

    response = client.post(
        "/api/speech/tts",
        json={"text": "Hello world", "gender": "female"},
    )

    assert response.status_code == 200
    assert response.content == fake_audio


def test_tts_default_gender(client, mocker):
    """Test TTS defaults to neutral gender when not specified."""
    fake_audio = b"fake-mp3-audio-content"

    async def mock_synthesize_for_gender(text, gender="neutral"):
        assert gender == "neutral"
        return fake_audio

    mocker.patch(
        "app.services.polly_service.polly_service.synthesize_for_gender",
        side_effect=mock_synthesize_for_gender,
    )

    response = client.post("/api/speech/tts", json={"text": "Hello"})

    assert response.status_code == 200


def test_tts_service_error(client, mocker):
    """Test TTS returns 500 when Polly service fails and logs error."""
    async def mock_synthesize_error(text, gender="neutral"):
        raise RuntimeError("AWS Polly unavailable")

    mocker.patch(
        "app.services.polly_service.polly_service.synthesize_for_gender",
        side_effect=mock_synthesize_error,
    )
    mock_log_error = mocker.patch("app.routers.speech.log_error")

    response = client.post("/api/speech/tts", json={"text": "Hello"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Text-to-speech failed"
    mock_log_error.assert_called_once()
    call_kwargs = mock_log_error.call_args[1]
    assert call_kwargs["source"] == "swallowed"
    assert call_kwargs["service_name"] == "PollyService"


def test_tts_cache_control_header(client, mocker):
    """Test TTS response includes cache control header."""
    async def mock_synthesize_for_gender(text, gender="neutral"):
        return b"audio"

    mocker.patch(
        "app.services.polly_service.polly_service.synthesize_for_gender",
        side_effect=mock_synthesize_for_gender,
    )

    response = client.post("/api/speech/tts", json={"text": "Hello"})

    assert response.status_code == 200
    assert "max-age=86400" in response.headers.get("cache-control", "")
