from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.api.schemas import (
    SourceCreate,
    SourceHealthOut,
    SourceOut,
    SourcePatch,
    SyncDefaultsResult,
)
from app.models import IngestionSource
from app.services.ingestion_source_service import IngestionSourceService
from app.storage.cache import cached, invalidate_on_update

router = APIRouter()


@router.get("/sources", response_model=list[SourceOut], tags=["sources"])
@cached("sources")
def list_sources(
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = Query(False),
) -> list[SourceOut]:
    """List all ingestion sources."""
    return IngestionSourceService(db).list_sources(active_only=active_only)


@router.get("/sources/{source_id}", response_model=SourceOut, tags=["sources"])
@cached("source_by_id")
def get_source(
    source_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> SourceOut:
    """Get a specific source by ID."""
    svc = IngestionSourceService(db)
    row = svc.get_by_id(source_id)
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceOut.model_validate(row)


@router.post(
    "/sources",
    response_model=SourceOut,
    tags=["sources"],
    dependencies=[Depends(require_admin)],
)
@invalidate_on_update("sources", "source_by_id", "sources_health")
def create_source(
    body: SourceCreate,
    db: Annotated[Session, Depends(get_db)],
) -> SourceOut:
    """Create a new ingestion source (admin only)."""
    svc = IngestionSourceService(db)
    try:
        row = svc.create(
            source_type=body.source_type,
            display_name=body.display_name,
            identifier=body.identifier,
            description=body.description,
            category=body.category,
            is_active=body.is_active,
            fetch_interval_minutes=body.fetch_interval_minutes,
            priority=body.priority,
            max_items_per_fetch=body.max_items_per_fetch,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail="Source already exists for this type and identifier",
        ) from e
    return SourceOut.model_validate(row)


@router.patch(
    "/sources/{source_id}",
    response_model=SourceOut,
    tags=["sources"],
    dependencies=[Depends(require_admin)],
)
@invalidate_on_update("sources", "source_by_id", "sources_health")
def patch_source(
    source_id: int,
    body: SourcePatch,
    db: Annotated[Session, Depends(get_db)],
) -> SourceOut:
    """Update an ingestion source (admin only)."""
    svc = IngestionSourceService(db)
    row = svc.update(
        source_id,
        display_name=body.display_name,
        identifier=body.identifier,
        description=body.description,
        category=body.category,
        is_active=body.is_active,
        fetch_interval_minutes=body.fetch_interval_minutes,
        priority=body.priority,
        max_items_per_fetch=body.max_items_per_fetch,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceOut.model_validate(row)


@router.delete(
    "/sources/{source_id}",
    status_code=204,
    tags=["sources"],
    dependencies=[Depends(require_admin)],
)
@invalidate_on_update("sources", "source_by_id", "sources_health")
def delete_source(
    source_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete an ingestion source (admin only)."""
    svc = IngestionSourceService(db)
    row = svc.delete(source_id)
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")


@router.post(
    "/sources/sync-defaults",
    response_model=SyncDefaultsResult,
    tags=["sources"],
    dependencies=[Depends(require_admin)],
)
@invalidate_on_update("sources", "source_by_id", "sources_health")
def sync_default_sources(db: Annotated[Session, Depends(get_db)]) -> SyncDefaultsResult:
    """Sync default sources from configuration (admin only)."""
    stats = IngestionSourceService(db).sync_defaults()
    return SyncDefaultsResult(
        created=stats["created"],
        updated=stats["updated"],
        rss_feed_urls=stats["rss_feed_urls"],
        youtube_channels=stats["youtube_channels"],
        medium_sources=stats.get("medium_sources", 0),
    )


@router.get(
    "/sources/health",
    response_model=list[SourceHealthOut],
    tags=["sources"],
    dependencies=[Depends(require_admin)],
)
@cached("sources_health")
def sources_health(
    db: Annotated[Session, Depends(get_db)],
) -> list[SourceHealthOut]:
    """Get health status of all sources (admin only)."""
    sources = db.query(IngestionSource).all()
    return [
        SourceHealthOut(
            id=s.id,
            display_name=s.display_name,
            source_type=s.source_type,
            status=s.status.value if hasattr(s.status, 'value') else str(s.status),
            last_fetched_at=s.last_fetched_at,
            last_error_at=s.last_error_at,
            consecutive_errors=s.consecutive_errors,
            total_fetches=s.total_fetches,
            total_items_fetched=s.total_items_fetched,
        )
        for s in sources
    ]
