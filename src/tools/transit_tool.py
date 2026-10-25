import re
from typing import Any, Dict
from src.client.gemini_client import GeminiClient
from src.prompts.tools.transit_rules import TRANSIT_GUARDRAIL_PROMPT


def strip_markdown(text: str) -> str:
    """Strips markdown and URLs for telephony delivery."""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"https?://\S+", "", text)
    return text.strip()


class TransitTool:
    """Delivers train schedules and routes while enforcing IRCTC reservation boundary guardrails (CRIT-TRANSIT-01)."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    async def execute(self, query: str, language: str = "ta") -> Dict[str, Any]:
        """Executes transit tool query with automated capability boundary check."""
        query_lower = query.lower()

        # Check for prohibited booking / live seat availability intent
        booking_keywords = [
            "book",
            "ticket",
            "berth",
            "seat availability",
            "tatkal",
            "rac",
            "waitlist",
            "booking",
            "புக்",
            "டிக்கெட்",
            "சீட்",
        ]
        is_booking_request = any(kw in query_lower for kw in booking_keywords)

        if is_booking_request:
            # Enforce CRIT-TRANSIT-01 Guardrail fallback
            if language == "ta":
                spoken = (
                    "ரயில் டிக்கெட் புக் செய்ய என்னால் முடியாது. "
                    "உறுதிப்படுத்தப்பட்ட டிக்கெட் விவரங்களுக்கு அதிகாரப்பூர்வ IRCTC தளம் அல்லது உதவி எண் 139-ஐ அழைக்கலாம். "
                    "உங்களுக்கு பயண நினைவூட்டல் பதிவு செய்ய வேண்டுமா?"
                )
            else:
                spoken = (
                    "I cannot book train tickets or verify live seat availability directly. "
                    "For official bookings and live berth status, please call Railway Helpline 139 or visit the IRCTC portal. "
                    "Would you like me to set a travel reminder for you?"
                )

            return {
                "tool_name": "transit_tool",
                "guardrail_enforced": "CRIT-TRANSIT-01",
                "booking_refused": True,
                "helpline_offered": "139",
                "spoken_output": spoken,
                "grounding_sources": [{"title": "Indian Railways Helpline 139", "uri": "https://indianrailways.gov.in"}],
            }

        # Otherwise retrieve scheduled train timings and routes via Gemini grounding
        prompt = (
            f"Caller transit enquiry: {query}\n"
            f"Language requirement: Respond in {language}. Provide train numbers, departure/arrival times, and major halts. "
            f"Strictly enforce the transit rules:\n{TRANSIT_GUARDRAIL_PROMPT}\n"
            "Keep response under 3 spoken sentences without any markdown or URLs."
        )

        result = await self.gemini_client.generate_with_search_grounding(
            prompt=prompt,
            system_instruction=TRANSIT_GUARDRAIL_PROMPT,
        )

        spoken_text = strip_markdown(result.get("text", ""))

        return {
            "tool_name": "transit_tool",
            "guardrail_enforced": None,
            "booking_refused": False,
            "spoken_output": spoken_text,
            "grounding_sources": result.get("grounding_sources", []),
        }
