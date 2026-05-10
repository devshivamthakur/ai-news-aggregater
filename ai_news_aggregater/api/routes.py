"""API route handlers."""

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ai_news_aggregater.api.auth_routes import router as auth_router
from ai_news_aggregater.api.deps import get_db, require_admin_key
from ai_news_aggregater.api.schemas import (
    HealthOut,
    JobAccepted,
    NewsOut,
    SourceCreate,
    SourceOut,
    SourcePatch,
    SyncDefaultsResult,
)
from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.core.pipeline import aggregate_and_email
from ai_news_aggregater.logging.logger import logger
from ai_news_aggregater.models import News
from ai_news_aggregater.services.ingestion_source_service import IngestionSourceService

router = APIRouter()
router.include_router(auth_router, prefix="/auth")


@router.get("/health", response_model=HealthOut, tags=["health"])
def health() -> HealthOut:
    return HealthOut(
        status="ok",
        environment=settings.environment,
        scheduler_enabled=settings.scheduler.enabled,
    )


@router.get("/sources", response_model=list[SourceOut], tags=["sources"])
def list_sources(
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = Query(False),
) -> list[SourceOut]:
    return IngestionSourceService(db).list_sources(active_only=active_only)


@router.post(
    "/sources",
    response_model=SourceOut,
    tags=["sources"],
    dependencies=[Depends(require_admin_key)],
)
def create_source(body: SourceCreate, db: Annotated[Session, Depends(get_db)]) -> SourceOut:
    svc = IngestionSourceService(db)
    try:
        row = svc.create(
            source_type=body.source_type,
            display_name=body.display_name,
            identifier=body.identifier,
            is_active=body.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="Source already exists for this type and identifier") from e
    return SourceOut.model_validate(row)


@router.patch(
    "/sources/{source_id}",
    response_model=SourceOut,
    tags=["sources"],
    dependencies=[Depends(require_admin_key)],
)
def patch_source(
    source_id: int,
    body: SourcePatch,
    db: Annotated[Session, Depends(get_db)],
) -> SourceOut:
    svc = IngestionSourceService(db)
    row = svc.update(
        source_id,
        display_name=body.display_name,
        identifier=body.identifier,
        is_active=body.is_active,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceOut.model_validate(row)


@router.post(
    "/sources/sync-defaults",
    response_model=SyncDefaultsResult,
    tags=["sources"],
    dependencies=[Depends(require_admin_key)],
)
def sync_default_sources(db: Annotated[Session, Depends(get_db)]) -> SyncDefaultsResult:
    stats = IngestionSourceService(db).sync_defaults()
    return SyncDefaultsResult(
        created=stats["created"],
        updated=stats["updated"],
        rss_feed_urls=stats["rss_feed_urls"],
        youtube_channels=stats["youtube_channels"],
    )


async def _aggregate_job() -> None:
    try:
        await aggregate_and_email()
    except Exception:
        logger.exception("Background aggregation job failed")


@router.post(
    "/jobs/aggregate",
    response_model=JobAccepted,
    tags=["jobs"],
    dependencies=[Depends(require_admin_key)],
)
async def trigger_aggregate() -> JobAccepted:
    """Schedule a full aggregation cycle (fetch → LLM → DB → email) on the app event loop."""
    asyncio.create_task(_aggregate_job())
    return JobAccepted(detail="Aggregation task scheduled on event loop")


@router.get("/news", response_model=list[NewsOut], tags=["news"])
def recent_news(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
) -> list[NewsOut]:
    rows = db.query(News).order_by(News.created_at.desc()).limit(limit).all()
    return [
        NewsOut(
            id=n.id,
            title=n.title,
            summary=n.summary,
            category=n.category,
            source=n.source,
            url=n.url,
            news_type=n.news_type.value,
        )
        for n in rows
    ]
