import logging
import os
from pathlib import Path
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically calculate the absolute path to the .env file relative to this script
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# Application Constants
APP_NAME = "Theodore Voice AI"
APP_VERSION = "1.0.0"
DEFAULT_TELEPHONY_SAMPLE_RATE = 8000
DEFAULT_AUDIO_CHANNELS = 1
TELEPHONY_FRAME_MS = 20
TELEPHONY_FRAME_BYTES = 320  # 8000Hz * 16-bit / 8 * 0.02s
VAD_SILENCE_THRESHOLD_MS = 600
BARGE_IN_ENERGY_THRESHOLD_MS = 200

# Supported Languages
LANG_TAMIL = "ta"
LANG_ENGLISH = "en"
LANG_TANGLISH = "tanglish"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Pass the explicitly targeted _ENV_FILE path directly to Pydantic
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    # Server Runtime
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    PUBLIC_APP_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/theodore_telephony"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Gemini LLM & Grounding
    GEMINI_API_KEY: str = "dummy_key_for_dev"
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_OUTPUT_TOKENS: int = 400

    # Vobiz.ai Telephony Gateway
    VOBIZ_ACCOUNT_SID: str = "AC_DEV_VOBIZ"
    VOBIZ_AUTH_TOKEN: str = "DEV_AUTH_TOKEN"
    VOBIZ_PHONE_NUMBER: str = "+914440001122"
    VOBIZ_API_BASE_URL: str = "https://vobiz.ai"

    # Inworld AI TTS-2 Flash
    INWORLD_API_KEY: str = "dummy_inworld_key"
    INWORLD_VOICE_ID: str = "Sarah"
    INWORLD_MODEL_ID: str = "inworld-tts-2-flash"
    INWORLD_WS_URL: str = "wss://api.inworld.ai/tts/v1/voice:streamBidirectional"

    # LangSmith Observability
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_ENDPOINT: str = "https://langchain.com"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "theodore-voice-telephony"


@lru_cache
def get_settings() -> Settings:
    """Singleton getter for application settings."""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger("SettingsLogger")
    
    # Confirm the explicit file target location
    logger.info(f"Targeting explicit file layout for environment variables at: {_ENV_FILE}")
    
    settings = Settings()
    return settings
