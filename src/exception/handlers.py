import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exception.exceptions import AppException
from src.models.response import ApiResponse, ErrorDTO


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning("Handled application exception path=%s code=%s", request.url.path, exc.code)
        body = ApiResponse[None](
            success=False,
            message=exc.message,
            data=None,
            error=ErrorDTO(code=exc.code, details=exc.details),
        )
        return JSONResponse(status_code=500, content=body.model_dump())
