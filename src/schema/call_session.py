import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schema.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.schema.conversation_turn import ConversationTurn
    from src.schema.reminder import VoiceReminder


class CallSession(Base, TimestampMixin):
    """SQLAlchemy ORM model representing a phone call session."""

    __tablename__ = "call_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    call_sid: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    caller_phone: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    virtual_did: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ringing", nullable=False)
    detected_language: Mapped[str] = mapped_column(String(10), default="ta", nullable=False)
    playback_state: Mapped[str] = mapped_column(String(20), default="idle", nullable=False)
    turns_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    langsmith_run_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    # Relationships with selectin loading for async safety
    turns: Mapped[List["ConversationTurn"]] = relationship(
        "ConversationTurn",
        back_populates="session",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    reminders: Mapped[List["VoiceReminder"]] = relationship(
        "VoiceReminder",
        back_populates="session",
        lazy="selectin",
    )
