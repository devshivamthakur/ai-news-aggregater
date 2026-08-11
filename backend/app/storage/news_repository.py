
from sqlalchemy.orm import Session

from app.logging.logger import logger
from app.models import News
from app.storage.base import BaseRepository


class NewsRepository(BaseRepository):
    """Repository for News model with duplicate detection."""

    def __init__(self, db: Session):
        super().__init__(db, News)

    def get_or_create(self, url: str, **article_data) -> tuple:
        """Get existing news by URL or create new.

        Args:
            url: News URL (unique identifier)
            **article_data: Fields for News model

        Returns:
            Tuple of (news_record, is_new)
        """

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

    def get_by_hour(self, hour: int) -> list:
        """Get all news fetched in specific hour."""
        return self.filter(fetch_hour=hour)

    def get_by_source(self, source: str) -> list:
        """Get all news by source."""
        return self.filter(source=source)

    def get_recent(self, limit: int = 10) -> list:
        """Get most recent news."""
        return self.db.query(self.model).order_by(self.model.created_at.desc()).limit(limit).all()
