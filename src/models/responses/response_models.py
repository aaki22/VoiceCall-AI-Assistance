import datetime
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Detailed error object in errors array."""

    field: Optional[str] = None
    code: str
    message: str


class StandardResponse(BaseModel, Generic[T]):
    """Standardized top-level API response envelope."""

    model_config = ConfigDict(from_attributes=True)

    status: str = Field(example="success")
    code: int = Field(example=200)
    message: str = Field(example="Operation completed successfully")
    data: Optional[T] = None
    errors: List[ErrorDetail] = Field(default_factory=list)
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    request_id: str = Field(example="req-7f3a9b2c-4d1e-4a8f-9c5b-6e2d8f1a3b4c")


class ResponseBuilder:
    """Helper factory for generating standard success responses."""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        code: int = 200,
        request_id: str = "req-generic",
    ) -> StandardResponse[Any]:
        return StandardResponse(
            status="success",
            code=code,
            message=message,
            data=data,
            errors=[],
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            request_id=request_id,
        )
