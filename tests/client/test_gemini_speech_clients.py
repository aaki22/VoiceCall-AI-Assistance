import pytest

from src.client.gemini_client import GeminiClient
from src.client.speech_recognition_client import SpeechRecognitionClient
from src.exception.exceptions import LLMProviderException


class TestGeminiResponse:
    __test__ = False

    text = " hello "


class TestModels:
    __test__ = False

    def generate_content(self, **kwargs):
        return TestGeminiResponse()


class TestGenAIClient:
    __test__ = False

    def __init__(self, api_key):
        self.models = TestModels()


def test_gemini_client_returns_trimmed_text(monkeypatch):
    monkeypatch.setattr("src.client.gemini_client.genai.Client", TestGenAIClient)

    assert GeminiClient("key", "model").generate_text("prompt") == "hello"


def test_gemini_client_raises_controlled_error(monkeypatch):
    class BrokenModels:
        def generate_content(self, **kwargs):
            raise RuntimeError()

    class BrokenClient:
        def __init__(self, api_key):
            self.models = BrokenModels()

    monkeypatch.setattr("src.client.gemini_client.genai.Client", BrokenClient)

    with pytest.raises(LLMProviderException):
        GeminiClient("key", "model").generate_text("prompt")


def test_speech_recognition_client_returns_empty_on_failure(monkeypatch):
    class TestRecognizer:
        __test__ = False

        def record(self, source):
            return "audio"

        def recognize_google(self, audio, language):
            raise RuntimeError()

    class TestAudioFile:
        __test__ = False

        def __init__(self, path):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr("src.client.speech_recognition_client.sr.Recognizer", TestRecognizer)
    monkeypatch.setattr("src.client.speech_recognition_client.sr.AudioFile", TestAudioFile)

    assert SpeechRecognitionClient().transcribe_wav("a.wav", "ta-IN") == ""
