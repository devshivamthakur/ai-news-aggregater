"""Repository re-exports for backward compatibility."""

from .news_repository import NewsRepository
from .user_repository import UserRepository

__all__ = ["NewsRepository", "UserRepository"]
