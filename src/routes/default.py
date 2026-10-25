import datetime
from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.models.responses.response_models import ResponseBuilder, StandardResponse
from src.settings import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/healthCheck", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe returning 200 OK if server process is running."""
    return ResponseBuilder.success(
        data={"checks": {"server": "ok"}, "app_env": settings.APP_ENV},
        message="Theodore voice telephony service is healthy",
        request_id="req-healthcheck",
    )


@router.get("/ready", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe validating database connectivity and required credentials."""
    checks = {}

    # Check Database Connectivity
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    checks["gemini_api"] = "configured" if settings.GEMINI_API_KEY else "missing"
    checks["vobiz_gateway"] = "configured" if settings.VOBIZ_ACCOUNT_SID else "missing"
    checks["inworld_tts"] = "configured" if settings.INWORLD_API_KEY else "missing"

    is_ready = checks.get("database") == "connected"
    return ResponseBuilder.success(
        data={"dependencies": checks, "ready": is_ready},
        message="All dependencies operational" if is_ready else "Some dependencies degraded",
        request_id="req-readiness",
    )


@router.get("/docs", response_class=HTMLResponse)
async def api_documentation():
    """Serves OpenAPI documentation."""
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Theodore Voice Telephony API Documentation</title>
        <meta charset="utf-8"/>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
          window.onload = () => {
            window.ui = SwaggerUIBundle({
              url: '/public/openapi.yaml',
              dom_id: '#swagger-ui',
            });
          };
        </script>
      </body>
    </html>
    """
