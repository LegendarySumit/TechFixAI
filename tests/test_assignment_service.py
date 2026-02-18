"""
Tests for assignment service.
"""

import pytest
from app.models.developer import Developer
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.conversation import Conversation
from app.services.assignment_service import assignment_service


def test_assign_ticket_to_matching_developer(db):
    """
    Test that tickets are assigned to developers with matching technical areas.
    """
    # Create developers
    backend_dev = Developer(
        name="Backend Dev",
        email="backend@test.com",
        technical_areas=["backend", "database"],
        is_active=True,
        max_concurrent_tickets=5
    )
    frontend_dev = Developer(
        name="Frontend Dev",
        email="frontend@test.com",
        technical_areas=["frontend"],
        is_active=True,
        max_concurrent_tickets=5
    )
    
    db.add(backend_dev)
    db.add(frontend_dev)
    db.commit()
    
    # Create conversation
    conversation = Conversation(
        audio_file_path="/test/audio.wav",
        japanese_transcript="テスト",
        english_translation="Test"
    )
    db.add(conversation)
    db.commit()
    
    # Create backend ticket
    ticket = Ticket(
        ticket_number="TEST-001",
        title="Database issue",
        description="Database connection problem",
        priority=TicketPriority.HIGH,
        technical_area="backend",
        conversation_id=conversation.id
    )
    db.add(ticket)
    db.commit()
    
    # Assign ticket
    import asyncio
    assigned_dev = asyncio.run(assignment_service.assign_ticket(db, ticket))
    
    # Should assign to backend developer
    assert assigned_dev.id == backend_dev.id
    assert ticket.status == TicketStatus.ASSIGNED
    assert ticket.assigned_developer_id == backend_dev.id


def test_assign_ticket_based_on_workload(db):
    """
    Test that tickets are assigned to developers with lower workload.
    """
    # Create two backend developers
    dev1 = Developer(
        name="Dev 1",
        email="dev1@test.com",
        technical_areas=["backend"],
        is_active=True,
        max_concurrent_tickets=5
    )
    dev2 = Developer(
        name="Dev 2",
        email="dev2@test.com",
        technical_areas=["backend"],
        is_active=True,
        max_concurrent_tickets=5
    )
    
    db.add_all([dev1, dev2])
    db.commit()
    
    # Create conversation
    conversation = Conversation(
        audio_file_path="/test/audio.wav",
        japanese_transcript="テスト",
        english_translation="Test"
    )
    db.add(conversation)
    db.commit()
    
    # Assign 2 tickets to dev1
    for i in range(2):
        conv = Conversation(
            audio_file_path=f"/test/audio{i}.wav"
        )
        db.add(conv)
        db.commit()
        
        ticket = Ticket(
            ticket_number=f"TEST-00{i}",
            title=f"Issue {i}",
            description=f"Description {i}",
            priority=TicketPriority.MEDIUM,
            technical_area="backend",
            conversation_id=conv.id,
            assigned_developer_id=dev1.id,
            status=TicketStatus.IN_PROGRESS
        )
        db.add(ticket)
    db.commit()
    
    # Create new ticket
    new_ticket = Ticket(
        ticket_number="TEST-NEW",
        title="New issue",
        description="New description",
        priority=TicketPriority.MEDIUM,
        technical_area="backend",
        conversation_id=conversation.id
    )
    db.add(new_ticket)
    db.commit()
    
    # Assign ticket
    import asyncio
    assigned_dev = asyncio.run(assignment_service.assign_ticket(db, new_ticket))
    
    # Should assign to dev2 (lower workload)
    assert assigned_dev.id == dev2.id
