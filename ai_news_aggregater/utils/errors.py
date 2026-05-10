"""Comprehensive error handling and custom exceptions."""

import time
from functools import wraps
from typing import Callable, Any, Optional
from ai_news_aggregater.logging.logger import logger


# ============================================================================
# Custom Exceptions
# ============================================================================

class AggregatorException(Exception):
    """Base exception for all aggregator errors."""
    pass


class NewsAggregatorError(AggregatorException):
    """Base exception for the news aggregator (backward compatibility)."""
    pass


class FetchError(AggregatorException):
    """Error during news fetching."""
    
    def __init__(self, message: str, source: Optional[str] = None):
        self.message = message
        self.source = source
        super().__init__(f"Fetch error from {source}: {message}" if source else message)


class ValidationError(AggregatorException):
    """Data validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(f"Validation error in {field}: {message}" if field else message)


class DatabaseError(AggregatorException):
    """Database operation error."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        self.message = message
        self.operation = operation
        super().__init__(f"Database {operation} error: {message}" if operation else message)


class ProcessingError(AggregatorException):
    """Error during data processing."""
    pass


class ConfigError(AggregatorException):
    """Configuration error."""
    pass


class EmailError(AggregatorException):
    """Email sending error."""
    
    def __init__(self, message: str, recipient: Optional[str] = None):
        self.message = message
        self.recipient = recipient
        super().__init__(f"Email error to {recipient}: {message}" if recipient else message)


class SchedulerError(AggregatorException):
    """Scheduler error."""
    pass


# ============================================================================
# Decorators
# ============================================================================

def retry_on_failure(max_retries: int = 3, delay: float = 2.0, backoff: float = 1.0):
    """Retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for each retry
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for "
                            f"{func.__name__}: {e}. Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def handle_errors(
    error_type: type = Exception,
    default_return: Any = None,
    log_level: str = "error"
):
    """Error handling decorator.
    
    Args:
        error_type: Exception type to catch
        default_return: Default value if error occurs
        log_level: Logging level (debug, info, warning, error)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except error_type as e:
                log_func = getattr(logger, log_level.lower())
                log_func(f"Error in {func.__name__}: {e}")
                return default_return
        
        return wrapper
    return decorator


def validate_args(**arg_validators):
    """Validate function arguments before execution.
    
    Args:
        **arg_validators: Argument name -> validator function pairs
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Validate kwargs
            for arg_name, validator in arg_validators.items():
                if arg_name in kwargs:
                    if not validator(kwargs[arg_name]):
                        raise ValidationError(
                            f"Invalid value for {arg_name}: {kwargs[arg_name]}",
                            arg_name
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def measure_execution_time(func: Callable) -> Callable:
    """Measure and log function execution time.
    
    Args:
        func: Function to measure
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        logger.debug(f"{func.__name__} executed in {duration:.3f}s")
        return result
    
    return wrapper


def log_calls(log_level: str = "info"):
    """Log function calls with arguments and results.
    
    Args:
        log_level: Logging level
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            log_func = getattr(logger, log_level.lower())
            log_func(f"Calling {func.__name__}")
            
            result = func(*args, **kwargs)
            return result
        
        return wrapper
    return decorator


# ============================================================================
# Error Handler Classes
# ============================================================================

class ErrorHandler:
    """Centralized error handling with recovery strategies."""
    
    @staticmethod
    def handle_fetch_error(error: Exception, source: str) -> Optional[Any]:
        """Handle fetch errors with recovery.
        
        Args:
            error: Exception that occurred
            source: Source name for context
            
        Returns:
            None or recovery value
        """
        logger.error(f"Fetch error from {source}: {error}")
        return None
    
    @staticmethod
    def handle_db_error(error: Exception, operation: str) -> None:
        """Handle database errors.
        
        Args:
            error: Exception that occurred
            operation: Database operation being performed
            
        Raises:
            DatabaseError: Wrapped database error
        """
        logger.error(f"Database {operation} error: {error}")
        raise DatabaseError(str(error), operation)
    
    @staticmethod
    def handle_validation_error(error: Exception, field: str) -> None:
        """Handle validation errors.
        
        Args:
            error: Exception that occurred
            field: Field that failed validation
            
        Raises:
            ValidationError: Wrapped validation error
        """
        logger.error(f"Validation error in {field}: {error}")
        raise ValidationError(str(error), field)
    
    @staticmethod
    def handle_email_error(error: Exception, recipient: str) -> bool:
        """Handle email errors gracefully.
        
        Args:
            error: Exception that occurred
            recipient: Recipient email
            
        Returns:
            False to indicate failure
        """
        logger.error(f"Email error to {recipient}: {error}")
        return False


# Backward compatibility
__all__ = [
    'AggregatorException',
    'NewsAggregatorError',
    'FetchError',
    'ValidationError',
    'DatabaseError',
    'ProcessingError',
    'ConfigError',
    'EmailError',
    'SchedulerError',
    'retry_on_failure',
    'handle_errors',
    'validate_args',
    'measure_execution_time',
    'log_calls',
    'ErrorHandler',
]