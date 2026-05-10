"""Business logic layer separating concerns from repository/database layer."""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ai_news_aggregater.storage.repository import NewsRepository, UserRepository
from ai_news_aggregater.models import News, User
from ai_news_aggregater.models.news import NewsType
from ai_news_aggregater.logging.logger import logger


class NewsService:
    """Business logic for news operations."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.repo = NewsRepository(db)
    
    def add_article(
        self,
        url: str,
        title: str,
        content: str,
        summary: str,
        category: str,
        source: str,
        published_at: datetime,
        news_type: NewsType = NewsType.ARTICLE,
        fetch_hour: Optional[int] = None,
        fetch_date: Optional[datetime] = None
    ) -> tuple[News, bool]:
        """Add news article with automatic duplicate detection.
        
        Args:
            url: Article URL (unique identifier)
            title: Article title
            content: Full content
            summary: Brief summary
            category: Content category
            source: Source name
            published_at: When article was published
            news_type: Type of news (article, video, blog_post)
            fetch_hour: Hour when fetched (0-23), defaults to current hour
            fetch_date: When fetched, defaults to now
            
        Returns:
            Tuple of (news_record, is_new)
        """
        return self.repo.get_or_create(
            url=url,
            title=title,
            content=content,
            summary=summary,
            category=category,
            source=source,
            published_at=published_at,
            news_type=news_type,
            fetch_hour=fetch_hour or datetime.utcnow().hour,
            fetch_date=fetch_date or datetime.utcnow()
        )
    
    def get_news_by_category(self, category: str) -> List[News]:
        """Get all news in a category."""
        logger.info(f"Fetching news for category: {category}")
        return self.repo.get_by_category(category)
    
    def get_news_by_hour(self, hour: int) -> List[News]:
        """Get news fetched at specific hour."""
        if not 0 <= hour <= 23:
            raise ValueError("Hour must be between 0 and 23")
        logger.info(f"Fetching news for hour: {hour}")
        return self.repo.get_by_hour(hour)
    
    def get_news_by_source(self, source: str) -> List[News]:
        """Get all news from a source."""
        logger.info(f"Fetching news from source: {source}")
        return self.repo.get_by_source(source)
    
    def get_recent_news(self, limit: int = 10) -> List[News]:
        """Get most recent news articles."""
        if limit <= 0:
            raise ValueError("Limit must be greater than 0")
        logger.info(f"Fetching {limit} recent articles")
        return self.repo.get_recent(limit)
    
    def get_all_news(self) -> List[News]:
        """Get all news articles."""
        return self.repo.get_all()
    
    def search_news(self, query: str) -> List[News]:
        """Search news by title or summary."""
        from sqlalchemy import or_
        results = self.db.query(News).filter(
            or_(
                News.title.ilike(f"%{query}%"),
                News.summary.ilike(f"%{query}%")
            )
        ).all()
        logger.info(f"Found {len(results)} articles matching '{query}'")
        return results


class UserService:
    """Business logic for user operations."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.repo = UserRepository(db)
    
    def register_user(
        self,
        email: str,
        name: str,
        interests: List[str]
    ) -> tuple[User, bool]:
        """Register a new user with automatic duplicate detection.
        
        Args:
            email: User email (must be unique)
            name: User display name
            interests: List of user interests
            
        Returns:
            Tuple of (user_record, is_new)
        """
        if not email or '@' not in email:
            raise ValueError("Invalid email format")
        if not interests or not isinstance(interests, list):
            raise ValueError("Interests must be a non-empty list")
        
        logger.info(f"Registering user: {email}")
        return self.repo.get_or_create(
            email=email,
            name=name,
            interests=interests
        )
    
    def get_user(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.repo.get_by_email(email)
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        logger.info("Fetching active users")
        return self.repo.get_active_users()
    
    def get_users_by_interests(self, interests: List[str]) -> List[User]:
        """Get users interested in any of the given topics.
        
        Args:
            interests: List of interest keywords
            
        Returns:
            List of matching users
        """
        if not interests:
            raise ValueError("Interests list cannot be empty")
        logger.info(f"Finding users interested in: {interests}")
        return self.repo.get_by_interests(interests)
    
    def update_interests(self, email: str, interests: List[str]) -> Optional[User]:
        """Update user interests.
        
        Args:
            email: User email
            interests: New interests list
            
        Returns:
            Updated user or None
        """
        user = self.get_user(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None
        
        return self.repo.update(user.id, {'interests': interests})
    
    def deactivate_user(self, email: str) -> Optional[User]:
        """Deactivate a user."""
        user = self.get_user(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None
        
        logger.info(f"Deactivating user: {email}")
        return self.repo.deactivate(user.id)
    
    def activate_user(self, email: str) -> Optional[User]:
        """Activate a user."""
        user = self.get_user(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None
        
        logger.info(f"Activating user: {email}")
        return self.repo.activate(user.id)


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
    ) -> Optional[Dict]:
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
            'generated_at': datetime.utcnow()
        }
    
    def process_fetched_articles(
        self,
        articles: List[Dict],
        source: str
    ) -> Dict[str, int]:
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
                    published_at=article.get('published_at', datetime.utcnow()),
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
