"""News service for managing news articles in the database."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.logging.logger import logger
from app.models import News, NewsStatus, NewsType
from app.storage.base import BaseRepository


class NewsRepository(BaseRepository):
    """Repository for News model with duplicate detection."""

    def __init__(self, db: Session):
        super().__init__(db, News)

    def get_or_create(self, url: str, **article_data) -> tuple:
        """Get existing news by URL or create new."""
        existing = self.filter_one(url=url)
        if existing:
            logger.info(f"News URL already exists: {url}")
            return existing, False

        article_data['url'] = url
        news = News(**article_data)
        return self.create(news)

    def get_by_category(self, category: str) -> list:
        """Get all news by category."""
        return self.filter(category=category)

    def get_by_source(self, source: str) -> list:
        """Get all news by source."""
        return self.filter(source=source)

    def get_recent(self, limit: int = 10) -> list:
        """Get most recent news."""
        return self.db.query(self.model).order_by(self.model.created_at.desc()).limit(limit).all()

    def get_all(self) -> list:
        """Get all news."""
        return self.db.query(self.model).all()


class NewsService:
    """Service layer for News operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = NewsRepository(db)

    def get_recent_news(self, limit: int = 10) -> list[News]:
        """Get most recent news articles."""
        return self.repo.get_recent(limit)

    def get_all_news(self) -> list[News]:
        """Get all news articles."""
        return self.db.query(News).all()

    def get_by_category(self, category: str) -> list[News]:
        """Get all news articles in a category."""
        return self.repo.get_by_category(category)

    def get_by_categories(self, categories: list[str], limit: int = 50) -> list[News]:
        """Get recent news articles matching any of the given categories."""
        return self.repo.get_by_categories(categories, limit)

    def add_article(
        self,
        *,
        url: str,
        title: str,
        content: str = "",
        summary: str = "",
        category: str = "Uncategorized",
        source: str = "",
        published_at: datetime | None = None,
        news_type: NewsType = NewsType.ARTICLE,
        **kwargs: Any,
    ) -> tuple[News, bool]:
        """Add a news article, handling duplicates by URL."""
        return self.repo.get_or_create(
            url=url,
            title=title,
            content=content,
            summary=summary,
            category=category,
            source=source,
            published_at=published_at or datetime.now(UTC),
            news_type=news_type,
            status=NewsStatus.PENDING,
            **kwargs,
        )

    @staticmethod
    def create_news(
        db: Session,
        *,
        title: str,
        content: str,
        summary: str,
        category: str,
        source: str,
        url: str,
        published_at: datetime | None = None,
        news_type: NewsType = NewsType.ARTICLE,
        fetch_hour: int | None = None,
        fetch_date: datetime | None = None,
        **kwargs: Any,
    ) -> News | None:
        """Create a new news record in the database."""
        try:
            news = News(
                title=title,
                content=content,
                summary=summary,
                category=category,
                source=source,
                url=url,
                published_at=published_at or datetime.now(UTC),
                news_type=news_type,
                status=NewsStatus.PENDING,
                fetch_hour=fetch_hour,
                fetch_date=fetch_date,
                **kwargs,
            )
            db.add(news)
            db.commit()
            db.refresh(news)
            logger.info(f"Created news: {title[:50]}...")
            return news
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create news: {e}")
            return None
