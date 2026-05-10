"""Dependency injection container for managing service instances."""

from typing import Dict, Any, Callable
from sqlalchemy.orm import Session
from ai_news_aggregater.logging.logger import logger


class Container:
    """Simple dependency injection container.
    
    Manages singleton and factory instances of services and dependencies.
    Supports lazy initialization and lifecycle management.
    """
    
    def __init__(self):
        """Initialize container."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._initialized = False
    
    def register_singleton(self, name: str, instance: Any):
        """Register a singleton instance.
        
        Args:
            name: Unique service name
            instance: Service instance
        """
        self._singletons[name] = instance
        logger.debug(f"Registered singleton: {name}")
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory function.
        
        Creates a new instance each time get() is called.
        
        Args:
            name: Unique service name
            factory: Callable that returns service instance
        """
        self._factories[name] = factory
        logger.debug(f"Registered factory: {name}")
    
    def get(self, name: str, *args, **kwargs) -> Any:
        """Get service instance.
        
        Args:
            name: Service name
            *args: Positional arguments for factory
            **kwargs: Keyword arguments for factory
            
        Returns:
            Service instance (singleton or new from factory)
            
        Raises:
            ValueError: If service not found
        """
        if name in self._singletons:
            return self._singletons[name]
        
        if name in self._factories:
            return self._factories[name](*args, **kwargs)
        
        raise ValueError(f"Service '{name}' not found in container")
    
    def has(self, name: str) -> bool:
        """Check if service exists.
        
        Args:
            name: Service name
            
        Returns:
            True if service registered, False otherwise
        """
        return name in self._singletons or name in self._factories
    
    def clear(self):
        """Clear all registered services."""
        self._singletons.clear()
        self._factories.clear()
        logger.debug("Container cleared")


class ServiceContainer(Container):
    """Application service container with predefined services."""
    
    def __init__(self, db_session: Session, settings: any):
        """Initialize with core dependencies.
        
        Args:
            db_session: Database session
            settings: Application settings
        """
        super().__init__()
        
        # Register core dependencies
        self.register_singleton('db', db_session)
        self.register_singleton('settings', settings)
        
        # Register repositories
        self._register_repositories(db_session)
        
        # Register services
        self._register_services(db_session)
        
        # Register fetchers
        self._register_fetchers(settings)
        
        self._initialized = True
        logger.info("ServiceContainer initialized")
    
    def _register_repositories(self, db: Session):
        """Register all repository factories."""
        from ai_news_aggregater.storage.repository import NewsRepository, UserRepository
        
        self.register_factory('news_repo', lambda: NewsRepository(db))
        self.register_factory('user_repo', lambda: UserRepository(db))
    
    def _register_services(self, db: Session):
        """Register all service factories."""
        from ai_news_aggregater.services.news_service import (
            NewsService, UserService, AggregationService
        )
        
        self.register_factory('news_service', lambda: NewsService(db))
        self.register_factory('user_service', lambda: UserService(db))
        self.register_factory('aggregation_service', lambda: AggregationService(db))
    
    def _register_fetchers(self, settings: any):
        """Register all fetcher factories."""
        from ai_news_aggregater.fetchers.web_fetcher import WebScraper
        from ai_news_aggregater.fetchers.blog_fetcher import RSSFeedScraper
        from ai_news_aggregater.fetchers.video_fetcher import YouTubeScraper
        
        self.register_factory(
            'web_fetcher',
            lambda: WebScraper(settings.fetcher.timeout, settings.fetcher.max_retries)
        )
        self.register_factory(
            'rss_fetcher',
            lambda: RSSFeedScraper(settings.fetcher.timeout, settings.fetcher.max_retries)
        )
        self.register_factory(
            'video_fetcher',
            lambda: YouTubeScraper(settings.fetcher.timeout, settings.fetcher.max_retries)
        )


# Global container instance
_container: Container = Container()


def setup_container(db_session: Session, settings: any):
    """Initialize global container with dependencies.
    
    Args:
        db_session: Database session
        settings: Application settings
    """
    global _container
    _container = ServiceContainer(db_session, settings)


def get_container() -> Container:
    """Get global container instance.
    
    Returns:
        Global container
    """
    return _container


def get_service(name: str, *args, **kwargs) -> Any:
    """Get service from global container.
    
    Args:
        name: Service name
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Service instance
    """
    return _container.get(name, *args, **kwargs)
