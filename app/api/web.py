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

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle login form submission."""
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")
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
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create response and set session cookie
    response = RedirectResponse(url="/upload", status_code=303)
    
    # Simple session cookie (in production, use proper JWT or session management)
    max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days if remember me
    response.set_cookie(
        key="user_session",
        value=user.email,
        max_age=max_age,
        httponly=True,
        samesite="lax"
    )
    
    return response


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
    form_data = await request.form()
    
    email = form_data.get("email", "").strip()
    username = form_data.get("username", "").strip()
    full_name = form_data.get("full_name", "").strip()
    password = form_data.get("password", "")
    confirm_password = form_data.get("confirm_password", "")
    terms = form_data.get("terms")
    
    # Validate input
    errors = []
    
    if not email:
        errors.append("Email is required")
    elif "@" not in email or "." not in email:
        errors.append("Please enter a valid email address")
    
    if not username:
        errors.append("Username is required")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters")
    
    if not full_name:
        errors.append("Full name is required")
    
    if not password:
        errors.append("Password is required")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    if password != confirm_password:
        errors.append("Passwords do not match")
    
    if not terms:
        errors.append("You must agree to the terms and conditions")
    
    # Check if user already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        errors.append("Email already registered")
    
    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        errors.append("Username already taken")
    
    if errors:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error_message": "; ".join(errors),
                "email": email,
                "username": username,
                "full_name": full_name
            },
            status_code=400
        )
    
    # Create new user
    new_user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=User.get_password_hash(password),
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create response and set session cookie
    response = RedirectResponse(url="/upload", status_code=303)
    response.set_cookie(
        key="user_session",
        value=new_user.email,
        max_age=None,
        httponly=True,
        samesite="lax"
    )
    
    return response


@router.get("/logout")
async def logout(response: Response):
    """Logout user"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_session")
    return response


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
