import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.database.database import engine
from src.exception.exceptions import (
    BaseAppException,
    app_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from src.routes import (
    agent_test_router,
    audit_router,
    call_stream_router,
    default_router,
    reminder_router,
)
from src.schema.base import Base
from src.settings import get_settings
from src.utils.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI application lifespan context manager for startup and shutdown."""
    logger.info("Starting up Theodore Telephony Core...")

    # Initialize PostgreSQL tables if they don't exist
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schemas verified and initialized successfully.")
    except Exception as e:
        logger.warning(f"Database schema auto-creation skipped or failed: {e}")

    yield

    logger.info("Shutting down Theodore Telephony Core...")
    await engine.dispose()
    logger.info("Database connection pool disposed cleanly.")


def create_app() -> FastAPI:
    """Application factory for Theodore Voice Telephony API."""
    app = FastAPI(
        title="Theodore - Telephony AI Assistant",
        version="1.0.0",
        description="Production conversational voice assistant core for Vobiz.ai telephony WebSockets, Gemini Grounding, and Barge-In control.",
        lifespan=lifespan,
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Correlation ID & Request Tracking Middleware
    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Correlation-ID", f"req-{uuid.uuid4().hex[:12]}")
        request.state.request_id = req_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = req_id
        return response

    # 3. Global Exception Handlers
    app.add_exception_handler(BaseAppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # 4. Register Route Modules
    app.include_router(default_router)
    app.include_router(call_stream_router)
    app.include_router(reminder_router)
    app.include_router(agent_test_router)
    app.include_router(audit_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
