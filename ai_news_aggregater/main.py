import asyncio

from dotenv import load_dotenv

from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.core.pipeline import aggregate_and_email
from ai_news_aggregater.logging.logger import logger

load_dotenv()


def main():
    """CLI / cron entry: run one aggregation cycle."""
    logger.info("AI News Aggregator starting...")
    logger.info("Configured fetch hour: %s (24-hour format)", settings.custom_fetch_hour)
    asyncio.run(aggregate_and_email())

if __name__ == "__main__":
    main()
