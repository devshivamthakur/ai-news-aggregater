"""Enterprise Ingestion Source model with health tracking and metadata."""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class SourceType(enum.StrEnum):
    """Types of content sources."""

    RSS = "rss"
    YOUTUBE = "youtube"
    MEDIUM = "medium"
    TWITTER = "twitter"
    REDDIT = "reddit"
    PODCAST = "podcast"


class SourceStatus(enum.StrEnum):
    """Health status of a source."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    DEPRECATED = "deprecated"


class IngestionSource(Base):
    """Enterprise ingestion source with health tracking and metadata.

    Features:
    - Multiple source types (RSS, YouTube, Medium, Twitter, Reddit, Podcast)
    - Health monitoring (last fetch, error count, status)
    - Rate limiting and backoff support
    - Metadata (description, category, priority)
    - Audit trail
    """

    __tablename__ = "ingestion_sources"
    __table_args__ = (
        UniqueConstraint("source_type", "identifier", name="uq_ingestion_type_identifier"),
        Index("ix_ingestion_sources_status", "status"),
        Index("ix_ingestion_sources_is_active", "is_active"),
    )

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(20), nullable=False, index=True)
    display_name = Column(String(512), nullable=False)
    identifier = Column(String(2048), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    # Status and health
    status = Column(
        Enum(
            SourceStatus,
            values_callable=lambda e: [m.value for m in e],
            native_enum=False,
        ),
        default=SourceStatus.ACTIVE,
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Fetch configuration
    fetch_interval_minutes = Column(Integer, default=60)
    priority = Column(Integer, default=0)  # Higher = more important
    max_items_per_fetch = Column(Integer, default=50)

    # Health tracking
    last_fetched_at = Column(DateTime, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)
    consecutive_errors = Column(Integer, default=0)
    total_fetches = Column(Integer, default=0)
    total_items_fetched = Column(Integer, default=0)

    # Rate limiting
    rate_limit_remaining = Column(Integer, nullable=True)
    rate_limit_reset_at = Column(DateTime, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    news_items = relationship("News", back_populates="ingestion_source")

    def __repr__(self):
        return f"<IngestionSource(id={self.id}, name={self.display_name}, type={self.source_type})>"
