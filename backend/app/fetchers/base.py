"""Abstract base fetcher for consistent news fetching patterns."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

import requests

from app.logging.logger import logger


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    )
}


def fetch_feed_bytes(url: str, *, timeout: int = 20) -> str | None:
    """Fetch a feed's raw content as text.

    Performs the HTTP request ourselves (instead of letting feedparser do it)
    so we can:
    - send a browser-like User-Agent,
    - honour a timeout,
    - ignore the server's ``Content-Type`` (GitHub raw serves feeds as
      ``text/plain``, which feedparser otherwise refuses to parse).

    Returns the decoded body, or ``None`` on failure.
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        response.raise_for_status()
        # Let requests infer the correct encoding; fall back to utf-8.
        return response.text
    except requests.RequestException as e:
        logger.warning("Failed to download feed %s: %s", url, e)
        return None


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
    def fetch(self) -> list[dict[str, Any]]:
        """Fetch news from source.

        Returns:
            List of article dictionaries with keys: url, title, content,
            summary, category, published_at, source, news_type

        Raises:
            Exception: If fetching fails after retries
        """
        pass

    @abstractmethod
    def validate_data(self, item: dict) -> bool:
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

    def sanitize_text(self, text: str | None, max_length: int = 5000) -> str:
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

    def ensure_published_date(self, date: datetime | None) -> datetime:
        """Ensure we have a valid published date.

        Args:
            date: Date to validate

        Returns:
            Provided date or current UTC time
        """
        if isinstance(date, datetime):
            return date
        return datetime.now(UTC)


class FetcherRegistry:
    """Registry for managing fetchers."""

    _fetchers: dict[str, BaseFetcher] = {}

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
    def get(cls, name: str) -> BaseFetcher | None:
        """Get a registered fetcher.

        Args:
            name: Fetcher name

        Returns:
            Fetcher instance or None
        """
        return cls._fetchers.get(name)

    @classmethod
    def get_all(cls) -> dict[str, BaseFetcher]:
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
