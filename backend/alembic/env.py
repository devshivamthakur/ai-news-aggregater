"""Alembic migration environment."""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, inspect, pool, text

from alembic import context
from alembic.script import ScriptDirectory
from app.config.settings import settings
from app.models import Base

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return settings.database.url


def _reconcile_orphaned_revision(connection) -> None:
    """If DB alembic_version contains an unknown revision or missing schema columns, reset version so migrations run."""
    try:
        res = connection.execute(text("SELECT version_num FROM alembic_version")).fetchone()
        should_reset = False
        if res and res[0]:
            db_rev = res[0]
            script = ScriptDirectory.from_config(config)
            try:
                script.get_revision(db_rev)
            except Exception:
                should_reset = True

            if not should_reset:
                # Also verify schema columns: if users table exists but missing 'interests', reset version so Alembic applies migration scripts
                inspector = inspect(connection)
                tables = set(inspector.get_table_names())
                if "users" in tables:
                    user_cols = {c["name"] for c in inspector.get_columns("users")}
                    if "interests" not in user_cols:
                        should_reset = True

        if should_reset:
            connection.execute(text("DELETE FROM alembic_version"))
            connection.commit()
    except Exception:
        pass


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _reconcile_orphaned_revision(connection)

        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
