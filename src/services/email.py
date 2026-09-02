import smtplib
from email.message import EmailMessage

from src.config import get_settings


def send_password_reset_email(recipient: str, reset_url: str) -> bool:
    """Deliver a password reset link when SMTP is configured."""
    settings = get_settings()
    if not settings.smtp_host or not settings.email_from:
        return False

    message = EmailMessage()
    message["Subject"] = "Reset your MemoryChat password"
    message["From"] = settings.email_from
    message["To"] = recipient
    message.set_content(
        "We received a request to reset your MemoryChat password. "
        f"Use this link within {settings.password_reset_token_minutes} minutes:\n\n"
        f"{reset_url}\n\n"
        "If you did not request this, you can safely ignore this email."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
    return True
