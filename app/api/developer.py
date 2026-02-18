"""
Developer API endpoints.
View and manage developers.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.developer import Developer
from app.models.ticket import Ticket, TicketStatus

router = APIRouter()


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
