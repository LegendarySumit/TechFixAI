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
from app.models.user import User
from app.services.quota_service import QuotaService
from app.services.cost_tracking import CostTrackingService
from app.services.product_analytics import build_funnel_report

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


# ===== COST & QUOTA MONITORING (NEW) =====

@router.get("/costs/global")
async def get_global_costs(
    _current_user=Depends(get_current_user_or_401),
    db: Session = Depends(get_db)
):
    """
    Get global Groq API spending metrics.
    Shows system-wide cost tracking and budget status.
    """
    metrics = CostTrackingService.get_cost_metrics(db)
    
    return {
        "metrics": metrics,
        "status": "warning" if metrics["at_warning_threshold"] else ("exceeded" if metrics["exceeds_cap"] else "healthy")
    }


@router.get("/costs/users")
async def get_user_costs(
    skip: int = 0,
    limit: int = Query(default=50, le=500),
    sort_by: str = Query(default="spend", regex="^(spend|uploads|tier)$"),
    _current_user=Depends(get_current_user_or_401),
    db: Session = Depends(get_db)
):
    """
    Get per-user cost breakdown and quota usage.
    Useful for identifying heavy users and quota violations.
    """
    query = db.query(User)
    
    # Sort options
    if sort_by == "spend":
        query = query.order_by(User.groq_spend_cents_month.desc())
    elif sort_by == "uploads":
        query = query.order_by(User.uploads_this_month.desc())
    elif sort_by == "tier":
        query = query.order_by(User.subscription_tier.desc())
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    user_costs = []
    for user in users:
        user_costs.append({
            "user_id": user.id,
            "email": user.email,
            "subscription_tier": user.subscription_tier,
            "uploads_this_month": user.uploads_this_month,
            "upload_limit": QuotaService.get_upload_limit(user),
            "groq_spend_cents": user.groq_spend_cents_month,
            "groq_spend_usd": round(user.groq_spend_cents_month / 100, 2),
            "cost_limit_cents": QuotaService.get_cost_limit(user),
            "cost_limit_usd": round(QuotaService.get_cost_limit(user) / 100, 2),
            "quota_exceeded": user.quota_exceeded,
            "quota_reset_date": user.quota_reset_date,
        })
    
    return {
        "total": total,
        "users": user_costs
    }


@router.get("/quotas/user/{user_id}")
async def get_user_quota_detail(
    user_id: int,
    _current_user=Depends(get_current_user_or_401),
    db: Session = Depends(get_db)
):
    """
    Get detailed quota status for a specific user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    
    quota_status = QuotaService.get_user_quota_status(user, db)
    
    return {
        "user_id": user.id,
        "email": user.email,
        **quota_status
    }


@router.get("/analytics/funnel")
async def get_funnel_report(
    days: int = Query(default=30, ge=1, le=120),
    _current_user=Depends(get_current_user_or_401),
):
    """Get onboarding/upload funnel with dropoff points."""
    return build_funnel_report(since_days=days)
