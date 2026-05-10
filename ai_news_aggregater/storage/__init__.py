"""Data storage and access layer."""

from ai_news_aggregater.storage.repository import (
    BaseRepository,
    NewsRepository,
    UserRepository,
)

__all__ = [
    'BaseRepository',
    'NewsRepository',
    'UserRepository',
]
