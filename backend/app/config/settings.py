"""Configuration management with validation and environment-based settings."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

load_dotenv()


class DatabaseConfig(BaseModel):
    """Database configuration."""
    url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ai_news")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))

    @field_validator('url')
    @classmethod
    def validate_and_fix_url(cls, v: str) -> str:
        """Fix postgres:// to postgresql:// for SQLAlchemy compatibility."""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    class Config:
        """Pydantic config."""
        frozen = True


class BrevoConfig(BaseModel):
    """Brevo (formerly Sendinblue) transactional email configuration."""
    api_key: str | None = os.getenv("BREVO_API_KEY", None)
    # Verified sender address used in the `sender` field of each email.
    sender_email: str = os.getenv("BREVO_SENDER_EMAIL", "")
    sender_name: str = os.getenv("BREVO_SENDER_NAME", "AIPulse")
    # When True, the Brevo API is used for delivery.
    enabled: bool = os.getenv("BREVO_ENABLED", "false").lower() == "true"

    class Config:
        """Pydantic config."""
        frozen = True


class FetcherConfig(BaseModel):
    """News fetcher configuration."""
    timeout: int = int(os.getenv("FETCHER_TIMEOUT", "15"))
    max_retries: int = int(os.getenv("FETCHER_MAX_RETRIES", "3"))
    retry_delay: float = float(os.getenv("FETCHER_RETRY_DELAY", "2.0"))
    content_max_length: int = int(os.getenv("FETCHER_CONTENT_MAX_LENGTH", "5000"))

    class Config:
        """Pydantic config."""
        frozen = True


class SchedulerConfig(BaseModel):
    """APScheduler configuration."""
    fetch_hour: int = int(os.getenv("CUSTOM_FETCH_HOUR", "8"))
    enabled: bool = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
    timezone: str = os.getenv("SCHEDULER_TIMEZONE", "UTC")

    @field_validator('fetch_hour')
    @classmethod
    def validate_fetch_hour(cls, v):
        """Validate fetch hour is 0-23."""
        if not 0 <= v <= 23:
            raise ValueError('Fetch hour must be between 0 and 23')
        return v

    class Config:
        """Pydantic config."""
        frozen = True


class JWTConfig(BaseModel):
    """JWT settings for user sessions."""

    secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-insecure-change-me")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    class Config:
        """Pydantic config."""

        frozen = True

class RateLimitConfig(BaseModel):
    """Rate limiting configuration (slowapi / limits)."""

    enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    # Default per-route limit applied to every endpoint via SlowAPIMiddleware.
    # Format: "<number>/<period>" where period is one of second, minute, hour, day, month, year.
    default_limit: str = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")
    # Stricter limit applied to authentication endpoints (login/register/refresh).
    auth_limit: str = os.getenv("RATE_LIMIT_AUTH", "10/minute")
    # Stricter limit applied to admin mutation endpoints.
    admin_limit: str = os.getenv("RATE_LIMIT_ADMIN", "30/minute")
    # Storage URI for the limits backend. "memory://" keeps state in-process;
    # use a redis:// URI in production for shared state across workers.
    storage_uri: str = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")
    # Strategy for choosing which limit applies when several match.
    strategy: str = os.getenv("RATE_LIMIT_STRATEGY", "moving-window")

    @field_validator('strategy')
    @classmethod
    def validate_strategy(cls, v: str) -> str:
        """Validate the limits strategy."""
        valid = {'fixed-window', 'fixed-window-elastic-expiry', 'moving-window'}
        if v not in valid:
            raise ValueError(f'Rate limit strategy must be one of {valid}')
        return v

    class Config:
        """Pydantic config."""
        frozen = True

class RedisConfig(BaseModel):
    """Redis cache configuration."""

    url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    password: str | None = os.getenv("REDIS_PASSWORD", None)
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = int(os.getenv("REDIS_DB", "0"))
    ttl: int = int(os.getenv("REDIS_TTL", "300"))  # Default 5 minutes
    enabled: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"

    class Config:
        """Pydantic config."""
        frozen = True

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file: str | None = os.getenv("LOG_FILE", None)

    @field_validator('level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()

    class Config:
        """Pydantic config."""
        frozen = True


class Settings(BaseModel):
    """Main settings combining all configuration sections."""

    # Component configs
    database: DatabaseConfig = DatabaseConfig()
    brevo: BrevoConfig = BrevoConfig()
    fetcher: FetcherConfig = FetcherConfig()
    scheduler: SchedulerConfig = SchedulerConfig()
    logging: LoggingConfig = LoggingConfig()
    jwt: JWTConfig = JWTConfig()
    redis: RedisConfig = RedisConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()

    # General settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # HTTP API (FastAPI)
    api_key: str | None = os.getenv("API_KEY", None)
    admin_email: str = os.getenv("ADMIN_EMAIL", "shivamadmin@mailinator.com")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    cors_origins: tuple[str, ...] = tuple(
        dict.fromkeys(
            o.strip()
            for o in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,https://devshivamthakur.github.io",
            ).split(",")
            if o.strip()
        )
    )

    # Aggregation
    aggregation_lookback_hours: int = int(os.getenv("AGGREGATION_LOOKBACK_HOURS", "24"))
    aggregation_rss_per_feed_limit: int = int(os.getenv("AGGREGATION_RSS_PER_FEED_LIMIT", "20"))
    sync_default_sources_on_startup: bool = (
        os.getenv("SYNC_DEFAULT_SOURCES_ON_STARTUP", "false").lower() == "true"
    )
    # Max parallel LLM calls when analyzing a batch of fetched items.
    content_analyzer_max_concurrency: int = int(
        os.getenv("CONTENT_ANALYZER_MAX_CONCURRENCY", "5")
    )

    # Digest delivery scaling (for large subscriber bases, e.g. 100k+ users).
    # Max parallel Brevo API calls opened at once.
    digest_max_concurrency: int = int(os.getenv("DIGEST_MAX_CONCURRENCY", "10"))
    # Users sent per Brevo API call (one call is reused for the chunk).
    digest_batch_size: int = int(os.getenv("DIGEST_BATCH_SIZE", "200"))
    # Subscribers fetched from the DB per page (keyset pagination).
    digest_user_page_size: int = int(os.getenv("DIGEST_USER_PAGE_SIZE", "1000"))

    # API keys
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY", None)
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY", None)

    class Config:
        """Pydantic config."""
        frozen = True

    @property
    def database_url(self) -> str:
        """Backward compatibility property."""
        return self.database.url

    @property
    def custom_fetch_hour(self) -> int:
        """Backward compatibility property."""
        return self.scheduler.fetch_hour

    @property
    def log_level(self) -> str:
        """Backward compatibility property."""
        return self.logging.level


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern).

    Returns:
        Settings instance
    """
    return Settings()


# Create global settings instance
settings = get_settings()
