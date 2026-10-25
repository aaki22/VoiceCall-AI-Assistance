from pydantic import BaseModel

from src.client.llm_client import LLMClient


class Output(BaseModel):
    name: str = "fallback"


class TestLLM(LLMClient):
    __test__ = False

    def __init__(self, text):
        self.text = text

    def generate_text(self, prompt):
        return self.text


def test_generate_structured_parses_json_from_markdown():
    result = TestLLM('```json\n{"name": "ok"}\n```').generate_structured("prompt", Output, Output())

    assert result.name == "ok"


def test_generate_structured_returns_fallback_for_invalid_json():
    result = TestLLM("not json").generate_structured("prompt", Output, Output())

    assert result.name == "fallback"
