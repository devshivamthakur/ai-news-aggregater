"""Tests for DB-backed ingestion sources and sync."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, IngestionSource
from app.services.ingestion_source_service import IngestionSourceService


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)
    db = session()
    yield db
    db.close()


def test_sync_defaults_idempotent(memory_db):
    svc = IngestionSourceService(memory_db)
    a = svc.sync_defaults()
    b = svc.sync_defaults()
    assert a["created"] > 0
    assert b["created"] == 0
    assert b["updated"] == 0
    rows = memory_db.query(IngestionSource).all()
    assert len(rows) == (
        a["rss_feed_urls"]
        + a["youtube_channels"]
        + a["medium_sources"]
        + a["github_sources"]
    )


def test_sync_defaults_creates_github_trending_source(memory_db):
    svc = IngestionSourceService(memory_db)
    svc.sync_defaults()

    active = svc.get_active_github()
    assert len(active) == 1
    assert active[0].source_type == "github"
    assert active[0].identifier == "trending/ai"
    assert active[0].display_name == "GitHub Trending AI Repos"


def test_create_rejects_unknown_type(memory_db):
    svc = IngestionSourceService(memory_db)
    with pytest.raises(ValueError):
        svc.create(
            source_type="badtype",
            display_name="Bad",
            identifier="https://example.com/rss.xml",
        )


def test_create_github_source(memory_db):
    svc = IngestionSourceService(memory_db)
    row = svc.create(
        source_type="github",
        display_name="GitHub Trending LLM",
        identifier="trending/llm",
    )
    assert row.source_type == "github"
    assert svc.get_active_github()[0].identifier == "trending/llm"


def test_sync_defaults_preserves_existing_sources(memory_db):
    """Re-syncing must never remove or disable sources that already exist.

    Guards user-managed rows (custom RSS feeds, custom GitHub identifiers)
    from being wiped by a later sync_defaults() call.
    """
    svc = IngestionSourceService(memory_db)
    svc.sync_defaults()

    # User-managed changes after the first sync:
    # 1. a custom source added by hand
    custom = svc.create(
        source_type="github",
        display_name="GitHub Trending LLM",
        identifier="trending/llm",
    )
    # 2. a non-default RSS source added by hand
    custom_rss = svc.create(
        source_type="rss",
        display_name="My Custom Feed",
        identifier="https://example.com/custom.xml",
    )

    # Re-sync: nothing new to create, and rows are only updated, never deleted.
    result = svc.sync_defaults()
    assert result["created"] == 0
    assert result["updated"] == 0

    # Custom sources still there, still active, untouched.
    survived = svc.get_by_id(custom.id)
    assert survived is not None
    assert survived.is_active is True
    survived_rss = svc.get_by_id(custom_rss.id)
    assert survived_rss is not None
    assert survived_rss.is_active is True

    # Row count after first sync + 2 custom, unchanged by the second sync.
    # 8 RSS + 5 YouTube + 2 Medium + 1 GitHub = 16 defaults + 2 custom.
    rows = memory_db.query(IngestionSource).all()
    assert len(rows) == 18


def test_list_active_filter(memory_db):
    svc = IngestionSourceService(memory_db)
    svc.sync_defaults()
    memory_db.query(IngestionSource).filter(IngestionSource.identifier.like("%openai.com%")).update(
        {IngestionSource.is_active: False}, synchronize_session=False
    )
    memory_db.commit()
    active = svc.list_sources(active_only=True)
    assert all(r.is_active for r in active)
    assert not any("openai.com" in r.identifier for r in active)
