from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.logging.logger import logger
from app.models import NewsType

from app.services.news_service import NewsService
from app.services.user_service import UserService


class AggregationService:
    """Orchestrate news fetching, processing, and delivery."""

    def __init__(self, db: Session):
        """Initialize service with dependencies."""
        self.db = db
        self.news_service = NewsService(db)
        self.user_service = UserService(db)

    def get_personalized_digest(
        self,
        email: str,
        limit: int = 10
    ) -> dict | None:
        """Get personalized news digest for a user.

        Args:
            email: User email
            limit: Max articles to include

        Returns:
            Dictionary with user info and filtered news, or None if user not found
        """
        user = self.user_service.get_user(email)
        if not user:
            logger.warning(f"User not found for digest: {email}")
            return None

        if not user.interests:
            logger.warning(f"User has no interests: {email}")
            articles = self.news_service.get_recent_news(limit)
        else:
            # Get all news and filter by user interests
            all_news = self.news_service.get_all_news()
            articles = [
                n for n in all_news
                if any(interest.lower() in n.category.lower() for interest in user.interests)
            ][:limit]

        return {
            'user': {
                'name': user.name,
                'email': user.email,
                'interests': user.interests
            },
            'articles': articles,
            'article_count': len(articles),
            'generated_at': datetime.now(UTC)
        }

    def process_fetched_articles(
        self,
        articles: list[dict],
        source: str
    ) -> dict[str, int]:
        """Process fetched articles, handling duplicates.

        Args:
            articles: List of article dictionaries from fetcher
            source: Source name

        Returns:
            Dictionary with counts: {'created': int, 'skipped': int, 'errors': int}
        """
        stats = {'created': 0, 'skipped': 0, 'errors': 0}

        for article in articles:
            try:
                _, is_new = self.news_service.add_article(
                    url=article['url'],
                    title=article['title'],
                    content=article.get('content', ''),
                    summary=article.get('summary', ''),
                    category=article.get('category', 'Uncategorized'),
                    source=source,
                    published_at=article.get('published_at', datetime.now(UTC)),
                    news_type=article.get('news_type', NewsType.ARTICLE)
                )

                if is_new:
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            except Exception as e:
                logger.error(f"Error processing article from {source}: {e}")
                stats['errors'] += 1

        logger.info(f"Processing complete for {source}: {stats}")
        return stats
