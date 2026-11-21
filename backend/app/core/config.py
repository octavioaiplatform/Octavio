from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="development", alias="OCTAVIO_ENV")
    log_level: str = Field(default="INFO", alias="OCTAVIO_LOG_LEVEL")
    access_token: str = Field(default="local-dev-token", alias="OCTAVIO_ACCESS_TOKEN")
    max_audio_chunk_bytes: int = Field(default=65_536, alias="OCTAVIO_MAX_AUDIO_CHUNK_BYTES", ge=1_024)
    max_sessions: int = Field(default=100, alias="OCTAVIO_MAX_SESSIONS", ge=1)
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_realtime_model: str | None = Field(default=None, alias="OPENAI_REALTIME_MODEL")

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment.lower() == "production" and self.access_token == "local-dev-token":
            raise ValueError("OCTAVIO_ACCESS_TOKEN must be set to a non-development value in production")
        if self.environment.lower() == "production" and (not self.openai_api_key or not self.openai_realtime_model):
            raise ValueError("OPENAI_API_KEY and OPENAI_REALTIME_MODEL must be set in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
