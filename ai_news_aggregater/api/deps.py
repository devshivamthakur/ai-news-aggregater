"""FastAPI dependencies."""

from collections.abc import Generator

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.storage.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    """When `API_KEY` is set, require it for mutating / operational routes."""
    expected = settings.api_key
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
