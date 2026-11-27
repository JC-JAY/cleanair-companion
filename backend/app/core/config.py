"""Application settings — loaded from environment variables via Pydantic Settings."""
from __future__ import annotations

import secrets
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "CleanAir Companion"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:4200", "https://cleanair-companion.vercel.app"]

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://cleanair:cleanair@localhost:5432/cleanair"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "none"
    AQI_CACHE_TTL_SECONDS: int = 300          # 5 minutes
    PLAN_CACHE_TTL_SECONDS: int = 86400       # 24 hours

    # ── AI (Google Gemini & multi-provider) ──────────────────────────────────
    GEMINI_API_KEY: SecretStr = Field(default=SecretStr(""), description="Google Gemini API key")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    ANTHROPIC_API_KEY: SecretStr = Field(default=SecretStr(""), description="Anthropic Claude API key")
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5"
    OPENAI_API_KEY: SecretStr = Field(default=SecretStr(""), description="OpenAI key for embeddings")
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    RAG_TOP_K: int = 8
    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.3

    # ── Auth ──────────────────────────────────────────────────────────────────
    SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="JWT signing secret — securely generated if not set via environment",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24       # 24 h
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── External APIs ─────────────────────────────────────────────────────────
    OPENAQ_API_KEY: str = ""
    OPENAQ_BASE_URL: AnyHttpUrl = "https://api.openaq.org/v3"  # type: ignore[assignment]
    OPEN_METEO_BASE_URL: AnyHttpUrl = "https://api.open-meteo.com/v1"  # type: ignore[assignment]
    CPCB_API_KEY: str = ""

    # ── Notifications ─────────────────────────────────────────────────────────
    WHATSAPP_BUSINESS_TOKEN: SecretStr = Field(default=SecretStr(""), description="Meta WA token")
    WHATSAPP_PHONE_ID: str = ""
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_EMAIL: str = "admin@cleanair.local"

    # ── Privacy ───────────────────────────────────────────────────────────────
    LOCATION_PRECISION_DP: int = 2   # Round lat/lon to 2 decimal places (~1 km)

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    AQI_FETCH_INTERVAL_SECONDS: int = 300

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not (v.startswith("postgresql+asyncpg://") or v.startswith("sqlite+aiosqlite://")):
            raise ValueError("DATABASE_URL must use postgresql+asyncpg or sqlite+aiosqlite driver")
        return v


settings = Settings()  # type: ignore[call-arg]

