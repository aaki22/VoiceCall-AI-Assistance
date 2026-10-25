from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VoiceCall AI Assistance"
    environment: str = "local"
    database_url: str = "postgresql://postgres:1234@localhost:5432/Ai_Assistant"

    auth_id: str = ""
    auth_token: SecretStr = SecretStr("")
    public_url: str = "http://localhost:8000"

    gemini_api_key: SecretStr = SecretStr("")
    gemini_model: str = "gemini-2.5-flash"

    ors_api_key: SecretStr = SecretStr("")
    inworld_tts_url: str = "https://api.inworld.ai/tts/v1/voice"
    inworld_tts_auth: SecretStr = SecretStr("")
    inworld_voice_id: str = "Theodore"
    inworld_model_id: str = "inworld-tts-1.5-max"

    thinking_music_url: str = "https://www.soundjay.com/buttons/beep-01a.mp3"
    http_timeout_seconds: float = 20.0
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
