"""initial

Revision ID: 4e3df588d7ac
Revises:
Create Date: 2026-05-10 11:57:15.972977

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4e3df588d7ac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Bootstrap the full schema.

    Guards each table with an existence check so the migration works both on a
    fresh database (nothing exists) and on a database previously created with
    SQLAlchemy ``create_all`` (tables already present).
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "news" not in tables:
        op.create_table(
            "news",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("category", sa.String(), nullable=True),
            sa.Column("source", sa.String(), nullable=True),
            sa.Column("url", sa.String(), nullable=False),
            sa.Column("published_at", sa.DateTime(), nullable=True),
            sa.Column(
                "news_type",
                sa.Enum("ARTICLE", "VIDEO", "BLOG_POST", name="newstype"),
                nullable=True,
            ),
            sa.Column("fetch_hour", sa.Integer(), nullable=True),
            sa.Column("fetch_date", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("url", name="news_url_key"),
        )
        op.create_index("ix_news_id", "news", ["id"], unique=False)

    if "ingestion_sources" not in tables:
        op.create_table(
            "ingestion_sources",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("source_type", sa.String(length=20), nullable=False),
            sa.Column("display_name", sa.String(length=512), nullable=False),
            sa.Column("identifier", sa.String(length=2048), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "source_type", "identifier", name="uq_ingestion_type_identifier"
            ),
        )
        op.create_index("ix_ingestion_sources_id", "ingestion_sources", ["id"], unique=False)
        op.create_index(
            "ix_ingestion_sources_source_type", "ingestion_sources", ["source_type"], unique=False
        )

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("password_hash", sa.String(), nullable=True),
            sa.Column("interests", sa.JSON(), nullable=True),
            sa.Column("digest_subscribed", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("is_active", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email", name="users_email_key"),
        )
        op.create_index("ix_users_id", "users", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_news_id", table_name="news")
    op.drop_table("news")
    op.drop_index("ix_ingestion_sources_source_type", table_name="ingestion_sources")
    op.drop_index("ix_ingestion_sources_id", table_name="ingestion_sources")
    op.drop_table("ingestion_sources")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
