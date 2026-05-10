"""FastAPI application factory and ASGI entrypoint."""

from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_news_aggregater.api.routes import router as api_router
from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.core.pipeline import aggregate_and_email
from ai_news_aggregater.logging.logger import logger
from ai_news_aggregater.services.ingestion_source_service import IngestionSourceService
from ai_news_aggregater.storage.db import SessionLocal, create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup (environment=%s)", settings.environment)
    create_tables()

    if settings.sync_default_sources_on_startup:
        db = SessionLocal()
        try:
            IngestionSourceService(db).sync_defaults()
        finally:
            db.close()

    scheduler: AsyncIOScheduler | None = None
    if settings.scheduler.enabled:
        tz = ZoneInfo(settings.scheduler.timezone)
        scheduler = AsyncIOScheduler(timezone=tz)

        async def scheduled_aggregate() -> None:
            try:
                await aggregate_and_email()
            except Exception:
                logger.exception("Scheduled aggregation failed")

        scheduler.add_job(
            scheduled_aggregate,
            CronTrigger(
                hour=settings.scheduler.fetch_hour,
                minute=0,
                second=0,
                timezone=tz,
            ),
            id="daily_news_aggregate",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()
        logger.info(
            "APScheduler: daily aggregate at %02d:00 %s",
            settings.scheduler.fetch_hour,
            settings.scheduler.timezone,
        )

    yield

    if scheduler:
        scheduler.shutdown(wait=False)
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    application = FastAPI(
        title="AI News Aggregator",
        version="1.0.0",
        lifespan=lifespan,
        openapi_url=None
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix="/api/v1")

    @application.get("/health", include_in_schema=False)
    def load_balancer_health() -> dict[str, str | bool]:
        return {
            "status": "ok",
            "environment": settings.environment,
            "scheduler_enabled": settings.scheduler.enabled,
        }

    return application


app = create_app()
