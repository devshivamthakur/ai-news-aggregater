"""CRUD operations for storage models."""

from datetime import datetime
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.logging.logger import logger
from app.models import News, NewsStatus, NewsType


class NewsService:
    """CRUD service for News model used by the pipeline."""

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
        """Create a new news record in the database.

        Returns ``None`` (without raising) when the URL already exists — the
        unique ``news_url_key`` constraint is treated as a normal skip, not an
        error.
        """
        try:
            news = News(
                title=title,
                content=content,
                summary=summary,
                category=category,
                source=source,
                url=url,
                published_at=published_at or datetime.utcnow(),
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
        except IntegrityError:
            db.rollback()
            logger.info(f"Skipping duplicate news (url already exists): {url}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create news: {e}")
            return None
