"""End-to-end aggregation: fetch from DB-configured sources, analyze, store, email."""

from __future__ import annotations

import asyncio
from datetime import datetime

from app.config.settings import settings
from app.email.sender import email_sender
from app.fetchers.blog_fetcher import rss_scraper
from app.fetchers.models import BlogPost, ChannelVideo
from app.fetchers.video_fetcher import youtube_scraper
from app.logging.logger import logger
from app.models import NewsType
from app.processors.content_analyzer import ContentAnalyzerInstance
from app.services.ingestion_source_service import IngestionSourceService
from app.storage.crud import NewsService
from app.storage.cache import cache
from app.storage.db import SessionLocal, create_tables


async def _fetch_rss_feeds(
    rss_rows: list,
    lookback: int,
    per_feed_limit: int,
) -> list[BlogPost]:
    """Fetch all RSS feeds concurrently."""
    tasks = [
        asyncio.to_thread(
            rss_scraper.fetch_feed,
            src.identifier,
            src.display_name,
            hours=lookback,
            limit=per_feed_limit,
        )
        for src in rss_rows
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    posts: list[BlogPost] = []
    for result in results:
        if isinstance(result, Exception):
            logger.error("Failed to fetch RSS feed: %s", result)
        elif isinstance(result, list):
            posts.extend(result)
    return posts


async def _fetch_medium_feeds(
    medium_rows: list,
    lookback: int,
    per_feed_limit: int,
) -> list[BlogPost]:
    """Fetch all Medium feeds concurrently."""
    tasks = [
        asyncio.to_thread(
            rss_scraper.fetch_feed,
            src.identifier,
            src.display_name,
            hours=lookback,
            limit=per_feed_limit,
        )
        for src in medium_rows
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    posts: list[BlogPost] = []
    for result in results:
        if isinstance(result, Exception):
            logger.error("Failed to fetch Medium feed: %s", result)
        elif isinstance(result, list):
            posts.extend(result)
    return posts


async def _fetch_youtube_channels(
    yt_rows: list,
    lookback: int,
) -> list[ChannelVideo]:
    """Fetch all YouTube channels concurrently."""
    tasks = [
        asyncio.to_thread(
            youtube_scraper.scrape_channel,
            src.identifier,
            hours=lookback,
        )
        for src in yt_rows
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    videos: list[ChannelVideo] = []
    for src, result in zip(yt_rows, results, strict=False):
        if isinstance(result, Exception):
            logger.error("Failed to fetch YouTube channel: %s", result)
        elif isinstance(result, list):
            for v in result:
                videos.append(v.model_copy(update={"source": src.display_name}))
    return videos


async def _analyze_all_content(
    all_news: list[BlogPost | ChannelVideo],
) -> list[tuple[str, str, str] | BaseException]:
    """Analyze all news items as one parallel batch (instead of one-by-one)."""
    if not all_news:
        return []

    items = []
    for news_item in all_news:
        body = (
            news_item.content
            if isinstance(news_item, BlogPost)
            else (news_item.transcript or news_item.description or "")
        )
        items.append(
            (
                news_item.title,
                body,
            )
        )

    return await ContentAnalyzerInstance.process_batch(
        items,
        max_concurrency=settings.content_analyzer_max_concurrency,
    )


def _filter_new_items(
    all_news: list[BlogPost | ChannelVideo],
) -> list[BlogPost | ChannelVideo]:
    """Drop items whose URL already exists in the news table.

    Runs in its own thread (call via ``asyncio.to_thread``) with its own DB
    session so the event loop is never blocked. Checking before analysis means
    duplicates never waste an LLM call and the insert never trips the
    ``news_url_key`` unique constraint.
    """
    if not all_news:
        return []

    from app.models import News

    db = SessionLocal()
    try:
        urls = {item.url for item in all_news}
        existing_rows = (
            db.query(News.url)
            .filter(News.url.in_(list(urls)))
            .all()
        )
        existing_urls = {row[0] for row in existing_rows}
        if existing_urls:
            logger.info(
                "Skipping %s item(s) already in database (duplicate URLs)",
                len(existing_urls),
            )

        return [item for item in all_news if item.url not in existing_urls]
    finally:
        db.close()


def _get_active_source_rows() -> tuple[list, list, list]:
    """Sync helper: fetch active RSS / YouTube / Medium source rows.

    Runs in its own thread (call via ``asyncio.to_thread``) so the blocking
    DB queries never touch the event loop. Columns used by the fetchers
    (identifier, display_name) are eagerly loaded, so the detached rows are
    safe to use after the session closes.
    """
    db = SessionLocal()
    try:
        source_svc = IngestionSourceService(db)
        rss_rows = source_svc.get_active_rss()
        yt_rows = source_svc.get_active_youtube()
        medium_rows = source_svc.get_active_medium()
        return rss_rows, yt_rows, medium_rows
    finally:
        db.close()


def _store_news_items(
    all_news: list[BlogPost | ChannelVideo],
    analysis_results: list[tuple[str, str] | BaseException],
    current_hour: int,
    current_time: datetime,
) -> list:
    """Sync helper: persist analyzed items to the database.

    Runs in its own thread (call via ``asyncio.to_thread``) with its own DB
    session so the blocking per-item inserts never block the event loop.
    """
    if not all_news:
        return []

    db = SessionLocal()
    try:
        stored_news = []
        for news_item, analysis in zip(all_news, analysis_results, strict=False):
            try:
                if isinstance(analysis, BaseException):
                    logger.error("Failed to analyze news: %s", analysis)
                    continue
                summary, category = analysis
                body = (
                    news_item.content
                    if isinstance(news_item, BlogPost)
                    else (news_item.transcript or news_item.description or "")
                )
                news_type = (
                    NewsType.VIDEO
                    if isinstance(news_item, ChannelVideo)
                    else NewsType.ARTICLE
                )
                news_record = NewsService.create_news(
                    db=db,
                    title=news_item.title,
                    content=body,
                    summary=summary,
                    category=category,
                    source=news_item.source,
                    url=news_item.url,
                    published_at=(
                        news_item.published_at
                        if hasattr(news_item, "published_at")
                        else datetime.utcnow()
                    ),
                    news_type=news_type,
                    fetch_hour=current_hour,
                    fetch_date=current_time,
                )
                if news_record:
                    stored_news.append(news_record)
                    logger.info("Stored news: %s...", news_record.title[:50])
            except Exception as e:
                logger.error("Failed to process news: %s", e)

        # New articles were written: drop the cached news list / detail
        # responses so users see fresh content immediately instead of waiting
        # for the TTL to expire. Best-effort; a Redis outage must not fail the
        # aggregation run.
        if stored_news:
            try:
                cache.invalidate_cache("news_list")
                cache.invalidate_cache("news_by_id")
            except Exception as e:
                logger.warning("Failed to invalidate news cache: %s", e)

        return stored_news
    finally:
        db.close()


def _iter_digest_subscribers(page_size: int):
    """Yield digest subscribers in pages (keyset pagination by id).

    Pages keep memory flat no matter how many users exist, so 100k+ users are
    processed without ever loading them all into memory at once.
    """
    from app.models import User

    last_id = 0
    while True:
        db = SessionLocal()
        try:
            page = (
                db.query(User)
                .filter(
                    User.id > last_id,
                    User.is_active.is_(True),
                    User.digest_subscribed.is_(True),
                )
                .order_by(User.id)
                .limit(page_size)
                .all()
            )
        finally:
            db.close()

        if not page:
            return

        for user in page:
            yield user
        last_id = page[-1].id


def _group_news_by_category(stored_news: list) -> dict:
    """Index stored news by category for O(1) per-user interest filtering."""
    by_category: dict = {}
    for news_item in stored_news:
        by_category.setdefault(news_item.category, []).append(news_item)
    return by_category


async def _send_emails_to_users(
    users: list,
    stored_news: list,
) -> None:
    """Send emails to a batch of users concurrently, bounded by a semaphore.

    Each worker reuses a single SMTP connection for its slice of users so we
    never open more than ``digest_max_concurrency`` connections at once.
    """
    semaphore = asyncio.Semaphore(settings.digest_max_concurrency)
    news_by_category = _group_news_by_category(stored_news)

    async def _worker(user) -> None:
        async with semaphore:
            await asyncio.to_thread(_send_email_to_user, user, news_by_category)

    tasks = [_worker(user) for user in users]
    await asyncio.gather(*tasks, return_exceptions=True)


def _send_email_to_user(
    user,
    news_by_category: dict,
) -> None:
    """Send email to a single user, filtered to their interests.

    ``news_by_category`` is a pre-built category->items index so matching is
    O(interests) per user instead of O(total_news).
    """
    try:
        user_interests = user.interests or []
        if user_interests:
            matched = []
            for interest in user_interests:
                matched.extend(news_by_category.get(interest, []))
        else:
            matched = [n for items in news_by_category.values() for n in items]

        user_news = email_sender.build_digest_articles(matched, user_interests)

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


async def _deliver_digests(stored_news: list) -> None:
    """Deliver digests to all subscribers, paginated and concurrency-bounded.

    Subscribers are streamed from the DB in pages and processed in chunks so
    memory stays flat and SMTP connections are capped regardless of user count.
    """
    page_size = settings.digest_user_page_size
    batch_size = settings.digest_batch_size

    batch: list = []
    total_sent = 0
    async for user in _aiter(_iter_digest_subscribers(page_size)):
        batch.append(user)
        if len(batch) >= batch_size:
            await _send_emails_to_users(batch, stored_news)
            total_sent += len(batch)
            batch.clear()

    if batch:
        await _send_emails_to_users(batch, stored_news)
        total_sent += len(batch)

    logger.info("Digest delivery complete: %s subscriber(s) processed", total_sent)


async def _aiter(iterator):
    """Adapt a sync iterator into an async generator (yields without blocking)."""
    for item in iterator:
        yield item
        await asyncio.sleep(0)  # Allow event loop to breathe


async def aggregate_and_email() -> None:
    """Fetch news from all active DB sources, analyze, persist, and notify users.

    Every blocking operation (table creation, source queries, dedupe, inserts,
    user query, email sending) is offloaded to a worker thread via
    ``asyncio.to_thread`` so the event loop — and therefore the API server —
    is never blocked while aggregation runs.
    """
    await asyncio.to_thread(create_tables)
    try:
        current_hour = datetime.utcnow().hour
        current_time = datetime.utcnow()
        lookback = settings.aggregation_lookback_hours
        per_feed_limit = settings.aggregation_rss_per_feed_limit

        logger.info(
            "Starting news aggregation at hour %02d:00 UTC (lookback=%sh)",
            current_hour,
            lookback,
        )

        rss_rows, yt_rows, medium_rows = await asyncio.to_thread(
            _get_active_source_rows
        )

        if not rss_rows and not yt_rows and not medium_rows:
            logger.warning(
                "No active ingestion sources in database. "
                "Run POST /api/v1/sources/sync-defaults or add sources."
            )
            return

        # 1. Fetch all sources concurrently (each fetcher runs in a thread)
        rss_task = (
            _fetch_rss_feeds(rss_rows, lookback, per_feed_limit)
            if rss_rows
            else asyncio.sleep(0, result=[])
        )
        medium_task = (
            _fetch_medium_feeds(medium_rows, lookback, per_feed_limit)
            if medium_rows
            else asyncio.sleep(0, result=[])
        )
        youtube_task = (
            _fetch_youtube_channels(yt_rows, lookback)
            if yt_rows
            else asyncio.sleep(0, result=[])
        )

        all_rss, all_medium, all_youtube = await asyncio.gather(
            rss_task,
            medium_task,
            youtube_task,
        )

        all_news: list[BlogPost | ChannelVideo] = []
        all_news.extend(all_rss)
        all_news.extend(all_medium)
        all_news.extend(all_youtube)

        logger.info("Total fetched items: %s", len(all_news))

        # 2. Drop duplicates BEFORE analysis (threaded DB query) so we never
        #    waste LLM calls on articles that are already stored.
        all_news = await asyncio.to_thread(_filter_new_items, all_news)
        logger.info("New items after dedupe: %s", len(all_news))

        # 3. Analyze all new content as one parallel batch (async, non-blocking)
        analysis_results = await _analyze_all_content(all_news)

        # 4. Store news items (threaded per-item inserts)
        stored_news = await asyncio.to_thread(
            _store_news_items,
            all_news,
            analysis_results,
            current_hour,
            current_time,
        )
        logger.info("Stored %s news items", len(stored_news))

        # 5. Send emails to users (paginated + concurrency-bounded so 100k+
        #    subscribers are processed with flat memory and capped SMTP load)
        await _deliver_digests(stored_news)

        logger.info("News aggregation completed successfully")

    except Exception as e:
        logger.error("News aggregation failed: %s", e)
        raise
