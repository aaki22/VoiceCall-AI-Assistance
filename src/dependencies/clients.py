from src.client.gemini_client import GeminiClient
from src.client.geocoding_client import GeocodingClient
from src.client.inworld_tts_client import InworldTTSClient
from src.client.recording_client import RecordingClient
from src.client.speech_recognition_client import SpeechRecognitionClient
from src.client.traffic_client import TrafficClient
from src.settings.settings import settings


def get_llm_client() -> GeminiClient:
    return GeminiClient(
        api_key=settings.gemini_api_key.get_secret_value(),
        model=settings.gemini_model,
    )


def get_geocoding_client() -> GeocodingClient:
    return GeocodingClient(timeout_seconds=settings.http_timeout_seconds)


def get_traffic_client() -> TrafficClient:
    return TrafficClient(
        api_key=settings.ors_api_key.get_secret_value(),
        timeout_seconds=settings.http_timeout_seconds,
    )


def get_recording_client() -> RecordingClient:
    return RecordingClient(
        auth_id=settings.auth_id,
        auth_token=settings.auth_token.get_secret_value(),
        timeout_seconds=settings.http_timeout_seconds,
    )


def get_tts_client() -> InworldTTSClient:
    return InworldTTSClient(
        url=settings.inworld_tts_url,
        auth_token=settings.inworld_tts_auth.get_secret_value(),
        voice_id=settings.inworld_voice_id,
        model_id=settings.inworld_model_id,
        timeout_seconds=settings.http_timeout_seconds,
    )


def get_speech_recognition_client() -> SpeechRecognitionClient:
    return SpeechRecognitionClient()
