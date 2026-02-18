"""
Tests for ticket service.
"""

import pytest
from app.services.ticket_service import ticket_service


@pytest.mark.asyncio
async def test_generate_ticket_from_text():
    """
    Test ticket generation from English text.
    """
    english_text = """The production database is running slow. 
    Query response times have increased from 100ms to 5 seconds. 
    This is affecting user logins and we need immediate help."""
    
    ticket_data = await ticket_service.generate_ticket_from_text(english_text)
    
    assert "title" in ticket_data
    assert "description" in ticket_data
    assert "priority" in ticket_data
    assert "category" in ticket_data
    assert "technical_area" in ticket_data
    
    # Verify priority is valid
    assert ticket_data["priority"] in ["low", "medium", "high", "critical"]
    
    # Title should be shorter than description
    assert len(ticket_data["title"]) < len(ticket_data["description"])
    
    # Title should not exceed max length
    assert len(ticket_data["title"]) <= 200


@pytest.mark.asyncio
async def test_ticket_generation_consistency():
    """
    Test that same input produces consistent output.
    """
    english_text = "Database connection timeout error in production"
    
    result1 = await ticket_service.generate_ticket_from_text(english_text)
    result2 = await ticket_service.generate_ticket_from_text(english_text)
    
    # Category and technical area should be consistent
    assert result1["category"] == result2["category"]
    assert result1["technical_area"] == result2["technical_area"]
