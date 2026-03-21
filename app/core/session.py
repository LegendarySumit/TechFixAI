"""
Session helpers for signed auth cookies.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings
from app.models.user import User


SESSION_SALT = "techfixai.user-session.v1"


def _serializer() -> URLSafeTimedSerializer:
    secret = settings.SECRET_KEY or "techfixai-dev-insecure-secret"
    return URLSafeTimedSerializer(secret_key=secret, salt=SESSION_SALT)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _password_marker(user: User) -> int:
    changed_at = _to_utc(user.password_changed_at)
    if changed_at is None:
        return 0
    return int(changed_at.timestamp() * 1_000_000)


def _session_lifetime_seconds(remember: bool = False) -> int:
    if remember:
        return max(1, settings.SESSION_REMEMBER_DAYS) * 24 * 60 * 60
    return max(1, settings.SESSION_TTL_HOURS) * 60 * 60


def set_session_cookie(response: Response, user: User, remember: bool = False) -> None:
    now_ts = int(_utc_now().timestamp())
    ttl_seconds = _session_lifetime_seconds(remember=remember)
    payload = {
        "sub": user.email.lower().strip(),
        "iat": now_ts,
        "exp": now_ts + ttl_seconds,
        "pwd": _password_marker(user),
    }
    token = _serializer().dumps(payload)

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=ttl_seconds,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=settings.SESSION_COOKIE_NAME, path="/")


def decode_session_cookie(token: str) -> Optional[dict]:
    if not token:
        return None

    max_possible_age = max(
        _session_lifetime_seconds(remember=False),
        _session_lifetime_seconds(remember=True),
    )

    try:
        payload = _serializer().loads(token, max_age=max_possible_age)
    except (BadSignature, SignatureExpired, ValueError, TypeError):
        return None

    if not isinstance(payload, dict):
        return None

    try:
        exp_ts = int(payload.get("exp", 0))
    except (TypeError, ValueError):
        return None

    if exp_ts <= int(_utc_now().timestamp()):
        return None

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        return None

    return payload


def is_session_payload_valid_for_user(payload: dict, user: User) -> bool:
    subject = str(payload.get("sub", "")).lower().strip()
    if subject != user.email.lower().strip():
        return False

    try:
        session_pwd_marker = int(payload.get("pwd", -1))
    except (TypeError, ValueError):
        return False

    return session_pwd_marker == _password_marker(user)
