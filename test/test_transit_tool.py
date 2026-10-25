import pytest
from unittest.mock import AsyncMock
from src.client.gemini_client import GeminiClient
from src.tools.transit_tool import TransitTool


@pytest.mark.asyncio
async def test_transit_guardrail_blocks_ticket_booking():
    """Verify that ticket booking requests are blocked by CRIT-TRANSIT-01 and cite 139."""
    mock_gemini = AsyncMock(spec=GeminiClient)
    tool = TransitTool(mock_gemini)

    # User attempts to book a train ticket
    query = "Cheran express-la 2 berths book pannunga"
    result = await tool.execute(query, language="ta")

    # Guardrail must refuse booking and offer 139 helpline without calling external LLM
    assert result["booking_refused"] is True
    assert result["guardrail_enforced"] == "CRIT-TRANSIT-01"
    assert result["helpline_offered"] == "139"
    assert "139" in result["spoken_output"]
    assert mock_gemini.generate_with_search_grounding.call_count == 0


@pytest.mark.asyncio
async def test_transit_schedule_enquiry_allowed():
    """Verify that schedule inquiries pass through to grounded timetables."""
    mock_gemini = AsyncMock(spec=GeminiClient)
    mock_gemini.generate_with_search_grounding.return_value = {
        "text": "Cheran Express departs Chennai Central at 6:10 AM.",
        "grounding_sources": [{"title": "Southern Railway", "uri": "https://indianrailways.gov.in"}],
    }

    tool = TransitTool(mock_gemini)
    query = "Cheran express departure time enna?"
    result = await tool.execute(query, language="en")

    assert result["booking_refused"] is False
    assert result["guardrail_enforced"] is None
    assert "Cheran Express" in result["spoken_output"]
    assert mock_gemini.generate_with_search_grounding.call_count == 1
