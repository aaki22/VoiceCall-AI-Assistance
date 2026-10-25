from fastapi import Depends
from sqlalchemy.orm import Session

from src.agents.phone_assistant_graph import PhoneAssistantGraph
from src.agents.phone_assistant_nodes import PhoneAssistantNodes
from src.client.gemini_client import GeminiClient
from src.client.geocoding_client import GeocodingClient
from src.client.inworld_tts_client import InworldTTSClient
from src.client.recording_client import RecordingClient
from src.client.speech_recognition_client import SpeechRecognitionClient
from src.client.traffic_client import TrafficClient
from src.database.session import get_db
from src.dependencies.clients import (
    get_geocoding_client,
    get_llm_client,
    get_recording_client,
    get_speech_recognition_client,
    get_traffic_client,
    get_tts_client,
)
from src.repository.call_repository import CallRepository
from src.service.audio_service import AudioService
from src.service.conversation_service import ConversationService
from src.service.news_service import NewsService
from src.service.traffic_service import TrafficService
from src.tools.news_tool import NewsTool
from src.tools.traffic_tool import TrafficTool


def get_call_repository(db: Session = Depends(get_db)) -> CallRepository:
    return CallRepository(db)


def get_news_tool() -> NewsTool:
    return NewsTool()


def get_traffic_tool(
    geocoding_client: GeocodingClient = Depends(get_geocoding_client),
    traffic_client: TrafficClient = Depends(get_traffic_client),
) -> TrafficTool:
    return TrafficTool(geocoding_client, traffic_client)


def get_audio_service(
    recording_client: RecordingClient = Depends(get_recording_client),
    tts_client: InworldTTSClient = Depends(get_tts_client),
    speech_client: SpeechRecognitionClient = Depends(get_speech_recognition_client),
) -> AudioService:
    return AudioService(recording_client, tts_client, speech_client)


def get_news_service(news_tool: NewsTool = Depends(get_news_tool)) -> NewsService:
    return NewsService(news_tool)


def get_traffic_service(traffic_tool: TrafficTool = Depends(get_traffic_tool)) -> TrafficService:
    return TrafficService(traffic_tool)


def get_phone_assistant_graph(
    audio_service: AudioService = Depends(get_audio_service),
    llm_client: GeminiClient = Depends(get_llm_client),
    news_service: NewsService = Depends(get_news_service),
    traffic_service: TrafficService = Depends(get_traffic_service),
    call_repository: CallRepository = Depends(get_call_repository),
) -> PhoneAssistantGraph:
    nodes = PhoneAssistantNodes(
        audio_service=audio_service,
        llm_client=llm_client,
        news_service=news_service,
        traffic_service=traffic_service,
        call_repository=call_repository,
    )
    return PhoneAssistantGraph(nodes)


def get_conversation_service(
    call_repository: CallRepository = Depends(get_call_repository),
    audio_service: AudioService = Depends(get_audio_service),
    assistant_graph: PhoneAssistantGraph = Depends(get_phone_assistant_graph),
) -> ConversationService:
    return ConversationService(call_repository, audio_service, assistant_graph)
