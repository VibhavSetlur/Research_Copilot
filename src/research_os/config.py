"""Central Pydantic settings — read from env and from .env."""

from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-derived configuration for Research OS internals.

    Researcher-facing config lives in ``inputs/researcher_config.yaml``; this
    class only handles credentials and runtime knobs picked up from env vars.
    """

    # LLM provider keys (not used by Research OS itself, but exposed for tools
    # that integrate with these SDKs).
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Literature & search APIs
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    S2_API_KEY: Optional[str] = None  # alias frequently used by other SDKs
    CROSSREF_API_KEY: Optional[str] = None
    NCBI_API_KEY: Optional[str] = None
    FIRECRAWL_API_KEY: Optional[str] = None
    FIRECRAWL: Optional[str] = None  # alias
    SERPAPI_API_KEY: Optional[str] = None
    SERPAPI: Optional[str] = None  # alias

    # Optional storage
    DATABASE_URL: Optional[str] = None

    # Runtime knobs
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
