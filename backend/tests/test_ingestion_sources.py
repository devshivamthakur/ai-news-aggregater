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
    assert len(rows) == a["rss_feed_urls"] + a["youtube_channels"] + a["medium_sources"]


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
