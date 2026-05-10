"""Blocking scheduler for CLI-only / worker processes.

When running the FastAPI app (`ai_news_aggregater.api.main:app`), prefer the in-process
`AsyncIOScheduler` configured in the app lifespan instead of this module.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.core.pipeline import aggregate_and_email
from ai_news_aggregater.logging.logger import logger


def run_daily_aggregation() -> None:
    """Run the daily news aggregation and emailing."""
    logger.info("Starting daily aggregation at hour %s...", settings.scheduler.fetch_hour)
    logger.info("Timestamp: %s", datetime.utcnow().isoformat())
    asyncio.run(aggregate_and_email())


def start_scheduler() -> None:
    """Start the scheduler for daily runs at the configured local hour."""
    tz = ZoneInfo(settings.scheduler.timezone)
    scheduler = BlockingScheduler(timezone=tz)
    scheduler.add_job(
        run_daily_aggregation,
        CronTrigger(
            hour=settings.scheduler.fetch_hour,
            minute=0,
            second=0,
            timezone=tz,
        ),
        id="daily_news_aggregate_worker",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    logger.info(
        "Scheduler started. Daily run at %02d:00 %s",
        settings.scheduler.fetch_hour,
        settings.scheduler.timezone,
    )
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()
