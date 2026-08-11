
from sqlalchemy.orm import Session

from app.logging.logger import logger
from app.models import User
from app.storage.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for User model with custom queries."""

    def __init__(self, db: Session):
        from app.models import User
        super().__init__(db, User)

    def get_or_create(self, email: str, **user_data) -> tuple:
        """Get existing user by email or create new.

        Args:
            email: User email (unique identifier)
            **user_data: Fields for User model

        Returns:
            Tuple of (user_record, is_new)
        """
        from app.models import User

        existing = self.filter_one(email=email)
        if existing:
            logger.info(f"User email already exists: {email}")
            return existing, False

        user_data['email'] = email
        user = User(**user_data)
        return self.create(user)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.filter_one(email=email)

    def get_active_users(self) -> list[User]:
        """Get all active users."""
        return self.filter(is_active=True)

    def get_by_interests(self, interests: list[str]) -> list[User]:
        """Get users interested in any of the given topics."""
        from sqlalchemy import or_

        query = self.db.query(User).filter(
            or_(*[User.interests.contains(interest) for interest in interests])
        )
        return query.all()

    def deactivate(self, id: int) -> User | None:
        """Deactivate a user."""
        return self.update(id, {'is_active': False})

    def activate(self, id: int) -> User | None:
        """Activate a user."""
        return self.update(id, {'is_active': True})
