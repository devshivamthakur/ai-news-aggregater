"""add repository news type (github trending)

Revision ID: 4e3df588d7af
Revises: 4e3df588d7ae
Create Date: 2026-10-21 00:00:00.000000

Extends the native PostgreSQL ``newstype`` enum with the ``REPOSITORY``
label (used for daily GitHub trending repos). Also adds the previously
missing ``PODCAST`` and ``RESEARCH_PAPER`` labels that exist in the model
but were never applied to the DB type. SQLite is a no-op (enums are stored
as VARCHAR there).
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4e3df588d7af'
down_revision = '4e3df588d7ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return

    enum_name = "newstype"
    enum_name = "newstype"

    def _add_enum_label(label: str) -> None:
        bind.execute(
            sa.text(f"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS '{label}'")
        )

    _add_enum_label("REPOSITORY")
    # Repair enum labels that exist on the model but are missing in the DB
    # (news rows with these values would otherwise fail to insert).
    _add_enum_label("PODCAST")
    _add_enum_label("RESEARCH_PAPER")


def downgrade() -> None:
    # No downgrade: removing enum values is destructive of existing rows.
    # (PostgreSQL doesn't support dropping enum labels without a cumbersome
    # type rebuild; rows stored with REPOSITORY would become invalid.)
    pass
