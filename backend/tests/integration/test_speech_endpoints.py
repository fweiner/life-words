"""Integration tests for speech (Amazon Polly TTS) endpoints."""


def _setup_auth(app):
    """Add auth override for speech endpoints."""
    from app.core.auth import get_current_user_id

    async def override_get_current_user_id():
        return "test-user-123"

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id


def test_tts_unauthorized(client):
    """Test TTS without authentication returns 401."""
    response = client.post("/api/speech/tts", json={"text": "Hello", "gender": "neutral"})
    assert response.status_code == 401


def test_tts_empty_text(app, client):
    """Test TTS with empty text returns 422 (validation error)."""
    _setup_auth(app)
    response = client.post(
        "/api/speech/tts",
        json={"text": "", "gender": "neutral"},
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 422


def test_tts_missing_text(app, client):
    """Test TTS with missing text field returns 422."""
    _setup_auth(app)
    response = client.post(
        "/api/speech/tts",
        json={"gender": "neutral"},
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 422


def test_tts_whitespace_only_text(app, client):
    """Test TTS with whitespace-only text returns 422."""
    _setup_auth(app)
    response = client.post(
        "/api/speech/tts",
        json={"text": "   ", "gender": "neutral"},
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 422


def test_tts_success(app, client, mocker):
    """Test successful TTS request returns audio bytes."""
    _setup_auth(app)
    fake_audio = b"fake-mp3-audio-content"

    async def mock_synthesize_for_gender(text, gender="neutral"):
        return fake_audio

    mocker.patch(
        "app.services.polly_service.polly_service.synthesize_for_gender",
        side_effect=mock_synthesize_for_gender,
    )

    response = client.post(
        "/api/speech/tts",
        json={"text": "Hello world"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == fake_audio


def test_tts_with_gender(app, client, mocker):
    """Test TTS with specific gender preference."""
    _setup_auth(app)
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
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.content == fake_audio


def test_tts_default_gender(app, client, mocker):
    """Test TTS defaults to neutral gender when not specified."""
    _setup_auth(app)
    fake_audio = b"fake-mp3-audio-content"

    async def mock_synthesize_for_gender(text, gender="neutral"):
        assert gender == "neutral"
        return fake_audio

    mocker.patch(
        "app.services.polly_service.polly_service.synthesize_for_gender",
        side_effect=mock_synthesize_for_gender,
    )

    response = client.post(
        "/api/speech/tts",
        json={"text": "Hello"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200


def test_tts_service_error(app, client, mocker):
    """Test TTS returns 500 when Polly service fails and logs error."""
    _setup_auth(app)
    from app.services.polly_service import polly_service

    # Mock the boto3 client to simulate AWS failure
    mock_boto_client = mocker.MagicMock()
    mock_boto_client.synthesize_speech.side_effect = RuntimeError("AWS Polly unavailable")
    mocker.patch.object(polly_service, "_get_client", return_value=mock_boto_client)

    mock_log_error = mocker.patch("app.services.polly_service.log_error")

    response = client.post(
        "/api/speech/tts",
        json={"text": "Hello"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Text-to-speech failed"
    mock_log_error.assert_called_once()
    call_kwargs = mock_log_error.call_args[1]
    assert call_kwargs["source"] == "swallowed"
    assert call_kwargs["service_name"] == "PollyService"


def test_tts_cache_control_header(app, client, mocker):
    """Test TTS response includes cache control header."""
    _setup_auth(app)

    async def mock_synthesize_for_gender(text, gender="neutral"):
        return b"audio"

    mocker.patch(
        "app.services.polly_service.polly_service.synthesize_for_gender",
        side_effect=mock_synthesize_for_gender,
    )

    response = client.post(
        "/api/speech/tts",
        json={"text": "Hello"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert "max-age=86400" in response.headers.get("cache-control", "")
