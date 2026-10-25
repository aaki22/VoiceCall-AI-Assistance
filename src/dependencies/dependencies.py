from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.call_orchestrator_graph import CallOrchestratorGraph
from src.client.gemini_client import GeminiClient
from src.client.inworld_tts_client import InworldTTSClient
from src.client.vobiz_adapter import VobizAdapter
from src.database.database import get_db
from src.repository.audit_repository import AuditRepository
from src.repository.call_session_repository import CallSessionRepository
from src.repository.reminder_repository import ReminderRepository
from src.service.audio_stream_pipeline import AudioStreamPipeline
from src.service.audit_service import AuditService
from src.service.call_session_service import CallSessionService
from src.service.reminder_service import ReminderService

# Singletons for stateless clients & streaming pipelines
_gemini_client = GeminiClient()
_inworld_tts_client = InworldTTSClient()
_vobiz_adapter = VobizAdapter()
_audio_stream_pipeline = AudioStreamPipeline()


def get_gemini_client() -> GeminiClient:
    return _gemini_client


def get_inworld_tts_client() -> InworldTTSClient:
    return _inworld_tts_client


def get_vobiz_adapter() -> VobizAdapter:
    return _vobiz_adapter


def get_audio_stream_pipeline() -> AudioStreamPipeline:
    return _audio_stream_pipeline


def get_call_session_repository(db: AsyncSession = Depends(get_db)) -> CallSessionRepository:
    return CallSessionRepository(db)


def get_reminder_repository(db: AsyncSession = Depends(get_db)) -> ReminderRepository:
    return ReminderRepository(db)


def get_audit_repository(db: AsyncSession = Depends(get_db)) -> AuditRepository:
    return AuditRepository(db)


def get_audit_service(
    repo: AuditRepository = Depends(get_audit_repository),
) -> AuditService:
    return AuditService(repo)


def get_reminder_service(
    repo: ReminderRepository = Depends(get_reminder_repository),
    vobiz: VobizAdapter = Depends(get_vobiz_adapter),
) -> ReminderService:
    return ReminderService(repo, vobiz)


def get_call_orchestrator_graph(
    gemini: GeminiClient = Depends(get_gemini_client),
    reminder_repo: ReminderRepository = Depends(get_reminder_repository),
) -> CallOrchestratorGraph:
    return CallOrchestratorGraph(gemini, reminder_repo)


def get_call_session_service(
    call_repo: CallSessionRepository = Depends(get_call_session_repository),
    orchestrator: CallOrchestratorGraph = Depends(get_call_orchestrator_graph),
    tts_client: InworldTTSClient = Depends(get_inworld_tts_client),
    vobiz_adapter: VobizAdapter = Depends(get_vobiz_adapter),
    audit_service: AuditService = Depends(get_audit_service),
    stream_pipeline: AudioStreamPipeline = Depends(get_audio_stream_pipeline),
) -> CallSessionService:
    return CallSessionService(
        call_repo=call_repo,
        orchestrator=orchestrator,
        tts_client=tts_client,
        vobiz_adapter=vobiz_adapter,
        audit_service=audit_service,
        stream_pipeline=stream_pipeline,
    )
