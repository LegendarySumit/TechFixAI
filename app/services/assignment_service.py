"""
Assignment service.
Deterministic developer assignment based on skills and availability.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.developer import Developer
from app.models.ticket import Ticket, TicketStatus


class AssignmentService:
    """
    Service for assigning tickets to developers.
    Uses deterministic logic based on skills, workload, and availability.
    """

    async def assign_ticket(
        self,
        db: Session,
        ticket: Ticket
    ) -> Optional[Developer]:
        """
        DETERMINISTIC assignment: Rule-based, no AI.

        Rules (in order):
        1. Backend/Infrastructure + High/Critical -> Backend Team
        2. Frontend/UI + Any Priority -> Frontend Team
        3. Database/Data + High/Critical -> Backend Team
        4. Default -> Least loaded developer

        Args:
            db: Database session
            ticket: Ticket to assign

        Returns:
            Assigned Developer or None if no suitable dev found
        """

        # Get all online/busy developers (not offline)
        active_devs = db.query(Developer).filter(
            Developer.status.in_(["online", "busy"])
        ).all()

        if not active_devs:
            # If no online devs, get any developer
            active_devs = db.query(Developer).all()
            if not active_devs:
                return None

        # Calculate current workload
        dev_workload = {}
        for dev in active_devs:
            active_ticket_count = db.query(func.count(Ticket.id)).filter(
                Ticket.assigned_developer_id == dev.id,
                Ticket.status.in_([TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS])
            ).scalar()
            dev_workload[dev.id] = active_ticket_count

        # Normalize priority to plain string
        priority_val = ticket.priority.value if hasattr(ticket.priority, "value") else str(ticket.priority)

        # DETERMINISTIC RULES
        best_dev = None
        assignment_reason = ""

        # Rule 1: Backend/Infrastructure + High/Critical Priority
        if (ticket.category and "backend" in ticket.category.lower()) or            (ticket.technical_area and "backend" in ticket.technical_area.lower()):
            if priority_val in ["high", "critical"]:
                backend_devs = [
                    dev for dev in active_devs
                    if dev.expertise and "backend" in dev.expertise.lower()
                ]
                if backend_devs:
                    best_dev = min(backend_devs, key=lambda d: dev_workload[d.id])
                    assignment_reason = f"Rule: Backend/Infrastructure + {priority_val.upper()} priority -> Backend Team"

        # Rule 2: Frontend/UI
        if not best_dev and (
            (ticket.category and "frontend" in ticket.category.lower()) or
            (ticket.technical_area and "frontend" in ticket.technical_area.lower())
        ):
            frontend_devs = [
                dev for dev in active_devs
                if dev.expertise and "frontend" in dev.expertise.lower()
            ]
            if frontend_devs:
                best_dev = min(frontend_devs, key=lambda d: dev_workload[d.id])
                assignment_reason = "Rule: Frontend/UI issue -> Frontend Team"

        # Rule 3: Database + High/Critical
        if not best_dev and (
            (ticket.category and "database" in ticket.category.lower()) or
            (ticket.technical_area and "database" in ticket.technical_area.lower())
        ):
            if priority_val in ["high", "critical"]:
                backend_devs = [
                    dev for dev in active_devs
                    if dev.expertise and "backend" in dev.expertise.lower()
                ]
                if backend_devs:
                    best_dev = min(backend_devs, key=lambda d: dev_workload[d.id])
                    assignment_reason = f"Rule: Database + {priority_val.upper()} priority -> Backend Team"

        # Default: Least loaded developer
        if not best_dev:
            best_dev = min(active_devs, key=lambda d: dev_workload[d.id])
            assignment_reason = f"Default: Assigned to least loaded developer ({dev_workload[best_dev.id]} active tickets)"

        # Update ticket
        ticket.assigned_developer_id = best_dev.id
        ticket.assignment_reason = assignment_reason
        ticket.status = TicketStatus.ASSIGNED

        db.commit()
        db.refresh(ticket)

        return best_dev


# Singleton instance
assignment_service = AssignmentService()
