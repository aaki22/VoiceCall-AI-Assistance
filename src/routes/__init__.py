from src.routes.default import router as default_router
from src.routes.call_stream_routes import router as call_stream_router
from src.routes.reminder_routes import router as reminder_router
from src.routes.agent_test_routes import router as agent_test_router
from src.routes.audit_routes import router as audit_router

__all__ = [
    "default_router",
    "call_stream_router",
    "reminder_router",
    "agent_test_router",
    "audit_router",
]
