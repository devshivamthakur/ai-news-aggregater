"""Data storage and access layer."""

from .db import create_tables, get_db
from .news_repository import NewsRepository
from .user_repository import UserRepository

__all__ = [
    "get_db",
    "create_tables",
    "NewsRepository",
    "UserRepository",
]

