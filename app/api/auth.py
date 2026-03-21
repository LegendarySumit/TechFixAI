"""
Google OAuth authentication routes.
"""

from datetime import datetime
from urllib.parse import urlparse
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

from app.db.session import SessionLocal
from app.models.user import User
from app.core.config import settings
from app.core.session import set_session_cookie
from app.core.captcha import verify_captcha_token
from app.core.auth_guard import get_request_ip
from app.services.product_analytics import track_product_event

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def _build_google_redirect_uri(request: Request) -> str:
    """Build a deterministic OAuth callback URL to avoid redirect_uri mismatches."""
    configured_redirect = (settings.GOOGLE_REDIRECT_URI or "").strip()
    if configured_redirect:
        return configured_redirect

    configured_base = (settings.APP_BASE_URL or "").strip().rstrip("/")
    if configured_base:
        return f"{configured_base}/auth/google/callback"

    dynamic_redirect = str(request.url_for("google_callback"))
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",")[0].strip().lower()
    if forwarded_proto == "https":
        dynamic_redirect = dynamic_redirect.replace("http://", "https://", 1)
    return dynamic_redirect


def _is_local_host(hostname: str) -> bool:
    return (hostname or "").lower() in {"localhost", "127.0.0.1", "::1"}


def _maybe_redirect_to_canonical_oauth_host(request: Request, redirect_uri: str):
    """
    If auth starts on 127.0.0.1 but callback is configured for localhost (or vice versa),
    OAuth state cookie will mismatch by domain. Redirect first to canonical host.
    """
    parsed = urlparse(redirect_uri)
    callback_host = (parsed.hostname or "").lower()
    request_host = (request.url.hostname or "").lower()

    if not callback_host or not request_host:
        return None

    if callback_host == request_host:
        return None

    if _is_local_host(callback_host) and _is_local_host(request_host):
        canonical_url = f"{parsed.scheme}://{parsed.netloc}{request.url.path}"
        return RedirectResponse(url=canonical_url, status_code=307)

    return None


@router.get("/auth/google")
async def google_login(request: Request):
    """Redirect to Google OAuth consent screen."""
    source = request.query_params.get("source", "login")
    if settings.CAPTCHA_ENABLED and (settings.CAPTCHA_REQUIRED_LOGIN or settings.CAPTCHA_REQUIRED_SIGNUP):
        captcha_token = str(request.query_params.get("captcha_token", "")).strip()
        captcha_ok, _ = await verify_captcha_token(captcha_token, get_request_ip(request))
        if not captcha_ok:
            if source == "signup":
                return RedirectResponse(url="/signup?error=captcha_required", status_code=303)
            return RedirectResponse(url="/login?error=captcha_required", status_code=303)

    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        return RedirectResponse(url="/login?error=oauth_not_configured")

    track_product_event(
        event_name="google_oauth_started",
        session_id=request.cookies.get(settings.SESSION_COOKIE_NAME),
        ip_address=get_request_ip(request),
        properties={"source": source},
    )

    redirect_uri = _build_google_redirect_uri(request)
    canonical_host_redirect = _maybe_redirect_to_canonical_oauth_host(request, redirect_uri)
    if canonical_host_redirect:
        return canonical_host_redirect

    print(f"🔐 OAuth redirect_uri: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback", name="google_callback")
async def google_callback(request: Request):
    """Handle the OAuth callback from Google."""
    # Check for errors
    if request.query_params.get("error"):
        return RedirectResponse(url="/login?error=google_denied")

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        print(f"❌ OAuth callback error: {type(e).__name__}: {str(e)}")
        if "mismatching_state" in str(e).lower() or "mismatchingstateerror" in type(e).__name__.lower():
            return RedirectResponse(url="/login?error=oauth_state_mismatch")
        return RedirectResponse(url=f"/login?error=oauth_failed")

    user_info = token.get("userinfo")
    if not user_info:
        return RedirectResponse(url="/login?error=no_profile")

    email = user_info.get("email", "")
    google_id = user_info.get("sub", "")
    full_name = user_info.get("name", email.split("@")[0])
    picture = user_info.get("picture", "")

    if not email:
        return RedirectResponse(url="/login?error=no_email")

    db = SessionLocal()
    try:
        # Find by google_id first, then fall back to email
        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = db.query(User).filter(User.email == email).first()

        if user:
            # Update OAuth fields on existing account
            if not user.google_id:
                user.google_id = google_id
            if picture and not user.picture_url:
                user.picture_url = picture
            if not user.password_changed_at:
                user.password_changed_at = datetime.utcnow()
            user.last_login = datetime.utcnow()
            db.commit()
        else:
            # Create a new account — derive a unique username from email
            base = email.split("@")[0].replace(".", "_").replace("-", "_")[:24]
            username, counter = base, 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password="",   # OAuth users have no password
                google_id=google_id,
                picture_url=picture,
                is_active=True,
                is_verified=True,
                last_login=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        response = RedirectResponse(url="/dashboard", status_code=303)
        set_session_cookie(response, user, remember=True)
        track_product_event(
            event_name="google_oauth_completed",
            user_id=user.id,
            user_email=user.email,
            ip_address=get_request_ip(request),
        )
        return response
    except Exception as e:
        import traceback
        print(f"❌ OAuth DB error: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        return RedirectResponse(url="/login?error=oauth_failed")
    finally:
        db.close()
