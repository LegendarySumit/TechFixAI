"""
Web routes for serving HTML templates.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.config import settings
from app.services.email_service import send_verification_email, generate_verification_token

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    error_map = {
        "oauth_not_configured": "Google OAuth is not configured yet. Use email/password below.",
        "google_denied": "Google sign-in was cancelled.",
        "oauth_failed": "Google sign-in failed. Please try again.",
        "no_profile": "Could not retrieve your Google profile. Please try again.",
        "no_email": "Your Google account has no verified email.",
    }
    error = error_map.get(request.query_params.get("error", ""), "")
    return templates.TemplateResponse("login.html", {"request": request, "error_message": error})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle login form submission."""
    import traceback
    try:
        form_data = await request.form()
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        remember = form_data.get("remember", False)

        # Validate input
        if not email or not password:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error_message": "Email and password are required"},
                status_code=400
            )

        # Find user
        user = db.query(User).filter(User.email == email).first()

        if not user or not user.verify_password(password):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error_message": "Invalid email or password"},
                status_code=401
            )

        if not user.is_active:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error_message": "Account is disabled"},
                status_code=403
            )

        # Block manual-signup users who haven't verified their email.
        # Google OAuth users always have is_verified=True so they are never blocked.
        if not user.is_verified:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error_message": "Please verify your email before logging in. Check your inbox for the verification link.",
                    "show_resend": True,
                    "resend_email": email,
                },
                status_code=403
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Set session cookie
        max_age = 30 * 24 * 60 * 60 if remember else None
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(
            key="user_session",
            value=user.email,
            max_age=max_age,
            httponly=True,
            samesite="lax"
        )
        return response

    except Exception as e:
        print(f"❌ Login error: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": f"Login failed: {type(e).__name__}: {str(e)}"},
            status_code=500
        )


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Sign up page"""
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup", response_class=HTMLResponse)
async def signup_submit(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle signup form submission."""
    import traceback
    try:
        form_data = await request.form()

        email = form_data.get("email", "").strip()
        full_name = form_data.get("full_name", "").strip()
        password = form_data.get("password", "")
        terms = form_data.get("terms")

        # Validate input
        errors = []

        if not email:
            errors.append("Email is required")
        elif "@" not in email or "." not in email:
            errors.append("Please enter a valid email address")

        if not full_name:
            errors.append("Full name is required")

        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters")

        if not terms:
            errors.append("You must agree to the terms of service")

        # Check if email already exists
        if email and db.query(User).filter(User.email == email).first():
            errors.append("An account with this email already exists")

        if errors:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error_message": "; ".join(errors), "email": email, "full_name": full_name},
                status_code=400
            )

        # Auto-generate unique username from email prefix
        base_username = email.split("@")[0].lower().replace(".", "_").replace("+", "_")[:20]
        username = base_username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1

        # Generate verification token (expires 24 h)
        token, expires = generate_verification_token()

        # Create new user — NOT verified yet
        new_user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=User.get_password_hash(password),
            is_active=True,
            is_verified=False,
            verification_token=token,
            verification_token_expires=expires,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Send verification email (non-fatal if SMTP not configured)
        email_sent = send_verification_email(email, token, full_name, request)

        return templates.TemplateResponse(
            "verify_email_sent.html",
            {
                "request": request,
                "email": email,
                "email_sent": email_sent,
            }
        )

    except Exception as e:
        print(f"❌ Signup error: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error_message": f"Signup failed: {type(e).__name__}: {str(e)}"},
            status_code=500
        )


@router.get("/logout")
async def logout(response: Response):
    """Logout user"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_session")
    return response


@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email(request: Request, token: str = "", db: Session = Depends(get_db)):
    """Verify email address via token link."""
    error = ""
    if not token:
        error = "Invalid verification link."
    else:
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            error = "Verification link is invalid or already used."
        elif user.verification_token_expires and datetime.utcnow() > user.verification_token_expires:
            error = "Verification link has expired. Please request a new one."
        else:
            # Mark verified, clear token
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            user.last_login = datetime.utcnow()
            db.commit()
            # Auto-login and redirect to dashboard
            response = RedirectResponse(url="/dashboard", status_code=303)
            response.set_cookie(
                key="user_session",
                value=user.email,
                max_age=30 * 24 * 60 * 60,
                httponly=True,
                samesite="lax",
            )
            return response

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error_message": error or "Email verified! You can now log in."},
    )


@router.post("/resend-verification", response_class=HTMLResponse)
async def resend_verification(request: Request, db: Session = Depends(get_db)):
    """Resend verification email."""
    try:
        form_data = await request.form()
        email = form_data.get("email", "").strip()
        user = db.query(User).filter(User.email == email).first()

        # Always show the same page (don't reveal if email exists)
        if user and not user.is_verified:
            token, expires = generate_verification_token()
            user.verification_token = token
            user.verification_token_expires = expires
            db.commit()
            send_verification_email(email, token, user.full_name or email, request)

        return templates.TemplateResponse(
            "verify_email_sent.html",
            {"request": request, "email": email, "email_sent": True, "resent": True},
        )
    except Exception as e:
        import traceback
        print(f"❌ Resend error: {e}\n{traceback.format_exc()}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": "Could not resend email. Please try again."},
        )


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Upload audio page"""
    return templates.TemplateResponse("upload.html", {"request": request})


@router.get("/tickets", response_class=HTMLResponse)
async def tickets_page(request: Request):
    """Tickets list page"""
    return templates.TemplateResponse("tickets.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Admin dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/developers", response_class=HTMLResponse)
async def developers_page(request: Request):
    """Developers team page"""
    return templates.TemplateResponse("developers.html", {"request": request})


@router.get("/tickets/{ticket_number}", response_class=HTMLResponse)
async def ticket_detail_page(request: Request, ticket_number: str):
    """Ticket details page with chat"""
    return templates.TemplateResponse("ticket_detail.html", {"request": request})


@router.get("/documentation", response_class=HTMLResponse)
async def documentation_page(request: Request):
    """Documentation and API reference page"""
    return templates.TemplateResponse("documentation.html", {"request": request})


@router.get("/security", response_class=HTMLResponse)
async def security_page(request: Request):
    """Security information page"""
    return templates.TemplateResponse("security.html", {"request": request})


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Privacy policy page"""
    return templates.TemplateResponse("privacy.html", {"request": request})


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """About us page"""
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    """Support center page"""
    return templates.TemplateResponse("support.html", {"request": request})