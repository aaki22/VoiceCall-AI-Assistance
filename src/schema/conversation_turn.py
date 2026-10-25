import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schema.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.schema.call_session import CallSession


class ConversationTurn(Base, TimestampMixin):
    """SQLAlchemy ORM model representing a single conversational turn."""

    __tablename__ = "conversation_turns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("call_sessions.session_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    utterance: Mapped[str] = mapped_column(Text, nullable=False)
    detected_language: Mapped[str] = mapped_column(String(10), nullable=False)
    tool_called: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Native PostgreSQL JSONB for grounding chunks, source citations, and latencies
    grounding_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    latencies: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    barge_in_occurred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    langsmith_run_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    session: Mapped["CallSession"] = relationship("CallSession", back_populates="turns")
