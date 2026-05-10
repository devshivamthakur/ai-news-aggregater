"""Configuration management with validation and environment-based settings."""

import os
from functools import lru_cache
from typing import Optional
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig(BaseModel):
    """Database configuration."""
    url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ai_news")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    
    class Config:
        """Pydantic config."""
        frozen = True


class SMTPConfig(BaseModel):
    """SMTP email configuration."""
    server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port: int = int(os.getenv("SMTP_PORT", "587"))
    username: str = os.getenv("SMTP_USERNAME", "")
    password: str = os.getenv("SMTP_PASSWORD", "")
    use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    class Config:
        """Pydantic config."""
        frozen = True


class SendGridConfig(BaseModel):
    """SendGrid email configuration."""
    api_key: Optional[str] = os.getenv("SENDGRID_API_KEY", None)
    from_email: Optional[str] = os.getenv("SENDGRID_FROM_EMAIL", None)
    
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


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file: Optional[str] = os.getenv("LOG_FILE", None)
    
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
    smtp: SMTPConfig = SMTPConfig()
    sendgrid: SendGridConfig = SendGridConfig()
    fetcher: FetcherConfig = FetcherConfig()
    scheduler: SchedulerConfig = SchedulerConfig()
    logging: LoggingConfig = LoggingConfig()
    
    # General settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # HTTP API (FastAPI)
    api_key: Optional[str] = os.getenv("API_KEY", None)
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    
    # Aggregation
    aggregation_lookback_hours: int = int(os.getenv("AGGREGATION_LOOKBACK_HOURS", "24"))
    aggregation_rss_per_feed_limit: int = int(os.getenv("AGGREGATION_RSS_PER_FEED_LIMIT", "20"))
    sync_default_sources_on_startup: bool = (
        os.getenv("SYNC_DEFAULT_SOURCES_ON_STARTUP", "false").lower() == "true"
    )
    
    # API keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    
    class Config:
        """Pydantic config."""
        frozen = True
    
    @property
    def database_url(self) -> str:
        """Backward compatibility property."""
        return self.database.url
    
    @property
    def smtp_server(self) -> str:
        """Backward compatibility property."""
        return self.smtp.server
    
    @property
    def smtp_port(self) -> int:
        """Backward compatibility property."""
        return self.smtp.port
    
    @property
    def smtp_username(self) -> str:
        """Backward compatibility property."""
        return self.smtp.username
    
    @property
    def smtp_password(self) -> str:
        """Backward compatibility property."""
        return self.smtp.password
    
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