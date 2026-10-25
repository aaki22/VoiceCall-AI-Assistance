from typing import Any

from pydantic import BaseModel, Field


class PhoneAssistantState(BaseModel):
    session_id: str
    record_url: str = ""
    user_audio_path: str = ""
    user_text: str = ""
    ai_text: str = ""
    ai_audio_file: str = ""
    traffic_start: str = ""
    traffic_end: str = ""
    intent: str = "general_chat"
    should_end_call: bool = False
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
