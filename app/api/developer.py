"""
Developer API endpoints.
View and manage developers.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.core.access_control import require_admin_user
from app.models.developer import Developer
from app.models.ticket import Ticket, TicketStatus

router = APIRouter()


class DeveloperCreate(BaseModel):
    name: str
    email: str
    expertise: Optional[str] = None
    languages: Optional[str] = None
    status: Optional[str] = "online"
    max_concurrent_tickets: Optional[int] = 5


class StatusUpdate(BaseModel):
    status: str  # online | busy | offline


@router.get("/")
async def list_developers(
    status: Optional[str] = Query(None),
    expertise: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List all developers with their stats.
    """
    query = db.query(Developer)
    
    # Apply filters
    if status:
        query = query.filter(Developer.status == status)
    if expertise:
        query = query.filter(Developer.expertise.contains(expertise))
    
    developers = query.all()
    
    # Calculate stats for each developer
    developer_list = []
    total_active_tickets = 0
    
    for dev in developers:
        # Count active tickets assigned to this developer
        active_tickets = db.query(Ticket).filter(
            Ticket.assigned_developer_id == dev.id,
            Ticket.status.in_(['open', 'assigned', 'in_progress'])
        ).count()
        
        resolved_tickets = db.query(Ticket).filter(
            Ticket.assigned_developer_id == dev.id,
            Ticket.status == 'resolved'
        ).count()
        
        total_active_tickets += active_tickets
        
        developer_list.append({
            "id": dev.id,
            "name": dev.name,
            "email": dev.email,
            "expertise": dev.expertise,
            "languages": dev.languages,
            "status": dev.status or "offline",
            "active_tickets": active_tickets,
            "resolved_tickets": resolved_tickets,
            "avg_response_time": "2-5 min",  # Could be calculated from actual data
            "created_at": dev.created_at
        })
    
    # Calculate overall stats
    online_count = sum(1 for d in developer_list if d['status'] == 'online')
    
    return {
        "total": len(developer_list),
        "online": online_count,
        "active_tickets": total_active_tickets,
        "avg_response_time": "~3m",
        "developers": developer_list
    }


@router.get("/{developer_id}")
async def get_developer(
    developer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get developer details by ID.
    """
    developer = db.query(Developer).filter(Developer.id == developer_id).first()
    
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    # Get tickets assigned to this developer
    tickets = db.query(Ticket).filter(
        Ticket.assigned_developer_id == developer_id
    ).order_by(Ticket.created_at.desc()).limit(10).all()
    
    active_tickets = [t for t in tickets if t.status in ['open', 'assigned', 'in_progress']]
    resolved_tickets = [t for t in tickets if t.status == 'resolved']
    
    return {
        "id": developer.id,
        "name": developer.name,
        "email": developer.email,
        "expertise": developer.expertise,
        "languages": developer.languages,
        "status": developer.status or "offline",
        "active_tickets": len(active_tickets),
        "resolved_tickets": len(resolved_tickets),
        "recent_tickets": [
            {
                "ticket_number": t.ticket_number,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at
            }
            for t in tickets[:5]
        ],
        "created_at": developer.created_at
    }


@router.post("/")
async def create_developer(
    payload: DeveloperCreate,
    _admin=Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new developer."""
    existing = db.query(Developer).filter(Developer.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    allowed_statuses = ["online", "busy", "offline"]
    status = payload.status if payload.status in allowed_statuses else "online"

    dev = Developer(
        name=payload.name,
        email=payload.email,
        expertise=payload.expertise,
        languages=payload.languages,
        status=status,
        max_concurrent_tickets=payload.max_concurrent_tickets or 5,
    )
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return {"id": dev.id, "name": dev.name, "email": dev.email, "status": dev.status}


@router.patch("/{developer_id}/status")
async def update_developer_status(
    developer_id: int,
    payload: StatusUpdate,
    _admin=Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Update a developer's availability status."""
    dev = db.query(Developer).filter(Developer.id == developer_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")

    allowed = ["online", "busy", "offline"]
    if payload.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status must be one of {allowed}")

    dev.status = payload.status
    dev.updated_at = datetime.utcnow()
    db.commit()
    return {"id": dev.id, "status": dev.status}


@router.delete("/{developer_id}")
async def delete_developer(
    developer_id: int,
    _admin=Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Remove a developer (only if they have no active tickets)."""
    dev = db.query(Developer).filter(Developer.id == developer_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")

    active = db.query(Ticket).filter(
        Ticket.assigned_developer_id == developer_id,
        Ticket.status.in_([TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS])
    ).count()
    if active > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete developer with {active} active ticket(s)")

    db.delete(dev)
    db.commit()
    return {"deleted": developer_id}
