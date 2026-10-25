import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ReminderCreateDTO(BaseModel):
    """Payload to schedule a voice reminder."""

    model_config = ConfigDict(from_attributes=True)

    recipient_phone: str = Field(description="Recipient phone in E.164 format, e.g. +919840012345")
    reminder_text: str = Field(description="Spoken text to deliver over phone call")
    scheduled_time_utc: datetime.datetime = Field(description="UTC timestamp for reminder dispatch")
    preferred_language: str = Field(default="ta", description="Voice language: ta or en")
    session_id: Optional[str] = Field(default=None, description="Optional calling session ID")


class ReminderUpdateDTO(BaseModel):
    """Payload to update or cancel a scheduled voice reminder."""

    model_config = ConfigDict(from_attributes=True)

    reminder_text: Optional[str] = None
    scheduled_time_utc: Optional[datetime.datetime] = None
    status: Optional[str] = Field(default=None, description="pending, completed, cancelled, or failed")


class ReminderResponseDTO(BaseModel):
    """DTO representing a voice reminder record."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: Optional[str] = None
    recipient_phone: str
    reminder_text: str
    scheduled_time_utc: datetime.datetime
    preferred_language: str
    status: str
    outbound_call_sid: Optional[str] = None
    retry_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
