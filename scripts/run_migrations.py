#!/usr/bin/env python3
"""Run Alembic migrations programmatically."""

import sys
from alembic.config import Config
from alembic import command
from pathlib import Path

def run_migrations(migrate_type: str = "upgrade"):
    """Run database migrations.
    
    Args:
        migrate_type: "upgrade" to apply migrations, "downgrade" to revert
    """
    # Get the alembic configuration
    alembic_cfg = Config(Path(__file__).parent.parent / "alembic.ini")
    
    if migrate_type == "upgrade":
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations applied successfully")
    elif migrate_type == "downgrade":
        command.downgrade(alembic_cfg, "-1")
        print("✅ Database downgrade successful")
    else:
        print(f"❌ Unknown migration type: {migrate_type}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_type = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    run_migrations(migrate_type)
