from typing import Any, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import datetime

from src.constants.errors import (
    ERR_GUARDRAIL_VIOLATION,
    ERR_INTERNAL_ERROR,
    ERR_NOT_FOUND,
    ERR_SESSION_NOT_FOUND,
    ERR_SUBPROCESS_FAILURE,
    ERR_VALIDATION_ERROR,
    ERR_VOBIZ_GATEWAY_ERROR,
)
from src.utils.logger import logger


class BaseAppException(Exception):
    """Base application exception for domain errors."""

    def __init__(
        self,
        message: str,
        code: str = ERR_INTERNAL_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        field: Optional[str] = None,
        data: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.field = field
        self.data = data


class CallSessionNotFoundException(BaseAppException):
    """Raised when a telephony call session cannot be found."""

    def __init__(self, session_id: str):
        super().__init__(
            message=f"Call session '{session_id}' was not found",
            code=ERR_SESSION_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            field="session_id",
        )


class ResourceNotFoundException(BaseAppException):
    """Generic resource not found exception."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} '{identifier}' not found",
            code=ERR_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            field=resource.lower(),
        )


class VobizGatewayException(BaseAppException):
    """Raised when an interaction with Vobiz carrier gateway fails."""

    def __init__(self, details: str):
        super().__init__(
            message=f"Vobiz Telephony Gateway error: {details}",
            code=ERR_VOBIZ_GATEWAY_ERROR,
            status_code=status.HTTP_502_BAD_GATEWAY,
            field="vobiz_gateway",
        )


class GuardrailViolationException(BaseAppException):
    """Raised when an input or tool call breaches system safety boundaries."""

    def __init__(self, rule_id: str, reason: str):
        super().__init__(
            message=f"Guardrail '{rule_id}' breached: {reason}",
            code=ERR_GUARDRAIL_VIOLATION,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            field="guardrail",
            data={"rule_id": rule_id, "reason": reason},
        )


class SubprocessExecutionException(BaseAppException):
    """Raised when yt-dlp or ffmpeg fails."""

    def __init__(self, command: str, exit_code: int, stderr: str):
        super().__init__(
            message=f"Subprocess '{command}' failed with exit code {exit_code}: {stderr}",
            code=ERR_SUBPROCESS_FAILURE,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            field="subprocess",
        )


def build_error_payload(code: int, message: str, errors: list, request_id: str) -> dict:
    """Build standard JSON envelope for error responses."""
    return {
        "status": "error",
        "code": code,
        "message": message,
        "data": None,
        "errors": errors,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "request_id": request_id,
    }


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Global handler for domain-specific BaseAppException."""
    request_id = getattr(request.state, "request_id", "req-unknown")
    logger.error(
        f"Domain exception occurred: {exc.message} (code: {exc.code})",
        extra={"error_code": exc.code, "request_id": request_id, "path": request.url.path},
    )
    error_item = {"code": exc.code, "message": exc.message}
    if exc.field:
        error_item["field"] = exc.field

    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_payload(exc.status_code, exc.message, [error_item], request_id),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Global handler for Pydantic validation errors."""
    request_id = getattr(request.state, "request_id", "req-unknown")
    errors = []
    for err in exc.errors():
        field_path = ".".join(str(p) for p in err.get("loc", []) if p != "body")
        errors.append(
            {
                "field": field_path or "body",
                "code": ERR_VALIDATION_ERROR,
                "message": err.get("msg", "Invalid value"),
            }
        )

    logger.warning(
        f"Validation error on {request.url.path}: {len(errors)} fields failed",
        extra={"request_id": request_id},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_error_payload(422, "Request Validation Failed", errors, request_id),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for uncaught unexpected exceptions."""
    request_id = getattr(request.state, "request_id", "req-unknown")
    logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}", extra={"request_id": request_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_payload(
            500,
            "Internal Server Error",
            [{"code": ERR_INTERNAL_ERROR, "message": "An unexpected error occurred"}],
            request_id,
        ),
    )
