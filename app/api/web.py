"""
Web routes for serving HTML templates.
"""

from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.config import settings
from app.core.auth_guard import (
    check_auth_allowed,
    get_request_ip,
    register_auth_failure,
    register_auth_success,
)
from app.core.captcha import verify_captcha_token
from app.core.rate_limit import check_rate_limit
from app.core.session import clear_session_cookie, set_session_cookie
from app.core.access_control import is_admin_email
from app.core.health import HealthChecker
from app.services.product_analytics import track_product_event


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["sentry_frontend_dsn"] = settings.SENTRY_DSN
templates.env.globals["sentry_environment"] = "production" if settings.PUBLIC_DEPLOYMENT else "development"
templates.env.globals["sentry_release"] = settings.SENTRY_RELEASE


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
        "oauth_state_mismatch": "Google sign-in session expired or host changed (localhost vs 127.0.0.1). Retry from localhost.",
        "captcha_required": "Please complete CAPTCHA before continuing.",
        "no_profile": "Could not retrieve your Google profile. Please try again.",
        "no_email": "Your Google account has no verified email.",
        "weak_password": "New password must be at least 8 characters.",
        "password_mismatch": "New password and confirmation do not match.",
        "invalid_current_password": "Current password is incorrect.",
        "password_reuse": "New password must be different from your current password.",
    }
    error = error_map.get(request.query_params.get("error", ""), "")
    info_map = {
        "password_changed": "Password updated. Please sign in again.",
    }
    info = info_map.get(request.query_params.get("info", ""), "")
    track_product_event(
        event_name="login_started",
        session_id=request.cookies.get(settings.SESSION_COOKIE_NAME),
        ip_address=get_request_ip(request),
    )
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error_message": error,
            "success_message": info,
            "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
        },
    )


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
        remember = str(form_data.get("remember", "")).lower() in {"1", "true", "on", "yes"}
        ip_address = get_request_ip(request)
        account_key = email.lower() if email else "unknown"

        allowed_auth_rate, retry_auth_rate = check_rate_limit(
            bucket=f"auth_login:{ip_address}",
            max_requests=settings.AUTH_LOGIN_RATE_LIMIT_REQUESTS,
            window_seconds=settings.AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS,
        )
        if not allowed_auth_rate:
            wait_minutes = max(1, retry_auth_rate // 60)
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": f"Too many login requests. Please retry in about {wait_minutes} minute(s).",
                },
                status_code=429,
            )

        if settings.CAPTCHA_ENABLED and settings.CAPTCHA_REQUIRED_LOGIN:
            captcha_token = str(form_data.get("captcha_token", "")).strip()
            captcha_ok, captcha_error = await verify_captcha_token(captcha_token, ip_address)
            if not captcha_ok:
                register_auth_failure(ip_address, account_key)
                return templates.TemplateResponse(
                    "login.html",
                    {
                        "request": request,
                        "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                        "error_message": captcha_error,
                    },
                    status_code=400,
                )

        allowed, retry_after_seconds = check_auth_allowed(ip_address, account_key)
        if not allowed:
            wait_minutes = max(1, retry_after_seconds // 60)
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": f"Too many attempts. Please try again in about {wait_minutes} minute(s).",
                },
                status_code=429,
            )

        # Validate input
        if not email or not password:
            register_auth_failure(ip_address, account_key)
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": "Email and password are required",
                },
                status_code=400
            )

        # Find user
        user = db.query(User).filter(User.email == email).first()

        if not user or not user.verify_password(password):
            register_auth_failure(ip_address, account_key)
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": "Invalid email or password",
                },
                status_code=401
            )

        if not user.is_active:
            register_auth_failure(ip_address, account_key)
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": "Account is disabled",
                },
                status_code=403
            )

        register_auth_success(ip_address, account_key)

        track_product_event(
            event_name="login_success",
            user_id=user.id,
            user_email=user.email,
            ip_address=ip_address,
        )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Set session cookie
        response = RedirectResponse(url="/dashboard", status_code=303)
        set_session_cookie(response, user, remember=remember)
        return response

    except Exception as e:
        print(f"❌ Login error: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                "error_message": "Login failed. Please try again.",
            },
            status_code=500
        )


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Sign up page"""
    error_map = {
        "captcha_required": "Please complete CAPTCHA before continuing.",
    }
    track_product_event(
        event_name="signup_started",
        session_id=request.cookies.get(settings.SESSION_COOKIE_NAME),
        ip_address=get_request_ip(request),
    )
    return templates.TemplateResponse(
        "signup.html",
        {
            "request": request,
            "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
            "error_message": error_map.get(request.query_params.get("error", ""), ""),
        },
    )


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
        ip_address = get_request_ip(request)
        account_key = email.lower() if email else "unknown"

        # Honeypot anti-bot field: real users never fill this hidden field.
        if str(form_data.get("website", "")).strip():
            register_auth_failure(ip_address, account_key)
            return templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": "Signup validation failed.",
                    "email": email,
                    "full_name": full_name,
                },
                status_code=400,
            )

        allowed_signup_rate, retry_signup_rate = check_rate_limit(
            bucket=f"auth_signup:{ip_address}",
            max_requests=settings.AUTH_SIGNUP_RATE_LIMIT_REQUESTS,
            window_seconds=settings.AUTH_SIGNUP_RATE_LIMIT_WINDOW_SECONDS,
        )
        if not allowed_signup_rate:
            wait_minutes = max(1, retry_signup_rate // 60)
            return templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": f"Too many signup requests. Please retry in about {wait_minutes} minute(s).",
                    "email": email,
                    "full_name": full_name,
                },
                status_code=429,
            )

        if settings.CAPTCHA_ENABLED and settings.CAPTCHA_REQUIRED_SIGNUP:
            captcha_token = str(form_data.get("captcha_token", "")).strip()
            captcha_ok, captcha_error = await verify_captcha_token(captcha_token, ip_address)
            if not captcha_ok:
                register_auth_failure(ip_address, account_key)
                return templates.TemplateResponse(
                    "signup.html",
                    {
                        "request": request,
                        "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                        "error_message": captcha_error,
                        "email": email,
                        "full_name": full_name,
                    },
                    status_code=400,
                )

        allowed, retry_after_seconds = check_auth_allowed(ip_address, account_key)
        if not allowed:
            wait_minutes = max(1, retry_after_seconds // 60)
            return templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": f"Too many signup attempts. Please try again in about {wait_minutes} minute(s).",
                    "email": email,
                    "full_name": full_name,
                },
                status_code=429,
            )

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
            register_auth_failure(ip_address, account_key)
            return templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                    "error_message": "; ".join(errors),
                    "email": email,
                    "full_name": full_name,
                },
                status_code=400
            )

        # Auto-generate unique username from email prefix
        base_username = email.split("@")[0].lower().replace(".", "_").replace("+", "_")[:20]
        username = base_username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1

        # Create user — verified immediately, no email step
        new_user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=User.get_password_hash(password),
            is_active=True,
            is_verified=True,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Log in directly
        new_user.last_login = datetime.utcnow()
        db.commit()

        register_auth_success(ip_address, account_key)

        track_product_event(
            event_name="signup_completed",
            user_id=new_user.id,
            user_email=new_user.email,
            ip_address=ip_address,
        )

        response = RedirectResponse(url="/dashboard", status_code=303)
        set_session_cookie(response, new_user, remember=False)
        return response

    except Exception as e:
        print(f"❌ Signup error: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
                "error_message": "Signup failed. Please try again.",
            },
            status_code=500
        )


@router.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/", status_code=303)
    clear_session_cookie(response)
    return response


@router.post("/account/password")
async def change_password_submit(
    request: Request,
    db: Session = Depends(get_db),
):
    """Change password and force logout from existing sessions."""
    if not request.state.current_user:
        return RedirectResponse(url="/login", status_code=303)

    form_data = await request.form()
    current_password = form_data.get("current_password", "")
    new_password = form_data.get("new_password", "")
    confirm_password = form_data.get("confirm_password", "")

    if not new_password or len(new_password) < 8:
        return RedirectResponse(url="/login?error=weak_password", status_code=303)

    if new_password != confirm_password:
        return RedirectResponse(url="/login?error=password_mismatch", status_code=303)

    user = db.query(User).filter(User.id == request.state.current_user.id).first()
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if user.hashed_password and not user.verify_password(current_password):
        return RedirectResponse(url="/login?error=invalid_current_password", status_code=303)

    if user.hashed_password and user.verify_password(new_password):
        return RedirectResponse(url="/login?error=password_reuse", status_code=303)

    user.hashed_password = User.get_password_hash(new_password)
    user.password_changed_at = datetime.utcnow()
    user.last_login = None
    db.commit()

    response = RedirectResponse(url="/login?info=password_changed", status_code=303)
    clear_session_cookie(response)
    return response


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Upload audio page - Protected"""
    if not request.state.current_user:
        return RedirectResponse(url="/login", status_code=303)
    track_product_event(
        event_name="upload_page_viewed",
        user_id=request.state.current_user.id,
        user_email=request.state.current_user.email,
        ip_address=get_request_ip(request),
    )
    return templates.TemplateResponse("upload.html", {"request": request})


@router.get("/tickets", response_class=HTMLResponse)
async def tickets_page(request: Request):
    """Tickets list page - Protected"""
    if not request.state.current_user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("tickets.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page - Protected"""
    if not request.state.current_user:
        return RedirectResponse(url="/login", status_code=303)
    track_product_event(
        event_name="retention_visit",
        user_id=request.state.current_user.id,
        user_email=request.state.current_user.email,
        ip_address=get_request_ip(request),
    )
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/developers", response_class=HTMLResponse)
async def developers_page(request: Request):
    """Developers team page - Protected"""
    if not request.state.current_user:
        return RedirectResponse(url="/login", status_code=303)
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


@router.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Terms of service page"""
    return templates.TemplateResponse("terms.html", {"request": request})


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """About us page"""
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    """Support center page"""
    return templates.TemplateResponse("support.html", {"request": request})


@router.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    """Public service status page."""
    status = await HealthChecker.get_health_status()
    return templates.TemplateResponse(
        "status.html",
        {
            "request": request,
            "status": status,
            "uptime_target_percent": 99.9,
        },
    )


@router.get("/changelog", response_class=HTMLResponse)
async def changelog_page(request: Request):
    """Legacy changelog URL redirected to merged status page section."""
    return RedirectResponse(url="/status#changelog", status_code=307)


@router.get("/sla", response_class=HTMLResponse)
async def sla_page(request: Request):
    """Legacy SLA URL redirected to merged status page section."""
    return RedirectResponse(url="/status#sla", status_code=307)


@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    """Public pricing page aligned with backend quota controls."""
    return templates.TemplateResponse(
        "pricing.html",
        {
            "request": request,
            "free_quota": settings.FREE_TIER_UPLOAD_QUOTA,
            "pro_quota": settings.PRO_TIER_UPLOAD_QUOTA,
            "enterprise_quota": settings.ENTERPRISE_TIER_UPLOAD_QUOTA,
            "free_cost_limit": settings.FREE_TIER_MONTHLY_COST_LIMIT_CENTS,
            "pro_cost_limit": settings.PRO_TIER_MONTHLY_COST_LIMIT_CENTS,
        },
    )


@router.get("/billing-policy", response_class=HTMLResponse)
async def billing_policy_page(request: Request):
    """Legacy billing policy URL redirected to merged pricing page section."""
    return RedirectResponse(url="/pricing#billing", status_code=307)


@router.get("/go-no-go", response_class=HTMLResponse)
async def go_no_go_page(request: Request):
    """Public launch readiness checklist page."""
    return templates.TemplateResponse("go_no_go.html", {"request": request})


# Observability endpoints (health checks, metrics)

@router.get("/health")
async def health_check():
    """
    Health check endpoint for uptime monitoring.
    Returns 200 if healthy, 503 if any dependency is down.
    """
    from app.core.health import HealthChecker, HealthStatus
    from app.core.metrics import MetricsRecorder
    from fastapi.responses import JSONResponse
    import time
    
    start_time = time.time()
    
    try:
        status_data = await HealthChecker.get_health_status()
        duration = time.time() - start_time
        
        # Record health check metrics
        healthy = status_data["status"] == HealthStatus.HEALTHY
        MetricsRecorder.record_health_check(healthy, duration)
        
        # Return 503 if unhealthy or degraded
        status_code = 200 if status_data["status"] == HealthStatus.HEALTHY else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                **status_data,
                "response_time_seconds": duration,
            }
        )
    except Exception as e:
        duration = time.time() - start_time
        MetricsRecorder.record_health_check(False, duration)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "response_time_seconds": duration,
            }
        )


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    Returns all collected metrics in Prometheus text format.
    Enabled only if METRICS_ENABLED=True.
    """
    from app.core.config import settings
    from app.core.metrics import get_metrics_text
    from fastapi.responses import Response
    
    if not settings.METRICS_ENABLED:
        return JSONResponse(
            status_code=404,
            content={"detail": "Metrics disabled"}
        )
    
    return Response(
        content=get_metrics_text(),
        media_type="text/plain; charset=utf-8",
    )