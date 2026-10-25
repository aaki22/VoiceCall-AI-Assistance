import datetime
import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schema.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.schema.call_session import CallSession


class VoiceReminder(Base, TimestampMixin):
    """SQLAlchemy ORM model representing a scheduled outbound voice reminder."""

    __tablename__ = "voice_reminders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("call_sessions.session_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    recipient_phone: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    reminder_text: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_time_utc: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    preferred_language: Mapped[str] = mapped_column(String(10), default="ta", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True, nullable=False
    )  # pending, completed, cancelled, failed
    outbound_call_sid: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    session: Mapped[Optional["CallSession"]] = relationship("CallSession", back_populates="reminders")
