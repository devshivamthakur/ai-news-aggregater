"""Enterprise CRUD and sync for ingestion sources stored in the database."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.data.default_sources import (
    DEFAULT_MEDIUM_SOURCES,
    DEFAULT_RSS_FEEDS,
    DEFAULT_YOUTUBE_CHANNELS,
)
from app.logging.logger import logger
from app.models import IngestionSource
from app.models.source import SourceStatus, SourceType

# Identifiers that were previously seeded but are now confirmed dead
# (e.g. 404/403 feeds, channels that no longer exist). sync_defaults()
# deactivates any active rows matching these so stale sources stop being
# polled. Add new confirmed-dead identifiers here.
DEAD_SOURCE_IDENTIFIERS: set[str] = {
    "UC8wZnXY3hz3L9Nf3q7v6RgA",  # "AI Explained" - YouTube: channel does not exist
    "https://openai.com/feed.xml",  # 403 Forbidden
    "https://medium.com/feed/@thomas-shu",  # 404
    "https://medium.com/feed/@analyticsvidhya",  # 404
    "https://medium.com/feed/@machinelearningworld",  # 404
    "https://medium.com/@dev_shivam_thakur",  # 403 (wrong URL format)
}


class IngestionSourceService:
    """Manage ingestion_sources rows with enterprise patterns."""

    def __init__(self, db: Session):
        self._db = db

    def list_sources(self, active_only: bool = False) -> list[IngestionSource]:
        """List all sources, optionally filtered to active only."""
        q = self._db.query(IngestionSource).order_by(
            IngestionSource.source_type, IngestionSource.display_name
        )
        if active_only:
            q = q.filter(IngestionSource.is_active.is_(True))
        return q.all()

    def get_by_id(self, source_id: int) -> IngestionSource | None:
        """Get a source by ID."""
        return self._db.query(IngestionSource).filter(IngestionSource.id == source_id).first()

    def get_active_rss(self) -> list[IngestionSource]:
        """Get all active RSS sources."""
        return (
            self._db.query(IngestionSource)
            .filter(
                IngestionSource.is_active.is_(True),
                IngestionSource.source_type == SourceType.RSS.value,
            )
            .all()
        )

    def get_active_youtube(self) -> list[IngestionSource]:
        """Get all active YouTube sources."""
        return (
            self._db.query(IngestionSource)
            .filter(
                IngestionSource.is_active.is_(True),
                IngestionSource.source_type == SourceType.YOUTUBE.value,
            )
            .all()
        )

    def get_active_medium(self) -> list[IngestionSource]:
        """Get all active Medium sources."""
        return (
            self._db.query(IngestionSource)
            .filter(
                IngestionSource.is_active.is_(True),
                IngestionSource.source_type == SourceType.MEDIUM.value,
            )
            .all()
        )

    def sync_defaults(self) -> dict[str, Any]:
        """Upsert rows from `default_sources` (idempotent).

        Syncs RSS feeds, YouTube channels, and Medium sources from the
        default configuration. Uses batch queries for better performance.
        """
        created = 0
        updated = 0
        medium_created = 0

        # Build a set of all identifiers to check in a single query
        all_identifiers = []
        for urls in DEFAULT_RSS_FEEDS.values():
            all_identifiers.extend(urls)
        for channel_id, _ in DEFAULT_YOUTUBE_CHANNELS:
            all_identifiers.append(channel_id)
        for url, _ in DEFAULT_MEDIUM_SOURCES:
            all_identifiers.append(url)

        # Fetch all existing sources in a single query
        existing_sources = {
            row.identifier: row
            for row in self._db.query(IngestionSource)
            .filter(IngestionSource.identifier.in_(all_identifiers))
            .all()
        }

        # Sync RSS feeds
        for display_name, urls in DEFAULT_RSS_FEEDS.items():
            for url in urls:
                row = existing_sources.get(url)
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
                            status=SourceStatus.ACTIVE,
                        )
                    )
                    created += 1

        # Sync YouTube channels
        for channel_id, display_name in DEFAULT_YOUTUBE_CHANNELS:
            row = existing_sources.get(channel_id)
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
                        status=SourceStatus.ACTIVE,
                    )
                )
                created += 1

        # Sync Medium sources
        for url, display_name in DEFAULT_MEDIUM_SOURCES:
            row = existing_sources.get(url)
            if row:
                if row.display_name != display_name or not row.is_active:
                    row.display_name = display_name
                    row.is_active = True
                    updated += 1
            else:
                self._db.add(
                    IngestionSource(
                        source_type=SourceType.MEDIUM.value,
                        display_name=display_name,
                        identifier=url,
                        is_active=True,
                        status=SourceStatus.ACTIVE,
                    )
                )
                created += 1
                medium_created += 1

        # Deactivate any previously-seeded sources that are now confirmed dead
        # (e.g. 404/403 feeds, deleted YouTube channels). sync_defaults only
        # upserts/activates from defaults, so without this step stale rows would
        # keep being polled forever.
        deactivated = 0
        if DEAD_SOURCE_IDENTIFIERS:
            dead_rows = (
                self._db.query(IngestionSource)
                .filter(
                    IngestionSource.identifier.in_(DEAD_SOURCE_IDENTIFIERS),
                    IngestionSource.is_active.is_(True),
                )
                .all()
            )
            for row in dead_rows:
                row.is_active = False
                row.status = SourceStatus.INACTIVE
                deactivated += 1
            if dead_rows:
                self._db.commit()

        self._db.commit()
        logger.info(
            "Synced default ingestion sources: created=%s updated=%s deactivated=%s (medium=%s)",
            created,
            updated,
            deactivated,
            medium_created,
        )
        return {
            "created": created,
            "updated": updated,
            "rss_feed_urls": sum(len(u) for u in DEFAULT_RSS_FEEDS.values()),
            "youtube_channels": len(DEFAULT_YOUTUBE_CHANNELS),
            "medium_sources": medium_created,
        }

    def create(
        self,
        *,
        source_type: str,
        display_name: str,
        identifier: str,
        description: str | None = None,
        category: str | None = None,
        is_active: bool = True,
        fetch_interval_minutes: int = 60,
        priority: int = 0,
        max_items_per_fetch: int = 50,
    ) -> IngestionSource:
        """Create a new ingestion source."""
        valid_types = {SourceType.RSS.value, SourceType.YOUTUBE.value, SourceType.MEDIUM.value}
        if source_type not in valid_types:
            raise ValueError(f"source_type must be one of: {', '.join(valid_types)}")

        row = IngestionSource(
            source_type=source_type,
            display_name=display_name,
            identifier=identifier.strip(),
            description=description,
            category=category,
            is_active=is_active,
            status=SourceStatus.ACTIVE if is_active else SourceStatus.INACTIVE,
            fetch_interval_minutes=fetch_interval_minutes,
            priority=priority,
            max_items_per_fetch=max_items_per_fetch,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def update(self, source_id: int, **fields: Any) -> IngestionSource | None:
        """Update an ingestion source."""
        row = self._db.query(IngestionSource).filter(IngestionSource.id == source_id).first()
        if not row:
            return None

        for key, value in fields.items():
            if value is not None and hasattr(row, key):
                setattr(row, key, value)

        # Update status based on is_active if provided
        if "is_active" in fields:
            row.status = SourceStatus.ACTIVE if fields["is_active"] else SourceStatus.INACTIVE

        self._db.commit()
        self._db.refresh(row)
        return row

    def delete(self, source_id: int) -> bool:
        """Delete an ingestion source."""
        row = self._db.query(IngestionSource).filter(IngestionSource.id == source_id).first()
        if not row:
            return False
        self._db.delete(row)
        self._db.commit()
        return True

    def record_fetch(
        self,
        source_id: int,
        items_count: int = 0,
        error: str | None = None,
    ) -> None:
        """Record a fetch attempt for health tracking."""
        from datetime import UTC, datetime

        row = self._db.query(IngestionSource).filter(IngestionSource.id == source_id).first()
        if not row:
            return

        row.total_fetches += 1
        row.last_fetched_at = datetime.now(UTC)

        if error:
            row.consecutive_errors += 1
            row.last_error_at = datetime.now(UTC)
            row.last_error_message = error
            if row.consecutive_errors >= 5:
                row.status = SourceStatus.ERROR
        else:
            row.consecutive_errors = 0
            row.total_items_fetched += items_count
            row.status = SourceStatus.ACTIVE
            row.last_error_message = None

        self._db.commit()
