import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint

from ai_news_aggregater.models.Base import Base


class SourceType(str, enum.Enum):
    RSS = "rss"
    YOUTUBE = "youtube"


class IngestionSource(Base):
    """RSS feed URL or YouTube channel id managed in the database."""

    __tablename__ = "ingestion_sources"
    __table_args__ = (UniqueConstraint("source_type", "identifier", name="uq_ingestion_type_identifier"),)

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(20), nullable=False, index=True)
    display_name = Column(String(512), nullable=False)
    identifier = Column(String(2048), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
