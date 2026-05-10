#!/usr/bin/env python3
"""Run Alembic migrations programmatically."""

import sys

from ai_news_aggregater.services.migration_service import MigrationService


def run_migrations(migrate_type: str = "upgrade"):
    """Run database migrations.

    Args:
        migrate_type: "upgrade" to apply migrations, "downgrade" to revert
    """
    svc = MigrationService()
    if migrate_type == "upgrade":
        svc.upgrade()
        print("✅ Database migrations applied successfully")
    elif migrate_type == "downgrade":
        svc.downgrade()
        print("✅ Database downgrade successful")
    else:
        print(f"❌ Unknown migration type: {migrate_type}")
        sys.exit(1)


if __name__ == "__main__":
    migrate_type = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    run_migrations(migrate_type)
