from functools import lru_cache
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "OakstrattonIMA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = ""
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS — accepts JSON array, comma-separated string, or empty
    CORS_ORIGINS: str = ""

    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@oakstrattonima.com"
    EMAIL_FROM_NAME: str = "OakstrattonIMA"

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_CONNECT_CLIENT_ID: Optional[str] = None

    # Social Media APIs
    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None

    # File Storage (S3-compatible)
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # AI — provider selection
    AI_PROVIDER: str = "claude"          # claude | gemini | openai
    AI_MAX_TOKENS: int = 4096

    # Anthropic / Claude
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL: str = "claude-sonnet-4-6"  # default Claude model

    # Google / Gemini
    GEMINI_API_KEY: Optional[str] = None

    # OpenAI / GPT (optional — install `openai` package separately)
    OPENAI_API_KEY: Optional[str] = None

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:5173"

    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    # Admin seeding — set this to protect the /auth/seed-admin endpoint
    # Leave blank to disable the endpoint entirely after first use
    SEED_ADMIN_SECRET: Optional[str] = None

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS from JSON array or comma-separated string."""
        import json
        val = self.CORS_ORIGINS.strip()
        if not val:
            # Fall back to FRONTEND_URL so credentials work (wildcard + credentials is invalid)
            if self.FRONTEND_URL and self.FRONTEND_URL != "http://localhost:5173":
                return [self.FRONTEND_URL.rstrip("/")]
            return ["*"]
        if val.startswith("["):
            try:
                return json.loads(val)
            except Exception:
                pass
        return [o.strip().rstrip("/") for o in val.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

