"""
Google OAuth authentication routes.
"""

from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

from app.db.session import SessionLocal
from app.models.user import User
from app.core.config import settings

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/auth/google")
async def google_login(request: Request):
    """Redirect to Google OAuth consent screen."""
    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        return RedirectResponse(url="/login?error=oauth_not_configured")
    redirect_uri = settings.GOOGLE_REDIRECT_URI
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
        response.set_cookie(
            key="user_session",
            value=user.email,
            max_age=30 * 24 * 60 * 60,   # 30 days
            httponly=True,
            samesite="lax",
        )
        return response
    finally:
        db.close()
