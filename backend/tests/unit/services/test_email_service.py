"""Unit tests for email service."""
import pytest

from app.services.email_service import (
    get_first_name,
    send_invite_email,
    send_thank_you_email
)


# --- get_first_name ---


def test_get_first_name_single_name():
    """Test with a single name."""
    assert get_first_name("John") == "John"


def test_get_first_name_full_name():
    """Test with first and last name."""
    assert get_first_name("John Doe") == "John"


def test_get_first_name_multiple_names():
    """Test with multiple names."""
    assert get_first_name("John William Doe") == "John"


def test_get_first_name_empty_string():
    """Test with empty string."""
    assert get_first_name("") == "there"


def test_get_first_name_none_like():
    """Test with None-like value."""
    assert get_first_name("") == "there"


# --- send_invite_email ---


@pytest.mark.asyncio
async def test_send_invite_email_success(mocker):
    """Test successful invite email sending."""
    mock_send = mocker.patch("app.services.email_service.resend.Emails.send")
    mock_send.return_value = {"id": "email-123"}

    result = await send_invite_email(
        recipient_email="jane@example.com",
        recipient_name="Jane Smith",
        inviter_full_name="John Doe",
        invite_url="https://example.com/invite/token123",
        custom_message="Please help me with my recovery!"
    )

    success, error = result
    assert success is True
    assert error is None
    mock_send.assert_called_once()

    # Verify email content
    call_args = mock_send.call_args[0][0]
    assert call_args["to"] == ["jane@example.com"]
    assert "John" in call_args["subject"]
    assert "memory" in call_args["subject"].lower()
    assert "Please help me with my recovery!" in call_args["html"]
    assert "https://example.com/invite/token123" in call_args["html"]


@pytest.mark.asyncio
async def test_send_invite_email_without_custom_message(mocker):
    """Test invite email without custom message."""
    mock_send = mocker.patch("app.services.email_service.resend.Emails.send")
    mock_send.return_value = {"id": "email-123"}

    result = await send_invite_email(
        recipient_email="jane@example.com",
        recipient_name="Jane Smith",
        inviter_full_name="John Doe",
        invite_url="https://example.com/invite/token123"
    )

    success, error = result
    assert success is True
    assert error is None
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_send_invite_email_failure(mocker):
    """Test invite email failure."""
    mock_send = mocker.patch("app.services.email_service.resend.Emails.send")
    mock_send.side_effect = Exception("Email service error")
    mocker.patch("app.services.email_service.log_error")

    result = await send_invite_email(
        recipient_email="jane@example.com",
        recipient_name="Jane Smith",
        inviter_full_name="John Doe",
        invite_url="https://example.com/invite/token123"
    )

    success, error = result
    assert success is False
    assert error == "Email service error"


# --- send_thank_you_email ---


@pytest.mark.asyncio
async def test_send_thank_you_email_success(mocker):
    """Test successful thank you email sending."""
    mock_send = mocker.patch("app.services.email_service.resend.Emails.send")
    mock_send.return_value = {"id": "email-456"}

    result = await send_thank_you_email(
        recipient_email="jane@example.com",
        recipient_name="Jane Smith",
        inviter_full_name="John Doe"
    )

    assert result is True
    mock_send.assert_called_once()

    # Verify email content
    call_args = mock_send.call_args[0][0]
    assert call_args["to"] == ["jane@example.com"]
    assert "Thank you" in call_args["subject"]
    assert "John" in call_args["subject"]
    assert "Jane" in call_args["html"]


@pytest.mark.asyncio
async def test_send_thank_you_email_failure(mocker):
    """Test thank you email failure."""
    mock_send = mocker.patch("app.services.email_service.resend.Emails.send")
    mock_send.side_effect = Exception("Email service error")
    mocker.patch("app.services.email_service.log_error")

    result = await send_thank_you_email(
        recipient_email="jane@example.com",
        recipient_name="Jane Smith",
        inviter_full_name="John Doe"
    )

    assert result is False
