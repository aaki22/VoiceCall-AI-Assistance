from typing import Optional
from pydantic import BaseModel, ConfigDict


class TokenDTO(BaseModel):
    """Bearer token response DTO."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 86400


class VobizWebhookAuthDTO(BaseModel):
    """Validation DTO for Vobiz carrier webhook signatures."""

    model_config = ConfigDict(from_attributes=True)

    signature: str
    is_valid: bool = True
    account_sid: Optional[str] = None
