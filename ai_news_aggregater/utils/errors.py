import time
from functools import wraps
from typing import Callable, Any
from ai_news_aggregater.logging.logger import logger

class NewsAggregatorError(Exception):
    """Base exception for the news aggregator."""
    pass

class FetchError(NewsAggregatorError):
    """Error during data fetching."""
    pass

class ProcessingError(NewsAggregatorError):
    """Error during data processing."""
    pass

class DatabaseError(NewsAggregatorError):
    """Error with database operations."""
    pass

class EmailError(NewsAggregatorError):
    """Error with email sending."""
    pass

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry a function on failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {current_delay}s")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator