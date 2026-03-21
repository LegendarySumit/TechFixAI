"""
Access-control helpers for authenticated and admin-only routes.
"""

from fastapi import Depends, HTTPException, Request, status

from app.core.config import settings


def get_current_user_or_401(request: Request):
    user = getattr(request.state, "current_user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


def is_admin_email(email: str) -> bool:
    normalized = (email or "").strip().lower()
    if not normalized:
        return False

    raw_admins = settings.ADMIN_EMAILS
    if isinstance(raw_admins, str):
        admin_emails = {e.strip().lower() for e in raw_admins.split(",") if e.strip()}
    elif isinstance(raw_admins, (list, tuple, set)):
        admin_emails = {str(e).strip().lower() for e in raw_admins if str(e).strip()}
    else:
        admin_emails = set()

    if not admin_emails:
        return False

    return normalized in admin_emails


def require_admin_user(user=Depends(get_current_user_or_401)):
    if not is_admin_email(getattr(user, "email", "")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
