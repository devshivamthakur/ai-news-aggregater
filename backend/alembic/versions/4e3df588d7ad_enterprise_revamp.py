"""enterprise revamp

Revision ID: 4e3df588d7ad
Revises: 4e3df588d7ac
Create Date: 2026-08-11 12:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4e3df588d7ad'
down_revision = '4e3df588d7ac'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    # Create Categories table if not exists
    if "categories" not in tables:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_categories_id", "categories", ["id"], unique=False)
        op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    # 1. Update Ingestion Sources
    source_cols = {col["name"] for col in inspector.get_columns("ingestion_sources")}

    if "description" not in source_cols:
        op.add_column("ingestion_sources", sa.Column("description", sa.Text(), nullable=True))
    if "category" not in source_cols:
        op.add_column(
            "ingestion_sources", sa.Column("category", sa.String(length=100), nullable=True)
        )
    if "status" not in source_cols:
        op.add_column(
            "ingestion_sources",
            sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        )
        op.create_index(
            "ix_ingestion_sources_status", "ingestion_sources", ["status"], unique=False
        )
    if "fetch_interval_minutes" not in source_cols:
        op.add_column(
            "ingestion_sources",
            sa.Column("fetch_interval_minutes", sa.Integer(), nullable=False, server_default="60"),
        )
    if "priority" not in source_cols:
        op.add_column(
            "ingestion_sources",
            sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        )
    if "max_items_per_fetch" not in source_cols:
        op.add_column(
            "ingestion_sources",
            sa.Column("max_items_per_fetch", sa.Integer(), nullable=False, server_default="50"),
        )
    if "last_fetched_at" not in source_cols:
        op.add_column(
            "ingestion_sources", sa.Column("last_fetched_at", sa.DateTime(), nullable=True)
        )
    if "last_error_at" not in source_cols:
        op.add_column("ingestion_sources", sa.Column("last_error_at", sa.DateTime(), nullable=True))
    if "last_error_message" not in source_cols:
        op.add_column(
            "ingestion_sources", sa.Column("last_error_message", sa.Text(), nullable=True)
        )
    if "consecutive_errors" not in source_cols:
        op.add_column(
            "ingestion_sources",
            sa.Column("consecutive_errors", sa.Integer(), nullable=False, server_default="0"),
        )
    if "total_fetches" not in source_cols:
        op.add_column(
            "ingestion_sources",
            sa.Column("total_fetches", sa.Integer(), nullable=False, server_default="0"),
        )
    if "total_items_fetched" not in source_cols:
        op.add_column(
            "ingestion_sources",
            sa.Column("total_items_fetched", sa.Integer(), nullable=False, server_default="0"),
        )
    if "rate_limit_remaining" not in source_cols:
        op.add_column(
            "ingestion_sources", sa.Column("rate_limit_remaining", sa.Integer(), nullable=True)
        )
    if "rate_limit_reset_at" not in source_cols:
        op.add_column(
            "ingestion_sources", sa.Column("rate_limit_reset_at", sa.DateTime(), nullable=True)
        )
    if "created_by" not in source_cols:
        op.add_column("ingestion_sources", sa.Column("created_by", sa.Integer(), nullable=True))
    if "updated_by" not in source_cols:
        op.add_column("ingestion_sources", sa.Column("updated_by", sa.Integer(), nullable=True))

    # Add ingestion sources index
    source_indexes = {idx["name"] for idx in inspector.get_indexes("ingestion_sources")}
    if "ix_ingestion_sources_is_active" not in source_indexes:
        op.create_index(
            "ix_ingestion_sources_is_active", "ingestion_sources", ["is_active"], unique=False
        )

    # 2. Update Users
    user_cols = {col["name"] for col in inspector.get_columns("users")}

    if "role" not in user_cols:
        op.add_column(
            "users", sa.Column("role", sa.String(length=50), nullable=False, server_default="user")
        )
        op.create_index("ix_users_role", "users", ["role"], unique=False)
    if "status" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "status", sa.String(length=50), nullable=False, server_default="active"
            ),
        )
        op.create_index("ix_users_status", "users", ["status"], unique=False)
    if "email_verified" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "email_verified", sa.Boolean(), nullable=False, server_default="false"
            ),
        )
    if "email_verified_at" not in user_cols:
        op.add_column(
            "users", sa.Column("email_verified_at", sa.DateTime(), nullable=True)
        )
    if "digest_frequency" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "digest_frequency",
                sa.String(length=20),
                nullable=False,
                server_default="daily",
            ),
        )
    if "preferred_language" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "preferred_language", sa.String(length=10), nullable=False, server_default="en"
            ),
        )
    if "failed_login_attempts" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "failed_login_attempts", sa.Integer(), nullable=False, server_default="0"
            ),
        )
    if "locked_until" not in user_cols:
        op.add_column("users", sa.Column("locked_until", sa.DateTime(), nullable=True))
    if "last_login_at" not in user_cols:
        op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))
    if "last_login_ip" not in user_cols:
        op.add_column("users", sa.Column("last_login_ip", sa.String(length=45), nullable=True))
    if "password_changed_at" not in user_cols:
        op.add_column("users", sa.Column("password_changed_at", sa.DateTime(), nullable=True))
    if "deleted_at" not in user_cols:
        op.add_column("users", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    if "deleted_by" not in user_cols:
        op.add_column("users", sa.Column("deleted_by", sa.Integer(), nullable=True))
    if "created_by" not in user_cols:
        op.add_column("users", sa.Column("created_by", sa.Integer(), nullable=True))
    if "updated_by" not in user_cols:
        op.add_column("users", sa.Column("updated_by", sa.Integer(), nullable=True))

    # Safely convert is_active to Boolean if it's Integer
    for col in inspector.get_columns("users"):
        if col["name"] == "is_active" and isinstance(col["type"], sa.Integer):
            # Change Column type to Boolean safely
            op.execute(
                "ALTER TABLE users ALTER COLUMN is_active TYPE BOOLEAN USING (is_active::boolean)"
            )
            op.execute("ALTER TABLE users ALTER COLUMN is_active SET DEFAULT true")

    user_indexes = {idx["name"] for idx in inspector.get_indexes("users")}
    if "ix_users_email_active" not in user_indexes:
        op.create_index("ix_users_email_active", "users", ["email", "is_active"], unique=False)
    if "ix_users_created_at" not in user_indexes:
        op.create_index("ix_users_created_at", "users", ["created_at"], unique=False)

    # 3. Update News
    news_cols = {col["name"] for col in inspector.get_columns("news")}

    if "source_url" not in news_cols:
        op.add_column("news", sa.Column("source_url", sa.String(length=2048), nullable=True))
    if "image_url" not in news_cols:
        op.add_column("news", sa.Column("image_url", sa.String(length=2048), nullable=True))
    if "author" not in news_cols:
        op.add_column("news", sa.Column("author", sa.String(length=255), nullable=True))
    if "status" not in news_cols:
        op.add_column(
            "news",
            sa.Column(
                "status", sa.String(length=50), nullable=False, server_default="analyzed"
            ),
        )
        op.create_index("ix_news_status", "news", ["status"], unique=False)
    if "sentiment_score" not in news_cols:
        op.add_column("news", sa.Column("sentiment_score", sa.Float(), nullable=True))
    if "keywords" not in news_cols:
        op.add_column("news", sa.Column("keywords", sa.Text(), nullable=True))
    if "reading_time_minutes" not in news_cols:
        op.add_column("news", sa.Column("reading_time_minutes", sa.Integer(), nullable=True))
    if "language" not in news_cols:
        op.add_column(
            "news", sa.Column("language", sa.String(length=10), nullable=False, server_default="en")
        )
    if "updated_at" not in news_cols:
        op.add_column(
            "news",
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        )
    if "is_active" not in news_cols:
        op.add_column(
            "news", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true")
        )
    if "deleted_at" not in news_cols:
        op.add_column("news", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    if "ingestion_source_id" not in news_cols:
        op.add_column("news", sa.Column("ingestion_source_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_news_ingestion_source", "news", "ingestion_sources", ["ingestion_source_id"], ["id"]
        )

    # Create News indexes
    news_indexes = {idx["name"] for idx in inspector.get_indexes("news")}
    if "ix_news_category" not in news_indexes:
        op.create_index("ix_news_category", "news", ["category"], unique=False)
    if "ix_news_source" not in news_indexes:
        op.create_index("ix_news_source", "news", ["source"], unique=False)
    if "ix_news_published_at" not in news_indexes:
        op.create_index("ix_news_published_at", "news", ["published_at"], unique=False)
    if "ix_news_news_type" not in news_indexes:
        op.create_index("ix_news_news_type", "news", ["news_type"], unique=False)
    if "ix_news_created_at" not in news_indexes:
        op.create_index("ix_news_created_at", "news", ["created_at"], unique=False)
    if "ix_news_fetch_date" not in news_indexes:
        op.create_index("ix_news_fetch_date", "news", ["fetch_date"], unique=False)


def downgrade() -> None:
    # Downgrades are not required for this enterprise revamp as we are keeping schema forward
    # compatible
    pass
