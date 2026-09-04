"""feed interest index

Revision ID: 4e3df588d7ae
Revises: 4e3df588d7ad
Create Date: 2026-08-18 00:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4e3df588d7ae'
down_revision = '4e3df588d7ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes("news")
    if not any(idx["name"] == "ix_news_category_created_at" for idx in indexes):
        op.create_index(
            "ix_news_category_created_at",
            "news",
            ["category", "created_at"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes("news")
    if any(idx["name"] == "ix_news_category_created_at" for idx in indexes):
        op.drop_index("ix_news_category_created_at", table_name="news")
