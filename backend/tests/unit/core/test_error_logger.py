"""Unit tests for the fire-and-forget error logger."""
import asyncio
import pytest

from app.core.error_logger import _sanitize, _truncate, log_error


def test_sanitize_redacts_password():
    """Test that password fields are redacted."""
    data = {"username": "fred", "password": "secret123"}
    result = _sanitize(data)
    assert result["username"] == "fred"
    assert result["password"] == "***REDACTED***"


def test_sanitize_redacts_nested_tokens():
    """Test that nested sensitive fields are redacted."""
    data = {
        "user": {
            "name": "fred",
            "access_token": "abc123",
            "refresh_token": "def456",
        }
    }
    result = _sanitize(data)
    assert result["user"]["name"] == "fred"
    assert result["user"]["access_token"] == "***REDACTED***"
    assert result["user"]["refresh_token"] == "***REDACTED***"


def test_sanitize_redacts_api_key():
    """Test that api_key fields are redacted."""
    data = {"api_key": "sk-123", "endpoint": "/test"}
    result = _sanitize(data)
    assert result["api_key"] == "***REDACTED***"
    assert result["endpoint"] == "/test"


def test_sanitize_handles_lists():
    """Test that lists of dicts are sanitized."""
    data = [
        {"token": "abc", "name": "item1"},
        {"secret": "xyz", "name": "item2"},
    ]
    result = _sanitize(data)
    assert result[0]["token"] == "***REDACTED***"
    assert result[0]["name"] == "item1"
    assert result[1]["secret"] == "***REDACTED***"
    assert result[1]["name"] == "item2"


def test_sanitize_passes_through_primitives():
    """Test that non-dict/list values pass through unchanged."""
    assert _sanitize("hello") == "hello"
    assert _sanitize(42) == 42
    assert _sanitize(None) is None
    assert _sanitize(True) is True


def test_sanitize_empty_dict():
    """Test sanitizing an empty dict."""
    assert _sanitize({}) == {}


def test_sanitize_case_insensitive():
    """Test that key matching is case insensitive."""
    data = {"Password": "secret", "API_KEY": "key123"}
    result = _sanitize(data)
    assert result["Password"] == "***REDACTED***"
    assert result["API_KEY"] == "***REDACTED***"


def test_truncate_short_string():
    """Test that short strings are not truncated."""
    assert _truncate("hello", 100) == "hello"


def test_truncate_exact_limit():
    """Test that strings at exactly the limit are not truncated."""
    assert _truncate("12345", 5) == "12345"


def test_truncate_long_string():
    """Test that long strings are truncated with a note."""
    result = _truncate("a" * 200, 50)
    assert len(result) > 50  # includes truncation note
    assert result.startswith("a" * 50)
    assert "truncated" in result
    assert "200 chars total" in result


def test_truncate_none():
    """Test that None passes through."""
    assert _truncate(None, 100) is None


def test_log_error_with_exception(mocker):
    """Test log_error fires a task when given an Exception."""
    mock_task = mocker.MagicMock()
    mock_loop = mocker.MagicMock()
    mock_loop.create_task = mocker.MagicMock(return_value=mock_task)
    mocker.patch("app.core.error_logger.asyncio.get_running_loop", return_value=mock_loop)

    try:
        raise ValueError("test error")
    except ValueError as e:
        log_error(
            error=e,
            source="unhandled",
            endpoint="/api/test",
            http_method="GET",
            status_code=500,
        )

    mock_loop.create_task.assert_called_once()


def test_log_error_with_string(mocker):
    """Test log_error fires a task when given a string error."""
    mock_task = mocker.MagicMock()
    mock_loop = mocker.MagicMock()
    mock_loop.create_task = mocker.MagicMock(return_value=mock_task)
    mocker.patch("app.core.error_logger.asyncio.get_running_loop", return_value=mock_loop)

    log_error(
        error="Something went wrong",
        source="manual",
        service_name="TestService",
        function_name="do_thing",
    )

    mock_loop.create_task.assert_called_once()


def test_log_error_no_event_loop(mocker):
    """Test log_error falls back to logging when no event loop is running."""
    mocker.patch(
        "app.core.error_logger.asyncio.get_running_loop",
        side_effect=RuntimeError("no running loop"),
    )
    mock_logger = mocker.patch("app.core.error_logger.logger")

    log_error(error="test error", source="manual")

    mock_logger.error.assert_called_once()


def test_log_error_never_raises(mocker):
    """Test that log_error never raises, even if everything fails."""
    mocker.patch(
        "app.core.error_logger.asyncio.get_running_loop",
        side_effect=RuntimeError("no loop"),
    )
    mocker.patch(
        "app.core.error_logger.logger.error",
        side_effect=Exception("logging also broken"),
    )

    # Should not raise
    log_error(error="test", source="manual")


def test_log_error_sanitizes_request_body(mocker):
    """Test that request body is sanitized before logging."""
    mock_task = mocker.MagicMock()
    mock_loop = mocker.MagicMock()
    mock_loop.create_task = mocker.MagicMock(return_value=mock_task)
    mocker.patch("app.core.error_logger.asyncio.get_running_loop", return_value=mock_loop)

    mock_insert = mocker.patch("app.core.error_logger._insert_error_log")

    log_error(
        error="test",
        source="manual",
        request_body={"password": "secret", "username": "fred"},
    )

    # Get the data dict passed to _insert_error_log via create_task
    call_args = mock_loop.create_task.call_args
    # create_task is called with the coroutine from _insert_error_log(data)
    # We can verify by checking that _insert_error_log was called
    mock_insert.assert_called_once()
    data = mock_insert.call_args[0][0]
    assert data["request_body"]["password"] == "***REDACTED***"
    assert data["request_body"]["username"] == "fred"


@pytest.mark.asyncio
async def test_insert_error_log_success(mocker):
    """Test _insert_error_log POSTs to Supabase."""
    from app.core.error_logger import _insert_error_log

    mock_response = mocker.MagicMock()
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.post = mocker.AsyncMock(return_value=mock_response)

    mocker.patch("app.core.error_logger.httpx.AsyncClient", return_value=mock_client)

    await _insert_error_log({"error_message": "test"})

    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert "error_logs" in call_args[0][0]
    assert call_args.kwargs["json"] == {"error_message": "test"}


@pytest.mark.asyncio
async def test_insert_error_log_handles_failure(mocker):
    """Test _insert_error_log catches exceptions and logs them."""
    from app.core.error_logger import _insert_error_log

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.post = mocker.AsyncMock(side_effect=Exception("network error"))

    mocker.patch("app.core.error_logger.httpx.AsyncClient", return_value=mock_client)
    mock_logger = mocker.patch("app.core.error_logger.logger")

    # Should not raise
    await _insert_error_log({"error_message": "test"})

    mock_logger.error.assert_called_once()
