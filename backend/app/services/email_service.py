"""Email service using Resend for sending invite and notification emails."""
import resend
from typing import Optional
from app.config import settings


# Initialize Resend with API key
resend.api_key = settings.resend_api_key

# Email sender configuration
FROM_EMAIL = "Life Words <noreply@parrotsoftware.com>"


def get_first_name(full_name: str) -> str:
    """Extract first name from full name."""
    if not full_name:
        return "there"
    return full_name.split()[0]


async def send_invite_email(
    recipient_email: str,
    recipient_name: str,
    inviter_full_name: str,
    invite_url: str,
    custom_message: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """Send an invite email to a contact asking them to fill out their information.

    Args:
        recipient_email: Email address of the recipient
        recipient_name: Name of the recipient
        inviter_full_name: Full name of the user sending the invite
        invite_url: URL to the invite form
        custom_message: Optional custom message from the inviter

    Returns:
        Tuple of (success, error_message). error_message is None if successful.
    """
    inviter_first_name = get_first_name(inviter_full_name)
    recipient_first_name = get_first_name(recipient_name)

    subject = f"{inviter_first_name} wants you to help with their memory recovery"

    # Build the email body
    message_section = ""
    if custom_message:
        message_section = f"""
            <p style="font-size: 16px; color: #475569; margin-bottom: 16px;">
                {custom_message}
            </p>
        """

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 32px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h1 style="color: #1e293b; font-size: 24px; margin-bottom: 24px;">Hello {recipient_first_name},</h1>

            {message_section}

            <p style="font-size: 16px; color: #475569; margin-bottom: 24px;">
                It only takes a few minutes and would mean a lot to {inviter_first_name}'s recovery journey.
            </p>

            <div style="text-align: center; margin: 32px 0;">
                <a href="{invite_url}"
                   style="display: inline-block; background-color: #3b82f6; color: #ffffff; text-decoration: none; padding: 16px 32px; border-radius: 8px; font-size: 18px; font-weight: 600;">
                    Add My Information
                </a>
            </div>

            <p style="font-size: 14px; color: #94a3b8; margin-top: 32px;">
                This link will expire in 30 days. If you have any questions, please reach out to {inviter_first_name} directly.
            </p>

            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 32px 0;">

            <p style="font-size: 12px; color: #94a3b8; text-align: center;">
                This email was sent by Life Words, a memory rehabilitation tool by Parrot Software.<br>
                If you received this email in error, you can safely ignore it.
            </p>
        </div>
    </body>
    </html>
    """

    try:
        result = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [recipient_email],
            "subject": subject,
            "html": html_body,
        })
        print(f"Email sent successfully: {result}")
        return True, None
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Failed to send invite email: {error_msg}")
        print(f"Error type: {type(e).__name__}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False, error_msg


async def send_thank_you_email(
    recipient_email: str,
    recipient_name: str,
    inviter_full_name: str
) -> bool:
    """Send a thank you email after someone completes the invite form.

    Args:
        recipient_email: Email address of the recipient
        recipient_name: Name of the recipient (what they entered in the form)
        inviter_full_name: Full name of the user who sent the invite

    Returns:
        True if email was sent successfully, False otherwise
    """
    inviter_first_name = get_first_name(inviter_full_name)
    recipient_first_name = get_first_name(recipient_name)

    subject = f"Thank you for helping {inviter_first_name}!"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 32px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 24px;">
                <span style="font-size: 48px;">🙏</span>
            </div>

            <h1 style="color: #1e293b; font-size: 24px; margin-bottom: 24px; text-align: center;">Thank You, {recipient_first_name}!</h1>

            <p style="font-size: 16px; color: #475569; margin-bottom: 16px;">
                Your information has been successfully added to <strong>{inviter_first_name}'s</strong> memory practice exercises.
            </p>

            <p style="font-size: 16px; color: #475569; margin-bottom: 16px;">
                Your support means so much. By taking the time to help, you're making a real difference in
                {inviter_first_name}'s rehabilitation journey. Practicing with photos and information about
                familiar people is one of the most effective ways to support memory recovery.
            </p>

            <div style="background-color: #f0fdf4; border-radius: 8px; padding: 20px; margin: 24px 0; text-align: center;">
                <p style="margin: 0; color: #166534; font-size: 16px;">
                    ✓ Your photo and information have been saved
                </p>
            </div>

            <p style="font-size: 14px; color: #94a3b8; margin-top: 32px;">
                If you have any questions about {inviter_first_name}'s treatment, please reach out to them directly.
            </p>

            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 32px 0;">

            <p style="font-size: 12px; color: #94a3b8; text-align: center;">
                This email was sent by Life Words, a memory rehabilitation tool by Parrot Software.
            </p>
        </div>
    </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [recipient_email],
            "subject": subject,
            "html": html_body,
        })
        return True
    except Exception as e:
        print(f"Failed to send thank you email: {e}")
        return False
