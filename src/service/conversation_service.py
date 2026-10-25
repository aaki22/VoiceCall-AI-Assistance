import logging
import uuid

from src.agents.phone_assistant_graph import PhoneAssistantGraph
from src.models.graph_state import PhoneAssistantState
from src.repository.call_repository import CallRepository
from src.service.audio_service import AudioService
from src.settings.settings import settings


logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(
        self,
        call_repository: CallRepository,
        audio_service: AudioService,
        assistant_graph: PhoneAssistantGraph,
    ):
        self._call_repository = call_repository
        self._audio_service = audio_service
        self._assistant_graph = assistant_graph

    def start_call(self) -> tuple[str, str]:
        session_id = str(uuid.uuid4())
        self._call_repository.create_call_session(session_id)
        greeting = "Hello! I am Theodore. வணக்கம்! நான் உங்கள் AI உதவியாளர். எப்படி உதவலாம்?"
        audio_file = self._audio_service.generate_tts(greeting)
        logger.info("Conversation started session_id=%s", session_id)
        return session_id, audio_file

    def process_recording(self, session_id: str, record_url: str) -> PhoneAssistantState:
        state = PhoneAssistantState(session_id=session_id, record_url=record_url)
        logger.info("Conversation turn processing started session_id=%s", session_id)
        return self._assistant_graph.run_turn(state)


def build_record_xml(session_id: str) -> str:
    return (
        f'<Record action="{settings.public_url}/process-recording?session_id={session_id}" '
        'method="POST" maxLength="10" playBeep="true"/>'
    )
