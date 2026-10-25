import json

from pydantic import BaseModel, ValidationError

from src.exception.exceptions import LLMProviderException


class LLMClient:
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError

    def generate_structured(self, prompt: str, dto_type: type[BaseModel], fallback: BaseModel) -> BaseModel:
        try:
            text = self.generate_text(prompt)
            json_text = _extract_json(text)
            return dto_type.model_validate(json.loads(json_text))
        except (json.JSONDecodeError, ValidationError, LLMProviderException):
            return fallback


def _extract_json(text: str) -> str:
    cleaned = text.strip().replace("```json", "").replace("```", "")
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start < 0 or end <= start:
        raise json.JSONDecodeError("No JSON object found", cleaned, 0)
    return cleaned[start:end]
