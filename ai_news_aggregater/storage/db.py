from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.logging.logger import logger

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    from ai_news_aggregater.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")