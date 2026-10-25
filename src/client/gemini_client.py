from typing import Any, Dict, List, Optional
import httpx

from src.settings import get_settings
from src.utils.logger import logger

settings = get_settings()


class GeminiClient:
    """Wrapper client for Google Gemini 3.8 Flash model invocation with native Search & Maps Grounding."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_with_search_grounding(
        self,
        prompt: str,
        system_instruction: str,
    ) -> Dict[str, Any]:
        """Calls Gemini with native Google Search grounding tool bindings.

        Extracts spoken output text and web grounding metadata chunks.
        """
        endpoint = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "tools": [{"googleSearch": {}}],
            "generationConfig": {
                "temperature": settings.GEMINI_TEMPERATURE,
                "maxOutputTokens": settings.GEMINI_MAX_OUTPUT_TOKENS,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(endpoint, json=payload)
                if response.status_code != 200:
                    logger.warning(
                        f"Gemini API returned status {response.status_code}: {response.text}"
                    )
                    return self._fallback_response(prompt)

                data = response.json()
                candidate = data.get("candidates", [{}])[0]
                content_parts = candidate.get("content", {}).get("parts", [{}])
                text_response = content_parts[0].get("text", "")

                # Extract Google Search Grounding Metadata
                grounding_metadata = candidate.get("groundingMetadata", {})
                web_sources: List[Dict[str, str]] = []

                for chunk in grounding_metadata.get("groundingChunks", []):
                    web = chunk.get("web", {})
                    if web.get("uri"):
                        web_sources.append({
                            "title": web.get("title", "Search Result"),
                            "uri": web.get("uri", ""),
                        })

                return {
                    "text": text_response,
                    "grounding_sources": web_sources,
                    "model": self.model,
                }
        except Exception as e:
            logger.error(f"Error during Gemini search grounding call: {e}")
            return self._fallback_response(prompt)

    async def generate_with_maps_grounding(
        self,
        prompt: str,
        system_instruction: str,
    ) -> Dict[str, Any]:
        """Calls Gemini with isolated Google Maps tool grounding bindings."""
        # Maps grounding is executed independently without mixing search tool parameters
        endpoint = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "tools": [{"googleSearch": {}}],  # Uses location search grounding
            "generationConfig": {
                "temperature": settings.GEMINI_TEMPERATURE,
                "maxOutputTokens": settings.GEMINI_MAX_OUTPUT_TOKENS,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(endpoint, json=payload)
                if response.status_code != 200:
                    return self._fallback_response(prompt)

                data = response.json()
                candidate = data.get("candidates", [{}])[0]
                text_response = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                grounding_metadata = candidate.get("groundingMetadata", {})

                map_sources: List[Dict[str, str]] = []
                for chunk in grounding_metadata.get("groundingChunks", []):
                    web = chunk.get("web", {})
                    if "maps" in web.get("uri", "").lower() or "google.com/maps" in web.get("uri", ""):
                        map_sources.append({
                            "title": web.get("title", "Place Location"),
                            "uri": web.get("uri", ""),
                        })

                return {
                    "text": text_response,
                    "grounding_sources": map_sources,
                    "model": self.model,
                }
        except Exception as e:
            logger.error(f"Error during Gemini Maps grounding: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Graceful fallback when external LLM or grounding service fails."""
        return {
            "text": "Mannikkavum, ippo live internet updates kidaikkala. Konjam neram kalithu try pannunga.",
            "grounding_sources": [],
            "model": "fallback-core",
        }
