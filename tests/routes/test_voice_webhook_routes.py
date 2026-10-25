from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.dependencies.services import get_conversation_service
from src.models.graph_state import PhoneAssistantState
from src.routes.voice_webhook import router


class TestConversationService:
    __test__ = False

    def start_call(self):
        return "session-1", "greeting.wav"

    def process_recording(self, session_id, record_url):
        return PhoneAssistantState(
            session_id=session_id,
            record_url=record_url,
            ai_audio_file="reply.wav",
            should_end_call=False,
        )


class TestEndConversationService(TestConversationService):
    __test__ = False

    def process_recording(self, session_id, record_url):
        return PhoneAssistantState(
            session_id=session_id,
            record_url=record_url,
            ai_audio_file="bye.wav",
            should_end_call=True,
        )


def make_client(service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_conversation_service] = lambda: service
    return TestClient(app)


def test_inbound_route_returns_xml():
    response = make_client(TestConversationService()).post("/inbound")

    assert response.headers["content-type"].startswith("application/xml")
    assert "<Play>" in response.text
    assert "<Record" in response.text


def test_process_recording_route_continues_call():
    response = make_client(TestConversationService()).post(
        "/process-recording?session_id=session-1",
        data={"RecordUrl": "https://recording"},
    )

    assert "<Hangup" not in response.text
    assert "<Record" in response.text


def test_process_recording_route_hangs_up():
    response = make_client(TestEndConversationService()).post(
        "/process-recording?session_id=session-1",
        data={"RecordUrl": "https://recording"},
    )

    assert "<Hangup" in response.text
