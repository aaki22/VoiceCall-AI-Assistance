import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CallSessionCreateDTO(BaseModel):
    """Payload when creating a new telephony session from Vobiz webhook."""

    model_config = ConfigDict(from_attributes=True)

    session_id: str
    call_sid: str
    caller_phone: str
    virtual_did: str
    correlation_id: str
    detected_language: str = "ta"


class CallSessionResponseDTO(BaseModel):
    """DTO representing a serialized call session."""

    model_config = ConfigDict(from_attributes=True)

    session_id: str
    call_sid: str
    caller_phone: str
    virtual_did: str
    status: str
    detected_language: str
    playback_state: str
    turns_count: int
    langsmith_run_id: Optional[str] = None
    correlation_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ConversationTurnDTO(BaseModel):
    """DTO representing a single conversation turn."""

    model_config = ConfigDict(from_attributes=True)

    turn_index: int
    speaker: str
    utterance: str
    detected_language: str
    tool_called: Optional[str] = None
    grounding_metadata: Optional[Dict[str, Any]] = None
    latencies: Optional[Dict[str, Any]] = None
    barge_in_occurred: bool = False
    langsmith_run_id: Optional[str] = None
    created_at: datetime.datetime


class BargeInRequestDTO(BaseModel):
    """Input DTO to trigger barge-in interrupt."""

    session_id: str
    reason: Optional[str] = Field(default="user_voice_energy_detected")


class BargeInResponseDTO(BaseModel):
    """Output DTO when a barge-in cutoff occurs."""

    session_id: str
    cutoff_latency_ms: int
    vobiz_clear_audio_sent: bool
    subprocess_terminated_pid: Optional[int] = None
    new_playback_state: str = "idle"


class AgentTurnRequestDTO(BaseModel):
    """Request DTO for direct/headless agent turn testing."""

    session_id: Optional[str] = None
    utterance: str
    language_override: Optional[str] = None


class AgentTurnResponseDTO(BaseModel):
    """Response DTO for direct/headless agent turn testing."""

    session_id: str
    spoken_response: str
    detected_language: str
    tool_invoked: Optional[str] = None
    grounding_sources: Optional[List[Dict[str, str]]] = None
    telemetry: Dict[str, Any]
