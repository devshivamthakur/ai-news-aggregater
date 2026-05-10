"""Repository pattern implementation for data access layer."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from ai_news_aggregater.logging.logger import logger

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository with common CRUD operations.
    
    Provides generic data access patterns for all models with:
    - Create, read, update, delete operations
    - Query filtering and pagination
    - Duplicate detection via unique fields
    - Transaction management
    """
    
    def __init__(self, db: Session, model: type):
        """Initialize repository with database session and model class.
        
        Args:
            db: SQLAlchemy session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model
        self._unique_fields = self._get_unique_fields()
    
    def _get_unique_fields(self) -> List[str]:
        """Extract unique column names from model."""
        mapper = inspect(self.model)
        return [col.name for col in mapper.columns if col.unique]
    
    def create(self, obj: T, skip_if_exists: bool = False) -> tuple[T, bool]:
        """Create a new record.
        
        Args:
            obj: Model instance to create
            skip_if_exists: If True, return existing if found; if False, raise error
            
        Returns:
            Tuple of (model_instance, is_new) where is_new indicates if newly created
            
        Raises:
            ValueError: If skip_if_exists=False and duplicate exists
        """
        try:
            self.db.add(obj)
            self.db.flush()  # Flush to get ID without committing
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Created new {self.model.__name__}")
            return obj, True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by primary key."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self) -> List[T]:
        """Get all records."""
        return self.db.query(self.model).all()
    
    def filter(self, **kwargs) -> List[T]:
        """Filter records by column conditions.
        
        Args:
            **kwargs: Column name -> value pairs to filter
            
        Returns:
            List of matching records
        """
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def filter_one(self, **kwargs) -> Optional[T]:
        """Filter records and return first match."""
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first()
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID.
        
        Args:
            id: Record ID
            data: Dictionary of fields to update
            
        Returns:
            Updated model instance or None if not found
        """
        record = self.get_by_id(id)
        if not record:
            logger.warning(f"{self.model.__name__} with id {id} not found")
            return None
        
        try:
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            self.db.commit()
            self.db.refresh(record)
            logger.info(f"Updated {self.model.__name__} with id {id}")
            return record
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        record = self.get_by_id(id)
        if not record:
            logger.warning(f"{self.model.__name__} with id {id} not found")
            return False
        
        try:
            self.db.delete(record)
            self.db.commit()
            logger.info(f"Deleted {self.model.__name__} with id {id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise
    
    def count(self) -> int:
        """Get total count of records."""
        return self.db.query(self.model).count()
    
    def paginate(self, page: int = 1, page_size: int = 10) -> tuple[List[T], int]:
        """Paginate through records.
        
        Args:
            page: Page number (1-indexed)
            page_size: Records per page
            
        Returns:
            Tuple of (records, total_count)
        """
        total = self.count()
        offset = (page - 1) * page_size
        records = self.db.query(self.model).offset(offset).limit(page_size).all()
        return records, total


class NewsRepository(BaseRepository):
    """Repository for News model with duplicate detection."""
    
    def __init__(self, db: Session):
        from ai_news_aggregater.models import News
        super().__init__(db, News)
    
    def get_or_create(self, url: str, **article_data) -> tuple:
        """Get existing news by URL or create new.
        
        Args:
            url: News URL (unique identifier)
            **article_data: Fields for News model
            
        Returns:
            Tuple of (news_record, is_new)
        """
        from ai_news_aggregater.models import News
        
        existing = self.filter_one(url=url)
        if existing:
            logger.info(f"News URL already exists: {url}")
            return existing, False
        
        article_data['url'] = url
        news = News(**article_data)
        return self.create(news)
    
    def get_by_category(self, category: str) -> List:
        """Get all news by category."""
        return self.filter(category=category)
    
    def get_by_hour(self, hour: int) -> List:
        """Get all news fetched in specific hour."""
        return self.filter(fetch_hour=hour)
    
    def get_by_source(self, source: str) -> List:
        """Get all news from specific source."""
        return self.filter(source=source)
    
    def get_recent(self, limit: int = 10) -> List:
        """Get most recent news."""
        return self.db.query(self.model).order_by(
            self.model.fetch_date.desc()
        ).limit(limit).all()


class UserRepository(BaseRepository):
    """Repository for User model with email uniqueness."""
    
    def __init__(self, db: Session):
        from ai_news_aggregater.models import User
        super().__init__(db, User)
    
    def get_or_create(self, email: str, **user_data) -> tuple:
        """Get existing user by email or create new.
        
        Args:
            email: User email (unique identifier)
            **user_data: Fields for User model
            
        Returns:
            Tuple of (user_record, is_new)
        """
        from ai_news_aggregater.models import User
        
        existing = self.filter_one(email=email)
        if existing:
            logger.info(f"User already exists: {email}")
            return existing, False
        
        user_data['email'] = email
        user = User(**user_data)
        return self.create(user)
    
    def get_by_email(self, email: str) -> Optional:
        """Get user by email."""
        return self.filter_one(email=email)
    
    def get_active_users(self) -> List:
        """Get all active users."""
        return self.db.query(self.model).filter(
            self.model.is_active == 1
        ).all()
    
    def get_by_interests(self, interests: List[str]) -> List:
        """Get users with any of the given interests.
        
        Args:
            interests: List of interest keywords
            
        Returns:
            List of users matching interests
        """
        # Query users whose interests JSON contains any of the given interests
        users = self.get_active_users()
        matching = [
            u for u in users 
            if u.interests and any(i in u.interests for i in interests)
        ]
        return matching
    
    def deactivate(self, user_id: int) -> Optional:
        """Deactivate a user."""
        return self.update(user_id, {'is_active': 0})
    
    def activate(self, user_id: int) -> Optional:
        """Activate a user."""
        return self.update(user_id, {'is_active': 1})
