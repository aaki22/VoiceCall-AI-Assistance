import logging

from google import genai

from src.client.llm_client import LLMClient
from src.exception.exceptions import LLMProviderException


logger = logging.getLogger(__name__)


class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate_text(self, prompt: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
            )
            return (response.text or "").strip()
        except Exception as exc:
            logger.exception("Gemini request failed model=%s", self._model)
            raise LLMProviderException("LLM provider request failed") from exc
