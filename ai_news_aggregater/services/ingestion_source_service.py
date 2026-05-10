"""CRUD and sync for RSS / YouTube ingestion sources stored in the database."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from ai_news_aggregater.data.default_sources import DEFAULT_RSS_FEEDS, DEFAULT_YOUTUBE_CHANNELS
from ai_news_aggregater.logging.logger import logger
from ai_news_aggregater.models import IngestionSource
from ai_news_aggregater.models.source import SourceType


class IngestionSourceService:
    """Manage ingestion_sources rows."""

    def __init__(self, db: Session):
        self._db = db

    def list_sources(self, active_only: bool = False) -> list[IngestionSource]:
        q = self._db.query(IngestionSource).order_by(IngestionSource.source_type, IngestionSource.display_name)
        if active_only:
            q = q.filter(IngestionSource.is_active.is_(True))
        return q.all()

    def get_active_rss(self) -> list[IngestionSource]:
        return (
            self._db.query(IngestionSource)
            .filter(IngestionSource.is_active.is_(True), IngestionSource.source_type == SourceType.RSS.value)
            .all()
        )

    def get_active_youtube(self) -> list[IngestionSource]:
        return (
            self._db.query(IngestionSource)
            .filter(IngestionSource.is_active.is_(True), IngestionSource.source_type == SourceType.YOUTUBE.value)
            .all()
        )

    def sync_defaults(self) -> dict[str, Any]:
        """Upsert rows from `default_sources` (idempotent)."""
        created = 0
        updated = 0

        for display_name, urls in DEFAULT_RSS_FEEDS.items():
            for url in urls:
                row = (
                    self._db.query(IngestionSource)
                    .filter(
                        IngestionSource.source_type == SourceType.RSS.value,
                        IngestionSource.identifier == url,
                    )
                    .first()
                )
                if row:
                    if row.display_name != display_name or not row.is_active:
                        row.display_name = display_name
                        row.is_active = True
                        updated += 1
                else:
                    self._db.add(
                        IngestionSource(
                            source_type=SourceType.RSS.value,
                            display_name=display_name,
                            identifier=url,
                            is_active=True,
                        )
                    )
                    created += 1

        for channel_id, display_name in DEFAULT_YOUTUBE_CHANNELS:
            row = (
                self._db.query(IngestionSource)
                .filter(
                    IngestionSource.source_type == SourceType.YOUTUBE.value,
                    IngestionSource.identifier == channel_id,
                )
                .first()
            )
            if row:
                if row.display_name != display_name or not row.is_active:
                    row.display_name = display_name
                    row.is_active = True
                    updated += 1
            else:
                self._db.add(
                    IngestionSource(
                        source_type=SourceType.YOUTUBE.value,
                        display_name=display_name,
                        identifier=channel_id,
                        is_active=True,
                    )
                )
                created += 1

        self._db.commit()
        logger.info("Synced default ingestion sources: created=%s updated=%s", created, updated)
        return {
            "created": created,
            "updated": updated,
            "rss_feed_urls": sum(len(u) for u in DEFAULT_RSS_FEEDS.values()),
            "youtube_channels": len(DEFAULT_YOUTUBE_CHANNELS),
        }

    def create(
        self,
        *,
        source_type: str,
        display_name: str,
        identifier: str,
        is_active: bool = True,
    ) -> IngestionSource:
        if source_type not in (SourceType.RSS.value, SourceType.YOUTUBE.value):
            raise ValueError("source_type must be 'rss' or 'youtube'")
        row = IngestionSource(
            source_type=source_type,
            display_name=display_name,
            identifier=identifier.strip(),
            is_active=is_active,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def update(self, source_id: int, **fields: Any) -> IngestionSource | None:
        row = self._db.query(IngestionSource).filter(IngestionSource.id == source_id).first()
        if not row:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(row, key):
                setattr(row, key, value)
        self._db.commit()
        self._db.refresh(row)
        return row
