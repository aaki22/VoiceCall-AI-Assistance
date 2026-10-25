import datetime
import uuid
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.schema.base import Base


class AuditLog(Base):
    """SQLAlchemy ORM model for centralized audit records and tracing logs."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    correlation_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    node_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        index=True,
        nullable=False,
    )
