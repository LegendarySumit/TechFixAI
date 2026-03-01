"""
Ticket API endpoints.
View and manage tickets.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.conversation import Conversation

router = APIRouter()


def delete_ticket_and_audio(ticket_number: str, delay_seconds: int = 5):
    """
    Background task to delete ticket and associated conversation after a delay.
    Opens its own DB session (must not reuse request session which is already closed).
    """
    import time
    from app.db.session import SessionLocal
    
    time.sleep(delay_seconds)
    
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()
        if ticket:
            conversation_id = ticket.conversation_id
            db.delete(ticket)
            db.flush()  # release FK before deleting parent
            if conversation_id:
                conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                if conv:
                    db.delete(conv)
            db.commit()
    except Exception as e:
        print(f"Error deleting ticket {ticket_number}: {str(e)}")
        db.rollback()
    finally:
        db.close()


@router.get("/{ticket_number}")
async def get_ticket(
    ticket_number: str,
    db: Session = Depends(get_db)
):
    """
    Get ticket details by ticket number.
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {
        "ticket_number": ticket.ticket_number,
        "title": ticket.title,
        "description": ticket.description,
        "priority": ticket.priority,
        "status": ticket.status,
        "category": ticket.category,
        "technical_area": ticket.technical_area,
        "assigned_to": {
            "name": ticket.assigned_developer.name,
            "email": ticket.assigned_developer.email
        } if ticket.assigned_developer else None,
        "assignment_reason": ticket.assignment_reason,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "resolved_at": ticket.resolved_at,
        "conversation": {
            "id": ticket.conversation.id,
            "japanese_transcript": ticket.conversation.japanese_transcript,
            "english_translation": ticket.conversation.english_translation,
            "audio_file_path": ticket.conversation.audio_file_path
        }
    }


@router.get("/")
async def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    technical_area: Optional[str] = Query(None),
    assigned_developer_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = Query(default=50, le=200),  # cap at 200 to prevent full-table dumps
    db: Session = Depends(get_db)
):
    """
    List tickets with optional filters.
    """
    query = db.query(Ticket)
    
    # Apply filters
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if technical_area:
        query = query.filter(Ticket.technical_area == technical_area)
    if assigned_developer_id:
        query = query.filter(Ticket.assigned_developer_id == assigned_developer_id)
    
    # Get total count
    total = query.count()
    
    # Pagination
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "tickets": [
            {
                "ticket_number": t.ticket_number,
                "title": t.title,
                "priority": t.priority,
                "status": t.status,
                "category": t.category,
                "technical_area": t.technical_area,
                "assigned_to": t.assigned_developer.name if t.assigned_developer else None,
                "created_at": t.created_at
            }
            for t in tickets
        ]
    }


@router.patch("/{ticket_number}/status")
async def update_ticket_status(
    ticket_number: str,
    status_update: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Update ticket status and schedule deletion after a delay.
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    new_status = status_update.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    ticket.status = new_status
    
    if new_status == 'resolved':
        from datetime import datetime
        ticket.resolved_at = datetime.utcnow()
    
    db.commit()
    
    background_tasks.add_task(delete_ticket_and_audio, ticket_number, delay_seconds=5)
    
    return {
        "success": True,
        "ticket_number": ticket.ticket_number,
        "status": ticket.status,
        "message": f"Ticket status updated to {new_status}. Ticket will be deleted in 5 seconds.",
        "will_delete": True,
        "delete_delay": 5
    }


@router.delete("/{ticket_number}")
async def delete_ticket(
    ticket_number: str,
    db: Session = Depends(get_db)
):
    """
    Permanently delete a ticket and its associated conversation.
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    conversation_id = ticket.conversation_id

    # Delete ticket first (it holds the FK to conversation)
    db.delete(ticket)
    db.flush()

    # Now safe to delete the orphaned conversation
    if conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            db.delete(conv)

    db.commit()

    return {"success": True, "message": f"Ticket {ticket_number} deleted"}
