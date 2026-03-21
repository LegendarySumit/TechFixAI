"""
Bot verification helpers (Turnstile / hCaptcha-compatible verification flow).
"""

from typing import Tuple

import httpx

from app.core.config import settings


async def verify_captcha_token(token: str, remote_ip: str) -> Tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    """
    if not settings.CAPTCHA_ENABLED:
        return True, ""

    if not settings.CAPTCHA_SECRET_KEY:
        return False, "Captcha is enabled but CAPTCHA_SECRET_KEY is missing."

    if not token:
        return False, "Captcha verification required."

    payload = {
        "secret": settings.CAPTCHA_SECRET_KEY,
        "response": token,
        "remoteip": remote_ip,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(settings.CAPTCHA_VERIFY_URL, data=payload)
            response.raise_for_status()
            result = response.json()
    except Exception:
        return False, "Captcha verification service is unavailable."

    if bool(result.get("success")):
        return True, ""

    error_codes = result.get("error-codes") or result.get("errors") or []
    if isinstance(error_codes, list):
        detail = ", ".join(str(code) for code in error_codes) if error_codes else "invalid-token"
    else:
        detail = str(error_codes)
    return False, f"Captcha verification failed ({detail})."
