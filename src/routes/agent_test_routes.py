import uuid
from fastapi import APIRouter, Depends, status

from src.agents.call_orchestrator_graph import CallOrchestratorGraph
from src.client.gemini_client import GeminiClient
from src.client.ytdlp_client import YtDlpClient
from src.dependencies.dependencies import (
    get_call_orchestrator_graph,
    get_gemini_client,
)
from src.models.dtos.call_models import (
    AgentTurnRequestDTO,
    AgentTurnResponseDTO,
)
from src.models.responses.response_models import ResponseBuilder, StandardResponse
from src.tools.search_tool import SearchTool
from src.tools.transit_tool import TransitTool

router = APIRouter(prefix="/api/v1/agent", tags=["Agent & Tool Testing"])


@router.post("/turn", response_model=StandardResponse[AgentTurnResponseDTO], status_code=status.HTTP_200_OK)
async def execute_agent_turn(
    request: AgentTurnRequestDTO,
    orchestrator: CallOrchestratorGraph = Depends(get_call_orchestrator_graph),
):
    """Executes a single conversational agent turn without WebSockets.

    Ideal for integration tests, curl probes, and CI evaluation.
    """
    session_id = request.session_id or f"sess-test-{uuid.uuid4().hex[:8]}"
    correlation_id = f"corr-{uuid.uuid4().hex[:8]}"
    langsmith_run_id = f"run-test-{uuid.uuid4().hex[:8]}"

    state = await orchestrator.process_turn(
        session_id=session_id,
        caller_phone="+919840012345",
        utterance=request.utterance,
        correlation_id=correlation_id,
        langsmith_run_id=langsmith_run_id,
    )

    response_dto = AgentTurnResponseDTO(
        session_id=session_id,
        spoken_response=state.get("spoken_response", ""),
        detected_language=state.get("detected_language", "ta"),
        tool_invoked=state.get("intent"),
        grounding_sources=state.get("grounding_sources", []),
        telemetry={
            "latencies": state.get("latencies", {}),
            "correlation_id": correlation_id,
            "langsmith_run_id": langsmith_run_id,
        },
    )
    return ResponseBuilder.success(data=response_dto, message="Agent turn processed successfully")


@router.post("/tools/transit", response_model=StandardResponse[dict])
async def test_transit_guardrail(
    query: str,
    gemini: GeminiClient = Depends(get_gemini_client),
):
    """Directly evaluates queries against the CRIT-TRANSIT-01 capability boundary guardrail."""
    tool = TransitTool(gemini)
    res = await tool.execute(query, language="ta")
    return ResponseBuilder.success(data=res, message="Transit tool executed")


@router.post("/tools/youtube-stream", response_model=StandardResponse[dict])
async def test_youtube_audio_pipeline(
    query: str,
):
    """Tests YouTube audio stream extraction without disk accumulation."""
    client = YtDlpClient()
    url = await client.get_audio_stream_url(query)
    return ResponseBuilder.success(
        data={"query": query, "stream_url_resolved": url is not None, "stream_url": url},
        message="YouTube audio extraction evaluated",
    )


@router.post("/tools/search", response_model=StandardResponse[dict])
async def test_search_tool(
    query: str,
    gemini: GeminiClient = Depends(get_gemini_client),
):
    """Directly tests live e-commerce search grounding."""
    tool = SearchTool(gemini)
    res = await tool.execute(query, language="en")
    return ResponseBuilder.success(data=res, message="Search tool executed")
