"""Abstract base fetcher for consistent news fetching patterns."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from ai_news_aggregater.utils.errors import retry_on_failure
from ai_news_aggregater.logging.logger import logger


class BaseFetcher(ABC):
    """Abstract base class for all news fetchers.
    
    Provides common patterns:
    - Retry mechanism for failed requests
    - Logging and error handling
    - Data validation with Pydantic
    - Timeout management
    """
    
    def __init__(self, timeout: int = 15, max_retries: int = 3):
        """Initialize fetcher with configuration.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.fetcher_name = self.__class__.__name__
    
    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch news from source.
        
        Returns:
            List of article dictionaries with keys: url, title, content, 
            summary, category, published_at, source, news_type
            
        Raises:
            Exception: If fetching fails after retries
        """
        pass
    
    @abstractmethod
    def validate_data(self, item: Dict) -> bool:
        """Validate fetched item before processing.
        
        Args:
            item: Item dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def log_fetch_summary(self, count: int, duration: float, errors: int = 0):
        """Log standardized fetch summary.
        
        Args:
            count: Number of items fetched
            duration: Fetch duration in seconds
            errors: Number of errors encountered
        """
        logger.info(
            f"{self.fetcher_name}: Fetched {count} items in {duration:.2f}s "
            f"({errors} errors)" if errors else 
            f"{self.fetcher_name}: Fetched {count} items in {duration:.2f}s"
        )
    
    def sanitize_text(self, text: Optional[str], max_length: int = 5000) -> str:
        """Sanitize and truncate text.
        
        Args:
            text: Text to sanitize
            max_length: Maximum length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Truncate if necessary
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + "..."
        
        return text.strip()
    
    def ensure_published_date(self, date: Optional[datetime]) -> datetime:
        """Ensure we have a valid published date.
        
        Args:
            date: Date to validate
            
        Returns:
            Provided date or current UTC time
        """
        if isinstance(date, datetime):
            return date
        return datetime.utcnow()


class FetcherRegistry:
    """Registry for managing fetchers."""
    
    _fetchers: Dict[str, BaseFetcher] = {}
    
    @classmethod
    def register(cls, name: str, fetcher: BaseFetcher):
        """Register a fetcher.
        
        Args:
            name: Unique fetcher name
            fetcher: Fetcher instance
        """
        cls._fetchers[name] = fetcher
        logger.info(f"Registered fetcher: {name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[BaseFetcher]:
        """Get a registered fetcher.
        
        Args:
            name: Fetcher name
            
        Returns:
            Fetcher instance or None
        """
        return cls._fetchers.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, BaseFetcher]:
        """Get all registered fetchers."""
        return cls._fetchers.copy()
    
    @classmethod
    def unregister(cls, name: str):
        """Unregister a fetcher.
        
        Args:
            name: Fetcher name
        """
        if name in cls._fetchers:
            del cls._fetchers[name]
            logger.info(f"Unregistered fetcher: {name}")
