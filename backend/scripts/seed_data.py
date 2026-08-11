#!/usr/bin/env python3
"""Seed initial data with enterprise defaults."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone

from app.api.security import hash_password
from app.models import User, UserRole, UserStatus
from app.services.category_service import CategoryService
from app.services.ingestion_source_service import IngestionSourceService
from app.storage.db import SessionLocal


def seed_admin_user(db):
    """Create default admin user if not exists."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@ainews.local")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!@#")

    existing = db.query(User).filter(User.email == admin_email).first()
    if existing:
        print(f"Admin user already exists: {admin_email}")
        return

    admin = User(
        email=admin_email,
        name="System Admin",
        password_hash=hash_password(admin_password),
        role=UserRole.SUPER_ADMIN,
        status=UserStatus.ACTIVE,
        email_verified=True,
        email_verified_at=datetime.now(timezone.utc),
        interests=["AI", "Technology", "Science"],
        digest_subscribed=True,
    )
    db.add(admin)
    db.commit()
    print(f"Created admin user: {admin_email}")


def seed_default_sources(db):
    """Sync default ingestion sources."""
    svc = IngestionSourceService(db)
    stats = svc.sync_defaults()
    print(f"Synced sources: {stats}")


def seed_test_users(db):
    """Create test users for development."""
    test_users = [
        {
            "email": "user1@test.com",
            "name": "Test User 1",
            "password": "Test123!@#",
            "interests": ["AI", "Machine Learning"],
        },
        {
            "email": "user2@test.com",
            "name": "Test User 2",
            "password": "Test123!@#",
            "interests": ["Technology", "Programming"],
        },
    ]

    for user_data in test_users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            continue

        user = User(
            email=user_data["email"],
            name=user_data["name"],
            password_hash=hash_password(user_data["password"]),
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            email_verified=True,
            email_verified_at=datetime.now(timezone.utc),
            interests=user_data["interests"],
            digest_subscribed=True,
        )
        db.add(user)

    db.commit()
    print(f"Created {len(test_users)} test users")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Seeding database...")
        seed_admin_user(db)
        print("Syncing default categories...")
        CategoryService(db).sync_defaults()
        seed_default_sources(db)

        if os.getenv("ENVIRONMENT") == "development":
            seed_test_users(db)

        print("Seeding complete!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
