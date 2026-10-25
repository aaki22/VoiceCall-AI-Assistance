from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schema.audit import AuditLog


class AuditRepository:
    """Data access repository for AuditLog entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_event(
        self,
        correlation_id: str,
        event_type: str,
        details: Dict[str, Any],
        session_id: Optional[str] = None,
        node_name: Optional[str] = None,
    ) -> AuditLog:
        """Records an audit log entry in PostgreSQL."""
        audit_entry = AuditLog(
            correlation_id=correlation_id,
            session_id=session_id,
            event_type=event_type,
            node_name=node_name,
            details=details,
        )
        self.session.add(audit_entry)
        await self.session.commit()
        await self.session.refresh(audit_entry)
        return audit_entry

    async def query_logs(
        self,
        correlation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[AuditLog]:
        """Queries audit entries with optional filters."""
        stmt = select(AuditLog)

        if correlation_id:
            stmt = stmt.where(AuditLog.correlation_id == correlation_id)
        if session_id:
            stmt = stmt.where(AuditLog.session_id == session_id)
        if event_type:
            stmt = stmt.where(AuditLog.event_type == event_type)

        stmt = stmt.order_by(desc(AuditLog.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
