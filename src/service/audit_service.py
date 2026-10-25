from typing import Any, Dict, Optional
from src.repository.audit_repository import AuditRepository
from src.schema.audit import AuditLog
from src.utils.logger import logger


class AuditService:
    """Centralized business service for recording structured system audit logs."""

    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    async def log_telephony_event(
        self,
        correlation_id: str,
        event_type: str,
        details: Dict[str, Any],
        session_id: Optional[str] = None,
        node_name: Optional[str] = None,
    ) -> AuditLog:
        """Records audit event and writes JSON log to stdout."""
        logger.info(
            f"Audit event '{event_type}' for session={session_id}",
            extra={
                "correlation_id": correlation_id,
                "session_id": session_id,
                "event_type": event_type,
                "node_name": node_name,
            },
        )
        return await self.audit_repo.log_event(
            correlation_id=correlation_id,
            event_type=event_type,
            details=details,
            session_id=session_id,
            node_name=node_name,
        )
