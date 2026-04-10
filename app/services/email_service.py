"""
Email service for sending verification emails.
Uses Python's built-in smtplib — no extra packages needed.
Configure via env vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, APP_BASE_URL
"""

import smtplib
import secrets
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def generate_verification_token() -> tuple[str, datetime]:
    """Generate a secure token and its 24-hour expiry."""
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=24)
    return token, expires


def _get_base_url(request=None) -> str:
    """Get the base URL — from env var, or from request, or localhost fallback."""
    if settings.APP_BASE_URL:
        return settings.APP_BASE_URL.rstrip("/")
    if request:
      # Build from request: respect forwarded proto/host when behind a reverse proxy
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("x-forwarded-host", request.url.netloc)
        return f"{scheme}://{host}"
    return "http://localhost:8000"


def send_verification_email(to_email: str, token: str, full_name: str, request=None) -> bool:
    """
    Send email verification link to user.
    Returns True on success, False on failure (non-fatal — user can request resend).
    
    POLICY: Email verification is DISABLED by default. Users are auto-verified on signup.
    Only call this function if email delivery is explicitly required.
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"ℹ️ [Email] Email sending is disabled (SMTP not fully configured). User {to_email} will not receive verification email.")
        print(f"   This is expected behavior — users are auto-verified on signup.")
        return False
    
    # Safety check: only send if all SMTP vars are non-empty strings
    if not all([settings.SMTP_HOST.strip(), settings.SMTP_USER.strip(), settings.SMTP_PASSWORD.strip()]):
        print(f"❌ [Email] SMTP configuration incomplete — aborting email send to {to_email}")
        return False

    base_url = _get_base_url(request)
    verify_url = f"{base_url}/verify-email?token={token}"
    from_email = settings.FROM_EMAIL or settings.SMTP_USER

    # Build HTML email
    html_body = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px;">
  <div style="max-width: 520px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 40px; border: 1px solid #334155;">
    <h2 style="color: #38bdf8; margin-top: 0;">Verify your TechFixAI email</h2>
    <p>Hi {full_name},</p>
    <p>Thanks for signing up! Click the button below to verify your email address and activate your account.</p>
    <p style="margin: 32px 0; text-align: center;">
      <a href="{verify_url}"
         style="background: #38bdf8; color: #0f172a; text-decoration: none;
                padding: 14px 32px; border-radius: 8px; font-weight: bold; font-size: 16px;">
        Verify Email Address
      </a>
    </p>
    <p style="color: #94a3b8; font-size: 13px;">
      This link expires in 24 hours.<br>
      If you didn't sign up, you can ignore this email.
    </p>
    <hr style="border-color: #334155; margin: 24px 0;">
    <p style="color: #64748b; font-size: 12px;">
      Or copy this link into your browser:<br>
      <span style="color: #38bdf8;">{verify_url}</span>
    </p>
  </div>
</body>
</html>
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Verify your TechFixAI account"
        msg["From"] = f"TechFixAI <{from_email}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(from_email, to_email, msg.as_string())

        print(f"✅ [Email] Verification email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ [Email] Failed to send verification email to {to_email}: {type(e).__name__}: {e}")
        return False
