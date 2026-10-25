from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.session import Base


class CallSession(Base):
    __tablename__ = "call_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_turns: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    turns: Mapped[list["CallTurn"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class CallTurn(Base):
    __tablename__ = "call_turns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("call_sessions.session_id"),
        index=True,
        nullable=False,
    )
    user_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_audio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_audio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    session: Mapped[CallSession] = relationship(back_populates="turns")
