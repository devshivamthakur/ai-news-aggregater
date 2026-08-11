
from sqlalchemy.orm import Session

from app.logging.logger import logger
from app.models import User
from app.storage.user_repository import UserRepository


class UserService:
    """Business logic for user operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.repo = UserRepository(db)

    def register_user(
        self,
        email: str,
        name: str,
        interests: list[str]
    ) -> tuple[User, bool]:
        """Register a new user with automatic duplicate detection.

        Args:
            email: User email (must be unique)
            name: User display name
            interests: List of user interests

        Returns:
            Tuple of (user_record, is_new)
        """
        if not email or '@' not in email:
            raise ValueError("Invalid email format")
        if not interests or not isinstance(interests, list):
            raise ValueError("Interests must be a non-empty list")

        logger.info(f"Registering user: {email}")
        return self.repo.get_or_create(
            email=email,
            name=name,
            interests=interests
        )

    def get_user(self, email: str) -> User | None:
        """Get user by email."""
        return self.repo.get_by_email(email)

    def get_active_users(self) -> list[User]:
        """Get all active users."""
        logger.info("Fetching active users")
        return self.repo.get_active_users()

    def get_users_by_interests(self, interests: list[str]) -> list[User]:
        """Get users interested in any of the given topics.

        Args:
            interests: List of interest keywords

        Returns:
            List of matching users
        """
        if not interests:
            raise ValueError("Interests list cannot be empty")
        logger.info(f"Finding users interested in: {interests}")
        return self.repo.get_by_interests(interests)

    def update_interests(self, email: str, interests: list[str]) -> User | None:
        """Update user interests.

        Args:
            email: User email
            interests: New interests list

        Returns:
            Updated user or None
        """
        user = self.get_user(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None

        return self.repo.update(user.id, {'interests': interests})

    def deactivate_user(self, email: str) -> User | None:
        """Deactivate a user."""
        user = self.get_user(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None

        logger.info(f"Deactivating user: {email}")
        return self.repo.deactivate(user.id)

    def activate_user(self, email: str) -> User | None:
        """Activate a user."""
        user = self.get_user(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None

        logger.info(f"Activating user: {email}")
        return self.repo.activate(user.id)
