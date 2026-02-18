"""
Web routes for serving HTML templates.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("home.html", {"request": request})


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
