import re
from typing import Any, Dict
from src.client.gemini_client import GeminiClient
from src.prompts.system.theodore_persona import THEODORE_SYSTEM_PROMPT


def strip_markdown(text: str) -> str:
    """Strips markdown and URLs for telephony delivery."""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"https?://\S+", "", text)
    return text.strip()


class MapsTool:
    """Encapsulates local place lookups (clinics, mechanics, pharmacies) with Google Maps grounding."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    async def execute(self, query: str, language: str = "en") -> Dict[str, Any]:
        """Executes isolated Google Maps grounding lookup."""
        prompt = (
            f"Caller location lookup: {query}\n"
            f"Language requirement: Respond in {language}. Provide the top relevant local place, landmark, and contact if known. "
            "Follow Voice-Delivery Contract CRIT-VOICE-01: no markdown, no URLs, maximum 2 sentences."
        )

        result = await self.gemini_client.generate_with_maps_grounding(
            prompt=prompt,
            system_instruction=THEODORE_SYSTEM_PROMPT,
        )

        spoken_text = strip_markdown(result.get("text", ""))

        return {
            "tool_name": "maps_tool",
            "spoken_output": spoken_text,
            "grounding_sources": result.get("grounding_sources", []),
        }
