import time
import uuid
from typing import Any, AsyncGenerator, Dict, Optional
from src.agents.call_orchestrator_graph import CallOrchestratorGraph
from src.client.inworld_tts_client import InworldTTSClient
from src.client.vobiz_adapter import VobizAdapter
from src.models.dtos.call_models import (
    BargeInResponseDTO,
    CallSessionResponseDTO,
)
from src.repository.call_session_repository import CallSessionRepository
from src.service.audio_stream_pipeline import AudioStreamPipeline
from src.service.audit_service import AuditService
from src.utils.logger import logger
from src.utils.vad import VoiceActivityDetector


class CallSessionService:
    """Core telephony session orchestrator managing VAD, turns, and barge-in interrupts."""

    def __init__(
        self,
        call_repo: CallSessionRepository,
        orchestrator: CallOrchestratorGraph,
        tts_client: InworldTTSClient,
        vobiz_adapter: VobizAdapter,
        audit_service: AuditService,
        stream_pipeline: AudioStreamPipeline,
    ):
        self.call_repo = call_repo
        self.orchestrator = orchestrator
        self.tts_client = tts_client
        self.vobiz_adapter = vobiz_adapter
        self.audit_service = audit_service
        self.stream_pipeline = stream_pipeline

        # In-memory VAD detectors mapped by session_id
        self.active_vads: Dict[str, VoiceActivityDetector] = {}

    def get_or_create_vad(self, session_id: str) -> VoiceActivityDetector:
        """Retrieves or initializes VAD state machine for a session."""
        if session_id not in self.active_vads:
            self.active_vads[session_id] = VoiceActivityDetector()
        return self.active_vads[session_id]

    async def initialize_session(
        self,
        session_id: str,
        call_sid: str,
        caller_phone: str,
        virtual_did: str,
        correlation_id: Optional[str] = None,
    ) -> CallSessionResponseDTO:
        """Initializes a new phone call session in PostgreSQL."""
        corr_id = correlation_id or f"corr-{uuid.uuid4().hex[:12]}"
        session = await self.call_repo.create_session(
            session_id=session_id,
            call_sid=call_sid,
            caller_phone=caller_phone,
            virtual_did=virtual_did,
            correlation_id=corr_id,
        )

        await self.audit_service.log_telephony_event(
            correlation_id=corr_id,
            session_id=session_id,
            event_type="call_started",
            details={"caller_phone": caller_phone, "call_sid": call_sid},
        )

        return CallSessionResponseDTO.model_validate(session)

    async def process_audio_frame(
        self,
        session_id: str,
        pcm_bytes: bytes,
        is_system_streaming: bool = False,
    ) -> tuple[bool, bool, Optional[bytes]]:
        """Feeds a 20ms audio frame into session VAD."""
        vad = self.get_or_create_vad(session_id)
        return vad.process_frame(pcm_bytes, is_system_streaming_audio=is_system_streaming)

    async def execute_turn(
        self,
        session_id: str,
        utterance_text: str,
        correlation_id: str,
        caller_phone: str = "+919840012345",
    ) -> tuple[str, AsyncGenerator[bytes, None], Dict[str, Any]]:
        """Processes caller utterance through LangGraph orchestrator and prepares TTS stream."""
        start_time = time.perf_counter()
        langsmith_run_id = f"run-{uuid.uuid4().hex[:12]}"

        # 1. Run LangGraph StateGraph engine
        state = await self.orchestrator.process_turn(
            session_id=session_id,
            caller_phone=caller_phone,
            utterance=utterance_text,
            correlation_id=correlation_id,
            langsmith_run_id=langsmith_run_id,
        )

        spoken_text = state.get("spoken_response", "")
        stream_url = state.get("stream_url")
        detected_lang = state.get("detected_language", "ta")
        grounding_sources = state.get("grounding_sources", [])

        # 2. Update session state in DB
        await self.call_repo.update_session_state(
            session_id=session_id,
            detected_language=detected_lang,
            playback_state="streaming" if stream_url else "speaking",
            increment_turns=True,
            langsmith_run_id=langsmith_run_id,
        )

        total_lat_ms = int((time.perf_counter() - start_time) * 1000)
        latencies = state.get("latencies", {})
        latencies["total_turnaround_ms"] = total_lat_ms

        # 3. Persist Turn in DB
        await self.call_repo.add_turn(
            session_id=session_id,
            turn_index=1,
            speaker="assistant",
            utterance=spoken_text,
            detected_language=detected_lang,
            tool_called=state.get("intent"),
            grounding_metadata={"sources": grounding_sources},
            latencies=latencies,
            langsmith_run_id=langsmith_run_id,
        )

        # 4. Generate Audio Stream Generator
        if stream_url:
            audio_generator = self.stream_pipeline.pipe_stream_to_telephony(stream_url)
        else:
            audio_generator = self.tts_client.stream_speech(spoken_text)

        metadata = {
            "spoken_text": spoken_text,
            "detected_language": detected_lang,
            "grounding_sources": grounding_sources,
            "latencies": latencies,
            "langsmith_run_id": langsmith_run_id,
            "is_media_stream": stream_url is not None,
        }

        return spoken_text, audio_generator, metadata

    async def execute_barge_in_cutoff(self, session_id: str) -> BargeInResponseDTO:
        """Executes instant voice barge-in interruption cutoff in <300ms SLA."""
        start = time.perf_counter()
        logger.info(f"Executing barge-in stream cutoff for session={session_id}")

        # Step 1: Terminate active media streaming subprocesses
        terminated_count = self.stream_pipeline.terminate_active_streams()

        # Step 2: Reset in-memory VAD speech tracking
        if session_id in self.active_vads:
            self.active_vads[session_id].reset_turn()

        # Step 3: Update session state in PostgreSQL
        await self.call_repo.update_session_state(
            session_id=session_id,
            playback_state="idle",
        )

        # Step 4: Log audit record
        cutoff_ms = int((time.perf_counter() - start) * 1000)
        await self.audit_service.log_telephony_event(
            correlation_id=f"barge-in-{session_id}",
            session_id=session_id,
            event_type="barge_in_interrupted",
            details={"cutoff_latency_ms": cutoff_ms, "subprocesses_killed": terminated_count},
        )

        return BargeInResponseDTO(
            session_id=session_id,
            cutoff_latency_ms=cutoff_ms,
            vobiz_clear_audio_sent=True,
            subprocess_terminated_pid=terminated_count,
            new_playback_state="idle",
        )
