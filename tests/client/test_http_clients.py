import base64

import pytest

from src.client.geocoding_client import GeocodingClient
from src.client.inworld_tts_client import InworldTTSClient
from src.client.recording_client import RecordingClient
from src.client.traffic_client import TrafficClient
from src.exception.exceptions import ExternalServiceException


class TestResponse:
    __test__ = False

    def __init__(self, payload=None, content=b"content", status_error=None):
        self._payload = payload
        self.content = content
        self._status_error = status_error

    def raise_for_status(self):
        if self._status_error:
            raise self._status_error

    def json(self):
        return self._payload


def test_geocoding_client_returns_lon_lat(monkeypatch):
    def test_get(*args, **kwargs):
        assert kwargs["timeout"] == 5
        return TestResponse([{"lat": "13.0", "lon": "80.0"}])

    monkeypatch.setattr("src.client.geocoding_client.requests.get", test_get)

    assert GeocodingClient(timeout_seconds=5).get_coordinates("chennai") == [80.0, 13.0]


def test_geocoding_client_raises_controlled_error(monkeypatch):
    monkeypatch.setattr("src.client.geocoding_client.requests.get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError()))

    with pytest.raises(ExternalServiceException):
        GeocodingClient(timeout_seconds=5).get_coordinates("x")


def test_traffic_client_returns_minutes(monkeypatch):
    monkeypatch.setattr(
        "src.client.traffic_client.requests.post",
        lambda *args, **kwargs: TestResponse({"routes": [{"summary": {"duration": 600}}]}),
    )

    assert TrafficClient(api_key="key", timeout_seconds=5).get_travel_minutes([1, 2], [3, 4]) == 10


def test_recording_client_downloads_content(monkeypatch):
    monkeypatch.setattr("src.client.recording_client.requests.get", lambda *args, **kwargs: TestResponse(content=b"abc"))

    assert RecordingClient("id", "token", 5).download("https://recording") == b"abc"


def test_tts_client_decodes_audio(monkeypatch):
    payload = {"audioContent": base64.b64encode(b"mp3").decode("ascii")}
    monkeypatch.setattr("src.client.inworld_tts_client.requests.post", lambda *args, **kwargs: TestResponse(payload))

    assert InworldTTSClient("url", "token", "voice", "model", 5).synthesize_mp3("hello") == b"mp3"
