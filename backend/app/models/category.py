"""Enterprise Category model."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.models.base import Base


def _utcnow():
    return datetime.now(UTC)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"
