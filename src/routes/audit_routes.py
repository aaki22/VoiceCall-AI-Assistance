from typing import List, Optional
from fastapi import APIRouter, Depends

from src.dependencies.dependencies import get_audit_repository
from src.models.responses.response_models import ResponseBuilder, StandardResponse
from src.repository.audit_repository import AuditRepository
from src.settings import get_settings

router = APIRouter(prefix="/api/v1/audit", tags=["Observability & Audit"])
settings = get_settings()


@router.get("/logs", response_model=StandardResponse[List[dict]])
async def query_audit_logs(
    correlation_id: Optional[str] = None,
    session_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
    repo: AuditRepository = Depends(get_audit_repository),
):
    """Retrieves structured system audit logs."""
    logs = await repo.query_logs(
        correlation_id=correlation_id,
        session_id=session_id,
        event_type=event_type,
        limit=limit,
    )
    items = [
        {
            "id": str(log.id),
            "correlation_id": log.correlation_id,
            "session_id": log.session_id,
            "event_type": log.event_type,
            "node_name": log.node_name,
            "details": log.details,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
    return ResponseBuilder.success(data=items, message="Audit logs retrieved")


@router.get("/langsmith-trace/{session_id}", response_model=StandardResponse[dict])
async def get_langsmith_trace_info(session_id: str):
    """Returns LangSmith project and trace links for session observability."""
    project = settings.LANGCHAIN_PROJECT
    trace_url = (
        f"https://smith.langchain.com/o/default/projects/p/{project}/r/run-{session_id}"
    )
    return ResponseBuilder.success(
        data={
            "session_id": session_id,
            "project_name": project,
            "tracing_enabled": settings.LANGCHAIN_TRACING_V2 == "true",
            "langsmith_endpoint": settings.LANGCHAIN_ENDPOINT,
            "trace_url": trace_url,
        },
        message="LangSmith trace reference retrieved",
    )
