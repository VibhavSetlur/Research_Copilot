from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Central configuration for Research OS."""

    # LLM Provider Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Research Tool API Keys
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    CROSSREF_API_KEY: Optional[str] = None
    NCBI_API_KEY: Optional[str] = None

    # Optional DB / Redis
    DATABASE_URL: Optional[str] = None

    # Environment config
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
