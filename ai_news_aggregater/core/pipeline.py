"""End-to-end aggregation: fetch from DB-configured sources, analyze, store, email."""

from __future__ import annotations

from datetime import datetime

from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.email.sender import email_sender
from ai_news_aggregater.fetchers.blog_fetcher import rss_scraper
from ai_news_aggregater.fetchers.models import BlogPost, ChannelVideo
from ai_news_aggregater.fetchers.video_fetcher import youtube_scraper
from ai_news_aggregater.logging.logger import logger
from ai_news_aggregater.models import NewsType
from ai_news_aggregater.processors.ContentAnalyzer import ContentAnalyzerInstance
from ai_news_aggregater.services.ingestion_source_service import IngestionSourceService
from ai_news_aggregater.storage.crud import NewsService
from ai_news_aggregater.storage.db import SessionLocal, create_tables


async def aggregate_and_email() -> None:
    """Fetch news from all active DB sources, analyze, persist, and notify users."""
    create_tables()
    db = SessionLocal()
    try:
        current_hour = datetime.utcnow().hour
        current_time = datetime.utcnow()
        lookback = settings.aggregation_lookback_hours
        per_feed_limit = settings.aggregation_rss_per_feed_limit

        logger.info("Starting news aggregation at hour %02d:00 UTC (lookback=%sh)", current_hour, lookback)

        source_svc = IngestionSourceService(db)
        rss_rows = source_svc.get_active_rss()
        yt_rows = source_svc.get_active_youtube()

        if not rss_rows and not yt_rows:
            logger.warning("No active ingestion sources in database. Run POST /api/v1/sources/sync-defaults or add sources.")
            return

        all_news: list[BlogPost | ChannelVideo] = []

        try:
            for src in rss_rows:
                posts = rss_scraper.fetch_feed(src.identifier, src.display_name, hours=lookback, limit=per_feed_limit)
                all_news.extend(posts)
            logger.info("Fetched %s blog posts from %s RSS source rows", len(all_news), len(rss_rows))
        except Exception as e:
            logger.error("Failed to fetch blog posts: %s", e)

        n_blog = len(all_news)

        try:
            for src in yt_rows:
                channel_videos = youtube_scraper.scrape_channel(src.identifier, hours=lookback)
                for v in channel_videos:
                    all_news.append(v.model_copy(update={"source": src.display_name}))
            logger.info("Fetched %s YouTube items from %s channel rows", len(all_news) - n_blog, len(yt_rows))
        except Exception as e:
            logger.error("Failed to fetch YouTube videos: %s", e)

        logger.info("Total fetched items: %s", len(all_news))

        stored_news = []
        for news_item in all_news:
            try:
                body = news_item.content if isinstance(news_item, BlogPost) else (news_item.transcript or news_item.description or "")
                result = await ContentAnalyzerInstance.process_content(
                    title=news_item.title,
                    content=body,
                )
                news_type = NewsType.VIDEO if isinstance(news_item, ChannelVideo) else NewsType.ARTICLE
                news_record = NewsService.create_news(
                    db=db,
                    title=news_item.title,
                    content=body,
                    summary=result.summary if result else "",
                    category=result.category if result else "",
                    source=news_item.source,
                    url=news_item.url,
                    published_at=news_item.published_at if hasattr(news_item, "published_at") else datetime.utcnow(),
                    news_type=news_type,
                    fetch_hour=current_hour,
                    fetch_date=current_time,
                )
                if news_record:
                    stored_news.append(news_record)
                    logger.info("Stored news: %s...", news_record.title[:50])
            except Exception as e:
                logger.error("Failed to process news: %s", e)

        logger.info("Stored %s news items", len(stored_news))

        from ai_news_aggregater.models import User

        users = db.query(User).all()

        for user in users:
            try:
                user_interests = user.interests or []
                user_news = []

                for news_item in stored_news:
                    if news_item.category in user_interests or not user_interests:
                        user_news.append(
                            {
                                "title": news_item.title,
                                "summary": news_item.summary,
                                "url": news_item.url,
                                "category": news_item.category,
                                "source": news_item.source,
                                "news_type": news_item.news_type.value,
                            }
                        )

                if user_news:
                    logger.info("Sending %s news items to %s", len(user_news), user.email)
                    email_sender.send_news_digest(
                        user_email=user.email,
                        user_name=user.name or user.email.split("@")[0],
                        articles=user_news,
                        user_interests=user_interests,
                    )
                else:
                    logger.info("No matching news for user %s", user.email)

            except Exception as e:
                logger.error("Failed to send email to %s: %s", user.email, e)

        logger.info("News aggregation completed successfully")

    except Exception as e:
        logger.error("Failed to aggregate and email news: %s", e)
        raise
    finally:
        db.close()
