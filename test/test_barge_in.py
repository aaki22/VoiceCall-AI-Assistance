import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.call_orchestrator_graph import CallOrchestratorGraph
from src.client.inworld_tts_client import InworldTTSClient
from src.client.vobiz_adapter import VobizAdapter
from src.repository.call_session_repository import CallSessionRepository
from src.service.audio_stream_pipeline import AudioStreamPipeline
from src.service.audit_service import AuditService
from src.service.call_session_service import CallSessionService


@pytest.mark.asyncio
async def test_barge_in_cutoff_terminates_pipeline_and_resets_state():
    """Verify that barge-in halts subprocesses and updates session state to idle in <300ms."""
    mock_call_repo = AsyncMock(spec=CallSessionRepository)
    mock_orchestrator = AsyncMock(spec=CallOrchestratorGraph)
    mock_tts = AsyncMock(spec=InworldTTSClient)
    mock_vobiz = MagicMock(spec=VobizAdapter)
    mock_audit = AsyncMock(spec=AuditService)
    mock_stream_pipeline = MagicMock(spec=AudioStreamPipeline)
    mock_stream_pipeline.terminate_active_streams.return_value = 1

    service = CallSessionService(
        call_repo=mock_call_repo,
        orchestrator=mock_orchestrator,
        tts_client=mock_tts,
        vobiz_adapter=mock_vobiz,
        audit_service=mock_audit,
        stream_pipeline=mock_stream_pipeline,
    )

    session_id = "sess-barge-in-test"
    response = await service.execute_barge_in_cutoff(session_id)

    # Assertions
    assert response.session_id == session_id
    assert response.new_playback_state == "idle"
    assert response.vobiz_clear_audio_sent is True
    assert response.cutoff_latency_ms < 300  # Sub-300ms SLA
    mock_stream_pipeline.terminate_active_streams.assert_called_once()
    mock_call_repo.update_session_state.assert_called_with(
        session_id=session_id, playback_state="idle"
    )
