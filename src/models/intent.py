from enum import StrEnum

from pydantic import BaseModel, Field


class AssistantIntent(StrEnum):
    TAMIL_NADU_NEWS = "tamil_nadu_news"
    GENERAL_CHAT = "general_chat"


class TrafficIntent(StrEnum):
    TRAFFIC = "traffic"
    OTHER = "other"


class TrafficIntentOutput(BaseModel):
    intent: TrafficIntent = TrafficIntent.OTHER
    start: str = ""
    end: str = ""


class AssistantIntentOutput(BaseModel):
    intent: AssistantIntent = AssistantIntent.GENERAL_CHAT


class JsonExtractionResult(BaseModel):
    raw_text: str = ""
    json_text: str = Field(default="")
