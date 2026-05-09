import os
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ai_news")
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    custom_fetch_hour: int = int(os.getenv("CUSTOM_FETCH_HOUR", "8"))
    
    @field_validator('custom_fetch_hour')
    @classmethod
    def validate_hour(cls, v):
        if not 0 <= v <= 23:
            raise ValueError('Hour must be between 0 and 23')
        return v

settings = Settings()