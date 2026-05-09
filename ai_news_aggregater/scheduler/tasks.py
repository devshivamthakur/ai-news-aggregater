from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from ai_news_aggregater.logging.logger import logger
from ai_news_aggregater.config.settings import settings
from datetime import datetime

def run_daily_aggregation():
    """Run the daily news aggregation and emailing."""
    logger.info(f"Starting daily aggregation at hour {settings.custom_fetch_hour}...")
    logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Import and call the main aggregation function
    from ai_news_aggregater.main import aggregate_and_email
    aggregate_and_email()

def start_scheduler():
    """Start the scheduler for daily runs at custom hour."""
    scheduler = BlockingScheduler()
    
    # Run daily at the custom hour (0-23 format)
    scheduler.add_job(
        run_daily_aggregation,
        CronTrigger(hour=settings.custom_fetch_hour)
    )
    
    hour_display = f"{settings.custom_fetch_hour:02d}:00"
    logger.info(f"Scheduler started. Running daily at {hour_display} UTC.")
    logger.info(f"Configured fetch hour: {settings.custom_fetch_hour} (24-hour format)")
    
    scheduler.start()