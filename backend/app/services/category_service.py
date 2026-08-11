"""Enterprise Category service for database operations and default seeding."""

from typing import Any

from sqlalchemy.orm import Session

from app.logging.logger import logger
from app.models.category import Category


class CategoryService:
    """Service layer for Category operations."""

    def __init__(self, db: Session):
        self._db = db

    def list_categories(self, active_only: bool = False) -> list[Category]:
        """List all categories."""
        q = self._db.query(Category).order_by(Category.name)
        if active_only:
            q = q.filter(Category.is_active.is_(True))
        return q.all()

    def get_by_id(self, category_id: int) -> Category | None:
        """Get category by ID."""
        return self._db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, name: str) -> Category | None:
        """Get category by name."""
        return self._db.query(Category).filter(Category.name.ilike(name)).first()

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        is_active: bool = True,
    ) -> Category:
        """Create a new category."""
        normalized_name = name.strip()
        existing = self.get_by_name(normalized_name)
        if existing:
            raise ValueError(f"Category '{normalized_name}' already exists.")

        row = Category(
            name=normalized_name,
            description=description,
            is_active=is_active,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        logger.info(f"Created category: {normalized_name}")
        return row

    def update(self, category_id: int, **fields: Any) -> Category | None:
        """Update an existing category."""
        row = self.get_by_id(category_id)
        if not row:
            return None

        if "name" in fields and fields["name"] is not None:
            name = fields["name"].strip()
            existing = self.get_by_name(name)
            if existing and existing.id != category_id:
                raise ValueError(f"Category '{name}' already exists.")
            row.name = name

        if "description" in fields:
            row.description = fields["description"]

        if "is_active" in fields and fields["is_active"] is not None:
            row.is_active = fields["is_active"]

        self._db.commit()
        self._db.refresh(row)
        logger.info(f"Updated category ID {category_id}")
        return row

    def delete(self, category_id: int) -> bool:
        """Delete a category."""
        row = self.get_by_id(category_id)
        if not row:
            return False
        self._db.delete(row)
        self._db.commit()
        logger.info(f"Deleted category ID {category_id}")
        return True

    def sync_defaults(self) -> dict:
        """Seed default categories if they do not exist."""
        defaults = [
            ("AI", "Artificial Intelligence and Machine Learning breakthroughs"),
            ("Technology", "General technology news, gadgets, and software"),
            ("Science", "Scientific discoveries, space, physics, and research"),
            ("Programming", "Software engineering, languages, frameworks, and patterns"),
            ("Finance", "Financial markets, economics, and business insights"),
            ("Health", "Medicine, health, fitness, and lifestyle wellness"),
            ("Education", "Education, learning, tutorials, and academic topics"),
            ("Business", "Business, startups, venture capital, and corporate news"),
            ("Sports", "Sports, matches, athletics, and updates"),
            ("Entertainment", "Movies, music, gaming, and pop culture"),
            ("Lifestyle", "Lifestyle, travel, food, and culture"),
        ]

        created = 0
        for name, desc in defaults:
            existing = self.get_by_name(name)
            if not existing:
                self.create(name=name, description=desc, is_active=True)
                created += 1

        return {"created": created, "total": len(defaults)}
