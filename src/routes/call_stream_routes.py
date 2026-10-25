import base64
import json
import uuid
from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    Form,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from src.client.vobiz_adapter import VobizAdapter
from src.dependencies.dependencies import (
    get_call_session_repository,
    get_call_session_service,
    get_vobiz_adapter,
)
from src.models.dtos.call_models import (
    BargeInResponseDTO,
    CallSessionResponseDTO,
    ConversationTurnDTO,
)
from src.models.responses.response_models import ResponseBuilder, StandardResponse
from src.repository.call_session_repository import CallSessionRepository
from src.service.call_session_service import CallSessionService
from src.settings import get_settings
from src.utils.logger import logger

router = APIRouter(prefix="/api/v1/telephony", tags=["Telephony"])
settings = get_settings()


@router.post("/webhook")
async def handle_vobiz_inbound_webhook(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    service: CallSessionService = Depends(get_call_session_service),
    vobiz: VobizAdapter = Depends(get_vobiz_adapter),
):
    """Vobiz Carrier Inbound Call Webhook.

    Allocates a session and returns VobizXML directing the carrier to stream 8kHz PCM via WebSocket.
    """
    session_id = f"sess-{uuid.uuid4().hex[:12]}"
    correlation_id = f"corr-{uuid.uuid4().hex[:12]}"

    # Initialize session in PostgreSQL
    await service.initialize_session(
        session_id=session_id,
        call_sid=CallSid,
        caller_phone=From,
        virtual_did=To,
        correlation_id=correlation_id,
    )

    # Build WebSocket URL
    ws_protocol = "wss" if settings.PUBLIC_APP_URL.startswith("https") else "ws"
    clean_host = settings.PUBLIC_APP_URL.replace("https://", "").replace("http://", "")
    stream_url = f"{ws_protocol}://{clean_host}/api/v1/telephony/stream/{session_id}"

    xml_response = vobiz.build_stream_xml(stream_url)
    return Response(content=xml_response, media_type="application/xml")


@router.websocket("/stream/{session_id}")
async def handle_telephony_websocket(
    websocket: WebSocket,
    session_id: str,
    service: CallSessionService = Depends(get_call_session_service),
    vobiz: VobizAdapter = Depends(get_vobiz_adapter),
):
    """Bi-directional 8kHz linear PCM telephony WebSocket stream handler.

    Receives Vobiz 'start' and 'media' frames, monitors VAD for 600ms silence turn boundary,
    executes LangGraph agent turns, pipes synthesized speech via 'playAudio', and enforces
    instant barge-in cutoff upon detecting voice during playback.
    """
    await websocket.accept()
    stream_id = None
    is_streaming = False
    logger.info(f"WebSocket connection established for session={session_id}")

    try:
        while True:
            raw_data = await websocket.receive_text()
            message = json.loads(raw_data)
            event_type = message.get("event")

            # 1. Handle Vobiz 'start' event
            if event_type == "start":
                start_data = message.get("start", {})
                stream_id = start_data.get("streamId")
                call_id = start_data.get("callId")
                logger.info(
                    f"Telephony stream started: streamId={stream_id}, callId={call_id}"
                )

            # 2. Handle incoming caller audio frames
            elif event_type == "media":
                media_data = message.get("media", {})
                payload_b64 = media_data.get("payload", "")
                if not payload_b64:
                    continue

                pcm_chunk = base64.b64decode(payload_b64)

                # Process frame through Voice Activity Detection
                turn_done, barge_in, completed_pcm = await service.process_audio_frame(
                    session_id=session_id,
                    pcm_bytes=pcm_chunk,
                    is_system_streaming=is_streaming,
                )

                # A. Handle Barge-In Interruption during active playback
                if barge_in and stream_id:
                    logger.info(f"Barge-in detected on session={session_id}. Flushing audio!")
                    is_streaming = False
                    # Send clearAudio event to Vobiz immediately
                    clear_msg = vobiz.build_clear_audio_message(stream_id)
                    await websocket.send_text(clear_msg)
                    await service.execute_barge_in_cutoff(session_id)

                # B. Handle Turn-Taking Boundary (Caller stopped speaking > 600ms)
                if turn_done and stream_id:
                    # In real production with STT, completed_pcm is transcribed to text.
                    # Here we simulate or process the captured turn utterance:
                    mock_utterance = "Chennai Central train timings and weather"
                    spoken_text, audio_stream, metadata = await service.execute_turn(
                        session_id=session_id,
                        utterance_text=mock_utterance,
                        correlation_id=f"turn-{uuid.uuid4().hex[:8]}",
                    )

                    is_streaming = True
                    # Stream synthesized/transcoded PCM chunks back to caller
                    async for out_pcm in audio_stream:
                        if not is_streaming:
                            break  # Barge-in interrupted
                        play_msg = vobiz.build_play_audio_message(stream_id, out_pcm)
                        await websocket.send_text(play_msg)

                    is_streaming = False

            # 3. Handle playback checkpoint acknowledgments
            elif event_type == "clearedAudio":
                logger.info(f"Vobiz acknowledged audio queue flushed for session={session_id}")

            elif event_type == "stop":
                logger.info(f"Telephony stream stopped for session={session_id}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for session={session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session={session_id}: {e}")
    finally:
        await service.execute_barge_in_cutoff(session_id)


@router.get("/sessions", response_model=StandardResponse[List[CallSessionResponseDTO]])
async def list_telephony_sessions(
    status: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    repo: CallSessionRepository = Depends(get_call_session_repository),
):
    """Lists telephony call sessions."""
    sessions = await repo.list_sessions(status=status, language=language, limit=limit, offset=offset)
    dtos = [CallSessionResponseDTO.model_validate(s) for s in sessions]
    return ResponseBuilder.success(data=dtos, message="Telephony sessions retrieved")


@router.get("/sessions/{session_id}", response_model=StandardResponse[CallSessionResponseDTO])
async def get_telephony_session(
    session_id: str,
    repo: CallSessionRepository = Depends(get_call_session_repository),
):
    """Retrieves metadata for a specific telephony session."""
    session = await repo.get_by_session_id(session_id)
    if not session:
        return ResponseBuilder.success(data=None, message="Session not found", code=404)
    return ResponseBuilder.success(data=CallSessionResponseDTO.model_validate(session))


@router.get("/sessions/{session_id}/turns", response_model=StandardResponse[List[ConversationTurnDTO]])
async def get_session_turns(
    session_id: str,
    repo: CallSessionRepository = Depends(get_call_session_repository),
):
    """Retrieves conversation turns for a session."""
    turns = await repo.get_turns_by_session_id(session_id)
    dtos = [ConversationTurnDTO.model_validate(t) for t in turns]
    return ResponseBuilder.success(data=dtos, message="Session turns retrieved")


@router.post("/stream/barge-in/{session_id}", response_model=StandardResponse[BargeInResponseDTO])
async def trigger_barge_in(
    session_id: str,
    service: CallSessionService = Depends(get_call_session_service),
):
    """Manual trigger to simulate or force an instant barge-in interrupt cutoff."""
    result = await service.execute_barge_in_cutoff(session_id)
    return ResponseBuilder.success(data=result, message="Barge-in stream cutoff executed")
