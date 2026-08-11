from typing import Any, TypeVar

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.logging.logger import logger

T = TypeVar('T')


class BaseRepository[T]:
    """Abstract base repository with common CRUD operations."""

    def __init__(self, db: Session, model: type):
        """Initialize repository with database session and model class."""
        self.db = db
        self.model = model
        self._unique_fields = self._get_unique_fields()

    def _get_unique_fields(self) -> list[str]:
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
            if skip_if_exists:
                logger.warning(f"Duplicate {self.model.__name__}, returning existing: {e}")
                return obj, False
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise

    def get_by_id(self, id: int) -> T | None:
        """Get record by primary key."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> list[T]:
        """Get all records."""
        return self.db.query(self.model).all()

    def filter(self, **kwargs) -> list[T]:
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

    def filter_one(self, **kwargs) -> T | None:
        """Filter records and return first match."""
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first()

    def update(self, id: int, data: dict[str, Any]) -> T | None:
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

    def paginate(self, page: int = 1, page_size: int = 10) -> tuple[list[T], int]:
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
