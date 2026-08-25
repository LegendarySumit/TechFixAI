"""
Web routes for serving HTML templates.
"""

from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
import os
import traceback

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

# Use raw Jinja2 to avoid Starlette's TemplateResponse caching issues
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir), cache_size=0)

def render_to_html(template_name: str, context: dict) -> str:
    """Render a template to HTML string."""
    template = jinja_env.get_template(template_name)
    return template.render(**context)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    html = render_to_html("home.html", {"request": request})
    return HTMLResponse(content=html)


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
    html = render_to_html("login.html", {
        "request": request,
        "error_message": error,
        "success_message": info,
        "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
    })
    return HTMLResponse(content=html)


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle login form submission."""
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
            return RedirectResponse(url=f"/login?error=rate_limit", status_code=303)

        if not email or not password:
            return RedirectResponse(url=f"/login?error=empty_fields", status_code=303)

        user = db.query(User).filter(User.email == email.lower()).first()
        if not user or not user.verify_password(password):
            register_auth_failure(account_key, ip_address)
            track_product_event(
                event_name="login_failed",
                session_id=request.cookies.get(settings.SESSION_COOKIE_NAME),
                ip_address=ip_address,
                details={"reason": "invalid_credentials"}
            )
            return RedirectResponse(url=f"/login?error=invalid_credentials", status_code=303)

        if not user.is_active:
            return RedirectResponse(url=f"/login?error=account_inactive", status_code=303)

        register_auth_success(account_key, ip_address)
        
        response = RedirectResponse(url="/upload", status_code=303)
        set_session_cookie(response, user.email, remember_me=remember)
        
        track_product_event(
            event_name="login_success",
            session_id=None,
            ip_address=ip_address,
        )
        
        return response

    except Exception as e:
        print(f"❌ Login error: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        html = render_to_html("login.html", {
            "request": request,
            "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
            "error_message": "Login failed. Please try again.",
        })
        return HTMLResponse(content=html, status_code=500)


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
    html = render_to_html("signup.html", {
        "request": request,
        "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
        "error_message": error_map.get(request.query_params.get("error", ""), ""),
    })
    return HTMLResponse(content=html)


@router.post("/signup", response_class=HTMLResponse)
async def signup_submit(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle signup form submission."""
    try:
        form_data = await request.form()
        email = form_data.get("email", "").strip()
        full_name = form_data.get("full_name", "").strip()
        password = form_data.get("password", "")
        password_confirm = form_data.get("password_confirm", "")
        ip_address = get_request_ip(request)

        allowed_auth_rate, retry_auth_rate = check_rate_limit(
            bucket=f"auth_signup:{ip_address}",
            max_requests=settings.AUTH_SIGNUP_RATE_LIMIT_REQUESTS,
            window_seconds=settings.AUTH_SIGNUP_RATE_LIMIT_WINDOW_SECONDS,
        )
        if not allowed_auth_rate:
            return RedirectResponse(url="/signup?error=rate_limit", status_code=303)

        if not email or not password or not password_confirm:
            return RedirectResponse(url="/signup?error=empty_fields", status_code=303)

        if len(password) < 8:
            return RedirectResponse(url="/signup?error=weak_password", status_code=303)

        if password != password_confirm:
            return RedirectResponse(url="/signup?error=password_mismatch", status_code=303)

        user = db.query(User).filter(User.email == email.lower()).first()
        if user:
            return RedirectResponse(url="/signup?error=email_exists", status_code=303)

        new_user = User(
            email=email.lower(),
            username=email.split("@")[0],
            full_name=full_name,
        )
        new_user.set_password(password)
        new_user.is_active = True

        db.add(new_user)
        db.commit()

        register_auth_success(email.lower(), ip_address)
        track_product_event(
            event_name="signup_success",
            session_id=None,
            ip_address=ip_address,
        )

        response = RedirectResponse(url="/login?info=signup_success", status_code=303)
        return response

    except Exception as e:
        print(f"❌ Signup error: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        html = render_to_html("signup.html", {
            "request": request,
            "captcha_site_key": settings.CAPTCHA_SITE_KEY if settings.CAPTCHA_ENABLED else "",
            "error_message": "Signup failed. Please try again.",
        })
        return HTMLResponse(content=html, status_code=500)


@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    response = RedirectResponse(url="/", status_code=303)
    clear_session_cookie(response)
    return response


@router.post("/change-password", response_class=HTMLResponse)
async def change_password_submit(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle password change."""
    try:
        user = request.state.current_user
        if not user:
            return RedirectResponse(url="/login", status_code=303)

        form_data = await request.form()
        current_password = form_data.get("current_password", "")
        new_password = form_data.get("new_password", "")
        confirm_password = form_data.get("confirm_password", "")

        if not user.verify_password(current_password):
            return RedirectResponse(url="/dashboard?error=invalid_current_password", status_code=303)

        if len(new_password) < 8:
            return RedirectResponse(url="/dashboard?error=weak_password", status_code=303)

        if new_password != confirm_password:
            return RedirectResponse(url="/dashboard?error=password_mismatch", status_code=303)

        if new_password == current_password:
            return RedirectResponse(url="/dashboard?error=password_reuse", status_code=303)

        user.set_password(new_password)
        db.commit()

        response = RedirectResponse(url="/login?info=password_changed", status_code=303)
        clear_session_cookie(response)
        return response

    except Exception as e:
        print(f"Password change error: {str(e)}")
        db.rollback()
        return RedirectResponse(url="/dashboard?error=change_failed", status_code=303)


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Upload page"""
    html = render_to_html("upload.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/tickets", response_class=HTMLResponse)
async def tickets_page(request: Request):
    """Tickets page"""
    html = render_to_html("tickets.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    html = render_to_html("dashboard.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/developers", response_class=HTMLResponse)
async def developers_page(request: Request):
    """Developers page"""
    html = render_to_html("developers.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/ticket/{ticket_number}", response_class=HTMLResponse)
async def ticket_detail_page(request: Request, ticket_number: str):
    """Ticket detail page"""
    html = render_to_html("ticket_detail.html", {"request": request, "ticket_number": ticket_number})
    return HTMLResponse(content=html)


@router.get("/documentation", response_class=HTMLResponse)
async def documentation_page(request: Request):
    """Documentation page"""
    html = render_to_html("documentation.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/security", response_class=HTMLResponse)
async def security_page(request: Request):
    """Security page"""
    html = render_to_html("security.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Privacy page"""
    html = render_to_html("privacy.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Terms page"""
    html = render_to_html("terms.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """About page"""
    html = render_to_html("about.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    """Support page"""
    html = render_to_html("support.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    """Status page"""
    html = render_to_html("status.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/changelog", response_class=HTMLResponse)
async def changelog_page(request: Request):
    """Changelog page"""
    html = render_to_html("changelog.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/sla", response_class=HTMLResponse)
async def sla_page(request: Request):
    """SLA page"""
    html = render_to_html("sla.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    """Pricing page"""
    html = render_to_html("pricing.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/billing-policy", response_class=HTMLResponse)
async def billing_policy_page(request: Request):
    """Billing policy page"""
    html = render_to_html("billing_policy.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/go-no-go", response_class=HTMLResponse)
async def go_no_go_page(request: Request):
    """Go/No-Go status page"""
    html = render_to_html("go_no_go.html", {"request": request})
    return HTMLResponse(content=html)


@router.get("/health")
async def health_check():
    """
    Health check endpoint for uptime monitoring.
    Returns 200 if healthy, 503 if any dependency is down.
    """
    from app.core.health import HealthChecker, HealthStatus
    from app.core.metrics import MetricsRecorder
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
