import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.config.settings import settings
from app.logging.logger import logger

engine = create_engine(
    settings.database_url,
    echo=False,
    poolclass=QueuePool,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle,
    pool_pre_ping=True,  # Verify connections before using them
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def mask_db_url(url: str) -> str:
    """Mask the password in a database connection URL for safe logging."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.password:
            netloc = parsed.hostname or ""
            if parsed.username:
                if parsed.port:
                    netloc = f"{parsed.username}:*****@{parsed.hostname}:{parsed.port}"
                else:
                    netloc = f"{parsed.username}:*****@{parsed.hostname}"
            else:
                if parsed.port:
                    netloc = f"*****@{parsed.hostname}:{parsed.port}"
                else:
                    netloc = f"*****@{parsed.hostname}"
            return parsed._replace(netloc=netloc).geturl()
        return url
    except Exception:
        return "hidden-url"


def create_tables():
    from app.models import Base
    masked_url = mask_db_url(settings.database_url)
    logger.info("Initializing database and creating tables at: %s", masked_url)
    if (
        ("localhost" in settings.database_url or "127.0.0.1" in settings.database_url)
        and (os.getenv("RENDER") or settings.environment == "production")
    ):
        logger.warning(
            "WARNING: Connecting to a LOCALHOST database while running in a "
            "PRODUCTION/RENDER environment! Please check that the DATABASE_URL "
            "environment variable is set correctly in your Render dashboard."
        )
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")
