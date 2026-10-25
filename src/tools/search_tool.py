import re
from typing import Any, Dict
from src.client.gemini_client import GeminiClient
from src.prompts.system.theodore_persona import THEODORE_SYSTEM_PROMPT


def strip_markdown(text: str) -> str:
    """Strips markdown asterisks, hashes, backticks, and bullet dashes for telephony voice delivery."""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^\s*[-*•]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"https?://\S+", "", text)  # Strip raw URLs
    return text.strip()


class SearchTool:
    """Encapsulates e-commerce, product pricing, and live news queries via Google Search Grounding."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    async def execute(self, query: str, language: str = "en") -> Dict[str, Any]:
        """Executes grounded search query and formats output strictly under CRIT-VOICE-01 contract."""
        prompt = (
            f"Caller query: {query}\n"
            f"Language requirement: Respond in {language}. Compare real-time pricing across stores if applicable. "
            "Follow the Voice-Delivery Contract CRIT-VOICE-01 strictly: no markdown, no URLs, maximum 2 to 3 spoken sentences."
        )

        result = await self.gemini_client.generate_with_search_grounding(
            prompt=prompt,
            system_instruction=THEODORE_SYSTEM_PROMPT,
        )

        spoken_text = strip_markdown(result.get("text", ""))

        return {
            "tool_name": "search_tool",
            "spoken_output": spoken_text,
            "grounding_sources": result.get("grounding_sources", []),
        }
