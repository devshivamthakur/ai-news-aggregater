"""Common utility validators and helpers."""

from typing import Optional
from urllib.parse import urlparse
import re


class Validators:
    """Collection of validation functions."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_valid_hour(hour: int) -> bool:
        """Validate hour (0-23).
        
        Args:
            hour: Hour to validate
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(hour, int) and 0 <= hour <= 23
    
    @staticmethod
    def is_non_empty_string(text: Optional[str]) -> bool:
        """Validate non-empty string.
        
        Args:
            text: Text to validate
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(text, str) and len(text.strip()) > 0
    
    @staticmethod
    def is_non_empty_list(items: any) -> bool:
        """Validate non-empty list.
        
        Args:
            items: Items to validate
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(items, list) and len(items) > 0


class TextHelpers:
    """Text processing and formatting utilities."""
    
    @staticmethod
    def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to max length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add when truncating
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        return ' '.join(text.split())
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name or None
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return None
    
    @staticmethod
    def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
        """Estimate reading time in minutes.
        
        Args:
            text: Text to estimate
            words_per_minute: Reading speed
            
        Returns:
            Estimated minutes
        """
        word_count = len(text.split())
        minutes = max(1, word_count // words_per_minute)
        return minutes


class CollectionHelpers:
    """Collection processing utilities."""
    
    @staticmethod
    def flatten_list(nested_list: list) -> list:
        """Flatten nested list.
        
        Args:
            nested_list: List with nested items
            
        Returns:
            Flattened list
        """
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(CollectionHelpers.flatten_list(item))
            else:
                result.append(item)
        return result
    
    @staticmethod
    def remove_duplicates(items: list, key: any = None) -> list:
        """Remove duplicates from list while preserving order.
        
        Args:
            items: List with potential duplicates
            key: Optional key function for comparison
            
        Returns:
            List without duplicates
        """
        seen = set()
        result = []
        for item in items:
            identifier = key(item) if key else item
            if identifier not in seen:
                seen.add(identifier)
                result.append(item)
        return result
    
    @staticmethod
    def batch_list(items: list, batch_size: int) -> list:
        """Split list into batches.
        
        Args:
            items: List to batch
            batch_size: Size of each batch
            
        Returns:
            List of batches
        """
        if batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        return batches
