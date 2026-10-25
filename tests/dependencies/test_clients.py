from src.client.geocoding_client import GeocodingClient
from src.client.inworld_tts_client import InworldTTSClient
from src.client.recording_client import RecordingClient
from src.client.speech_recognition_client import SpeechRecognitionClient
from src.client.traffic_client import TrafficClient
from src.dependencies.clients import (
    get_geocoding_client,
    get_recording_client,
    get_speech_recognition_client,
    get_traffic_client,
    get_tts_client,
)


def test_client_dependency_factories_return_expected_types():
    assert isinstance(get_geocoding_client(), GeocodingClient)
    assert isinstance(get_traffic_client(), TrafficClient)
    assert isinstance(get_recording_client(), RecordingClient)
    assert isinstance(get_tts_client(), InworldTTSClient)
    assert isinstance(get_speech_recognition_client(), SpeechRecognitionClient)
