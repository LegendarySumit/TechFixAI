"""
Admin API endpoints.
Admin visibility into the system.
"""

from datetime import timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.core.access_control import get_current_user_or_401
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.developer import Developer
from app.models.conversation import Conversation, ConversationStatus

router = APIRouter()


def _to_utc_iso(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


@router.get("/dashboard")
async def get_dashboard(
    _current_user=Depends(get_current_user_or_401),
    db: Session = Depends(get_db)
):
    """
    Admin dashboard with system overview.
    """
    
    # Ticket statistics
    total_tickets = db.query(func.count(Ticket.id)).scalar()
    open_tickets = db.query(func.count(Ticket.id)).filter(
        Ticket.status == TicketStatus.OPEN
    ).scalar()
    assigned_tickets = db.query(func.count(Ticket.id)).filter(
        Ticket.status == TicketStatus.ASSIGNED
    ).scalar()
    resolved_tickets = db.query(func.count(Ticket.id)).filter(
        Ticket.status == TicketStatus.RESOLVED
    ).scalar()
    
    # Priority breakdown
    critical_tickets = db.query(func.count(Ticket.id)).filter(
        Ticket.priority == TicketPriority.CRITICAL,
        Ticket.status != TicketStatus.RESOLVED
    ).scalar()
    
    # Conversation statistics
    total_conversations = db.query(func.count(Conversation.id)).scalar()
    processing_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.status.in_([ConversationStatus.RECEIVED, ConversationStatus.PROCESSING])
    ).scalar()
    failed_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.status == ConversationStatus.FAILED
    ).scalar()
    
    # Developer workload
    developers = db.query(Developer).filter(Developer.is_active == True).all()
    dev_workload = []
    for dev in developers:
        active_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.assigned_developer_id == dev.id,
            Ticket.status.in_([TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS])
        ).scalar()
        
        dev_workload.append({
            "developer_id": dev.id,
            "name": dev.name,
            "status": dev.status,
            "active_tickets": active_tickets,
            "max_capacity": dev.max_concurrent_tickets,
            "utilization": f"{(active_tickets / dev.max_concurrent_tickets * 100):.1f}%"
        })
    
    return {
        "tickets": {
            "total": total_tickets,
            "open": open_tickets,
            "assigned": assigned_tickets,
            "resolved": resolved_tickets,
            "critical_active": critical_tickets
        },
        "conversations": {
            "total": total_conversations,
            "processing": processing_conversations,
            "failed": failed_conversations
        },
        "developers": {
            "active_count": len(developers),
            "workload": dev_workload
        }
    }


@router.get("/conversations")
async def list_all_conversations(
    status: str = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    _current_user=Depends(get_current_user_or_401),
    db: Session = Depends(get_db)
):
    """
    List all conversations with full details (admin only).
    """
    query = db.query(Conversation)
    
    if status:
        query = query.filter(Conversation.status == status)
    
    total = query.count()
    conversations = query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "conversations": [
            {
                "id": c.id,
                "status": c.status,
                "audio_file_path": c.audio_file_path,
                "audio_duration_seconds": c.audio_duration_seconds,
                "japanese_transcript": c.japanese_transcript,
                "english_translation": c.english_translation,
                "created_at": _to_utc_iso(c.created_at),
                "has_ticket": c.ticket is not None,
                "ticket_number": c.ticket.ticket_number if c.ticket else None
            }
            for c in conversations
        ]
    }


@router.get("/developers")
async def list_developers(
    _current_user=Depends(get_current_user_or_401),
    db: Session = Depends(get_db)
):
    """
    List all developers with their stats.
    """
    developers = db.query(Developer).all()
    
    dev_list = []
    for dev in developers:
        total_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.assigned_developer_id == dev.id
        ).scalar()
        
        active_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.assigned_developer_id == dev.id,
            Ticket.status.in_([TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS])
        ).scalar()
        
        resolved_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.assigned_developer_id == dev.id,
            Ticket.status == TicketStatus.RESOLVED
        ).scalar()
        
        dev_list.append({
            "id": dev.id,
            "name": dev.name,
            "email": dev.email,
            "expertise": dev.expertise,
            "languages": dev.languages,
            "is_active": dev.is_active,
            "max_concurrent_tickets": dev.max_concurrent_tickets,
            "stats": {
                "total_tickets": total_tickets,
                "active_tickets": active_tickets,
                "resolved_tickets": resolved_tickets
            }
        })
    
    return {"developers": dev_list}
