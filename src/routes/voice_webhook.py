import logging

from fastapi import APIRouter, Depends, Request, Response

from src.constants.routes import INBOUND_PATH, PROCESS_RECORDING_PATH
from src.dependencies.services import get_conversation_service
from src.service.conversation_service import ConversationService, build_record_xml
from src.settings.settings import settings


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(INBOUND_PATH)
async def inbound_call(conversation_service: ConversationService = Depends(get_conversation_service)):
    session_id, audio_file = conversation_service.start_call()
    logger.info("Inbound call session started session_id=%s audio_file=%s", session_id, audio_file)
    xml = f"""
<Response>
<Play>{settings.public_url}/audio/{audio_file}</Play>
{build_record_xml(session_id)}
</Response>
"""
    return Response(xml, media_type="application/xml")


@router.post(PROCESS_RECORDING_PATH)
async def process_recording(
    request: Request,
    session_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    data = await request.form()
    record_url = data.get("RecordUrl", "")
    if not record_url:
        logger.warning("Recording callback missing RecordUrl session_id=%s", session_id)
    state = conversation_service.process_recording(session_id, record_url)

    if state.should_end_call:
        logger.info("Call hangup response generated session_id=%s", session_id)
        xml = f"<Response><Play>{settings.public_url}/audio/{state.ai_audio_file}</Play><Hangup/></Response>"
        return Response(xml, media_type="application/xml")

    xml = f"""
<Response>
<Play>{settings.thinking_music_url}</Play>
<Play>{settings.public_url}/audio/{state.ai_audio_file}</Play>
{build_record_xml(session_id)}
</Response>
"""
    return Response(xml, media_type="application/xml")
    logger.info("Call continue response generated session_id=%s", session_id)
