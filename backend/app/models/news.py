"""Enterprise News model with full-text search, metadata, and audit trail."""

import enum
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


def _utcnow():
    return datetime.now(UTC)


class NewsType(enum.StrEnum):
    """Types of news content."""

    ARTICLE = "article"
    VIDEO = "video"
    BLOG_POST = "blog_post"
    PODCAST = "podcast"
    RESEARCH_PAPER = "research_paper"


class NewsStatus(enum.StrEnum):
    """Processing status for news items."""

    PENDING = "pending"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    FAILED = "failed"
    ARCHIVED = "archived"


class News(Base):
    """Enterprise news model with full metadata and audit trail.

    Features:
    - Full-text search support (title, content, summary)
    - Content analysis metadata (sentiment, keywords, reading time)
    - Source tracking and attribution
    - Processing status tracking
    - User interaction tracking (views, bookmarks, shares)
    - Soft delete support
    """

    __tablename__ = "news"
    __table_args__ = (
        Index("ix_news_url", "url"),
        Index("ix_news_category", "category"),
        Index("ix_news_source", "source"),
        Index("ix_news_published_at", "published_at"),
        Index("ix_news_news_type", "news_type"),
        Index("ix_news_status", "status"),
        Index("ix_news_created_at", "created_at"),
        Index("ix_news_fetch_date", "fetch_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    category = Column(String(100))
    source = Column(String(255))  # e.g., OpenAI blog, Medium
    source_url = Column(String(2048))  # Original source URL
    url = Column(String(2048), unique=True, nullable=False)
    image_url = Column(String(2048), nullable=True)
    author = Column(String(255), nullable=True)

    # Content type and status
    news_type = Column(Enum(NewsType), default=NewsType.ARTICLE, nullable=False)
    status = Column(
        Enum(
            NewsStatus,
            values_callable=lambda e: [m.value for m in e],
            native_enum=False,
        ),
        default=NewsStatus.PENDING,
        nullable=False,
    )

    # Analysis metadata
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    keywords = Column(Text, nullable=True)  # JSON array of keywords
    reading_time_minutes = Column(Integer, nullable=True)
    language = Column(String(10), default="en")

    # Timestamps
    published_at = Column(DateTime, nullable=True)  # When the source published the item
    fetch_hour = Column(Integer)  # Hour (0-23) when the news was fetched
    fetch_date = Column(DateTime)  # Date and time when the news was fetched
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    ingestion_source_id = Column(
        Integer,
        ForeignKey("ingestion_sources.id"),
        nullable=True,
    )
    ingestion_source = relationship("IngestionSource", back_populates="news_items")

    def __repr__(self):
        return f"<News(id={self.id}, title={self.title[:50]}..., source={self.source})>"
