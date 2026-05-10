"""Apply database schema changes via Alembic."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from ai_news_aggregater.logging.logger import logger


def _project_root_alembic_ini() -> Path:
    # ai_news_aggregater/services/migration_service.py -> repo root (parent of package dir)
    return Path(__file__).resolve().parent.parent.parent / "alembic.ini"


class MigrationService:
    """Run Alembic migrations using the project `alembic.ini`."""

    def __init__(self, alembic_ini: Path | None = None):
        self._alembic_ini = alembic_ini or _project_root_alembic_ini()

    def _config(self) -> Config:
        path = self._alembic_ini
        if not path.is_file():
            raise FileNotFoundError(f"Alembic config not found: {path}")
        return Config(str(path))

    def upgrade(self, revision: str = "head") -> None:
        command.upgrade(self._config(), revision)
        logger.info("Database migrations upgraded to %s", revision)

    def downgrade(self, revision: str = "-1") -> None:
        command.downgrade(self._config(), revision)
        logger.info("Database migrations downgraded to %s", revision)
