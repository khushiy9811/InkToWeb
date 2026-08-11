"""
Sends OTP verification emails to new employees.

No SMTP or email-API credentials are configured for this project, so this
currently runs in dev mode: the OTP is logged to the server console instead
of actually being emailed. Swap the body of send_otp_email() for real SMTP
(smtplib) or an API (Resend, SendGrid, etc.) when credentials are available
— nothing else in the signup/verification flow needs to change.
"""
import logging

from .config import EMAIL_DEV_MODE

logger = logging.getLogger("inktoweb.email")


def send_otp_email(to_email: str, otp: str, full_name: str = "") -> None:
    if not EMAIL_DEV_MODE:
        raise NotImplementedError(
            "EMAIL_DEV_MODE is off but no real email provider is wired up yet."
        )

    logger.warning("[DEV MODE] OTP for %s: %s", to_email, otp)
    print(
        f"\n{'=' * 60}\n"
        f"[DEV MODE — no email service configured]\n"
        f"Verification code for {full_name or to_email} <{to_email}>: {otp}\n"
        f"{'=' * 60}\n"
    )
