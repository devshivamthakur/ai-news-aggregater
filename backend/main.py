"""Main entry point for AI News Aggregator application."""

import sys

from app.services.aggregation_service import AggregationService
from app.services.user_service import UserService

from app.config.settings import settings
from app.email.sender import EmailSender
from app.fetchers.blog_fetcher import RSSFeedScraper
from app.fetchers.video_fetcher import YouTubeScraper
from app.fetchers.web_fetcher import WebScraper
from app.logging.logger import logger
from app.storage.db import SessionLocal, create_tables
from app.utils.container import setup_container


def initialize_database():
    """Initialize database tables."""
    logger.info("Initializing database...")
    create_tables()
    logger.info("Database initialized successfully")


def initialize_container():
    """Initialize dependency injection container."""
    logger.info("Initializing service container...")
    db = SessionLocal()
    setup_container(db, settings)
    logger.info("Service container initialized")


def fetch_and_store_articles():
    """Fetch articles from all sources and store them."""
    logger.info("Starting article fetch cycle...")

    db = SessionLocal()
    aggregation_service = AggregationService(db)

    try:
        # Initialize fetchers
        web_scraper = WebScraper(
            timeout=settings.fetcher.timeout,
            max_retries=settings.fetcher.max_retries
        )
        rss_scraper = RSSFeedScraper(
            timeout=settings.fetcher.timeout,
            max_retries=settings.fetcher.max_retries
        )
        video_scraper = YouTubeScraper(
            timeout=settings.fetcher.timeout,
            max_retries=settings.fetcher.max_retries
        )

        # Fetch from each source and process
        sources = [
            ('web_scraper', web_scraper, 'Web Content'),
            ('rss_scraper', rss_scraper, 'Blog Posts'),
            ('video_scraper', video_scraper, 'YouTube Videos'),
        ]

        total_stats = {'created': 0, 'skipped': 0, 'errors': 0}

        for _source_name, fetcher, source_label in sources:
            try:
                articles = fetcher.fetch() if hasattr(fetcher, 'fetch') else []

                if articles:
                    stats = aggregation_service.process_fetched_articles(articles, source_label)
                    for key in total_stats:
                        total_stats[key] += stats[key]
                    logger.info(f"{source_label} processing: {stats}")
            except Exception as e:
                logger.error(f"Error fetching from {source_label}: {e}")
                total_stats['errors'] += 1

        logger.info(f"Fetch cycle complete. Total: {total_stats}")
        return total_stats

    except Exception as e:
        logger.error(f"Error in fetch_and_store_articles: {e}")
        raise
    finally:
        db.close()


def send_digests():
    """Send personalized news digests to active users."""
    logger.info("Starting digest sending cycle...")

    db = SessionLocal()
    user_service = UserService(db)
    aggregation_service = AggregationService(db)
    email_sender = EmailSender()

    try:
        users = user_service.get_active_users()
        logger.info(f"Found {len(users)} active users to send digests")

        sent_count = 0
        failed_count = 0

        for user in users:
            try:
                # Get personalized digest
                digest = aggregation_service.get_personalized_digest(user.email, limit=5)

                if digest and digest['articles']:
                    # Prepare articles for email
                    email_articles = [
                        {
                            'title': article.title,
                            'summary': article.summary or article.content[:200],
                            'url': article.url,
                            'source': article.source,
                            'category': article.category,
                        }
                        for article in digest['articles']
                    ]

                    # Send email
                    success = email_sender.send_news_digest(
                        user_email=user.email,
                        user_name=user.name or user.email.split('@')[0],
                        articles=email_articles,
                        user_interests=user.interests or [],
                    )

                    if success:
                        sent_count += 1
                        logger.info(f"Digest sent to {user.email}")
                    else:
                        failed_count += 1
                else:
                    logger.warning(f"No articles found for digest to {user.email}")

            except Exception as e:
                logger.error(f"Error sending digest to {user.email}: {e}")
                failed_count += 1

        logger.info(f"Digest sending complete: {sent_count} sent, {failed_count} failed")
        return {'sent': sent_count, 'failed': failed_count}

    except Exception as e:
        logger.error(f"Error in send_digests: {e}")
        raise
    finally:
        db.close()


def main():
    """Main application entry point."""
    logger.info("=" * 80)
    logger.info("AI News Aggregator Starting")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Fetch hour: {settings.custom_fetch_hour}")
    logger.info("=" * 80)

    try:
        # Initialize application
        initialize_database()
        initialize_container()

        # Run aggregation cycle
        fetch_and_store_articles()

        # Send digests
        send_digests()

        logger.info("Application completed successfully")

    except Exception as e:
        logger.critical(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
