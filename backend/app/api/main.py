"""FastAPI application factory and ASGI entrypoint."""

from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.auth_routes import router as auth_router
from app.api.rate_limit import limiter
from app.api.routes import router as api_router
from app.config.settings import settings
from app.core.pipeline import aggregate_and_email
from app.logging.logger import logger
from app.services.category_service import CategoryService
from app.services.ingestion_source_service import IngestionSourceService
from app.storage.db import SessionLocal, create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup (environment=%s)", settings.environment)
    create_tables()

    # Always sync default categories and sources on startup for complete out-of-the-box experience
    db = SessionLocal()
    try:
        CategoryService(db).sync_defaults()
        if settings.sync_default_sources_on_startup:
            IngestionSourceService(db).sync_defaults()
    except Exception:
        logger.exception("Failed to sync defaults on startup")
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
        version="2.1.0",
        lifespan=lifespan,
        openapi_url=None
    )

    # Bind the shared limiter so route-level @limiter.limit() decorators work.
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Apply the default per-route rate limit to every endpoint.
    if settings.rate_limit.enabled:
        application.add_middleware(SlowAPIMiddleware)

    # Harden responses with standard security headers.
    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=63072000; includeSubDomains; preload",
        )
        return response

    application.include_router(auth_router, prefix="/api/v1", tags=["auth"])
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
