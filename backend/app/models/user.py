"""Enterprise User model with RBAC, audit fields, and soft deletes."""

import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import validates

from app.models.base import Base


class UserRole(enum.StrEnum):
    """Role-based access control levels."""

    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(enum.StrEnum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """Enterprise user model with full audit trail and RBAC.

    Features:
    - Role-based access control (user, admin, super_admin)
    - Account status tracking (active, inactive, suspended, pending)
    - Soft delete support
    - Full audit trail (created/updated timestamps and actors)
    - Email verification tracking
    - Failed login attempt tracking
    - User preferences (interests, digest settings)
    """

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_role", "role"),
        Index("ix_users_status", "status"),
        Index("ix_users_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)

    # RBAC
    role = Column(
        Enum(
            UserRole,
            values_callable=lambda e: [m.value for m in e],
            native_enum=False,
        ),
        default=UserRole.USER,
        nullable=False,
    )
    status = Column(
        Enum(
            UserStatus,
            values_callable=lambda e: [m.value for m in e],
            native_enum=False,
        ),
        default=UserStatus.ACTIVE,
        nullable=False,
    )

    # Email verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)

    # User preferences
    interests = Column(JSON, default=list)  # List of category strings
    digest_subscribed = Column(Boolean, default=True, nullable=False)
    digest_frequency = Column(String(20), default="daily")  # daily, weekly, instant
    preferred_language = Column(String(10), default="en")

    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    password_changed_at = Column(DateTime, nullable=True)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    @validates("email")
    def validate_email(self, key, email):
        """Normalize email to lowercase."""
        if email:
            return email.lower().strip()
        return email

    @validates("name")
    def validate_name(self, key, name):
        """Strip whitespace from name."""
        if name:
            return name.strip()
        return name

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)

    @property
    def is_super_admin(self) -> bool:
        """Check if user has super admin privileges."""
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
