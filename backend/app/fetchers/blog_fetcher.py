import re
from datetime import datetime, timedelta

import feedparser

from app.config.settings import settings
from app.fetchers.models import BlogPost
from app.logging.logger import logger
from app.utils.errors import retry_on_failure


class RSSFeedScraper:
    """Fetch and parse content from RSS feeds."""

    def __init__(self):
        """Initialize RSS feed scraper."""
        # Configurable via FETCHER_TIMEOUT; guards against a single slow feed
        # hanging a worker thread (and therefore the whole aggregation run).
        self.timeout = settings.fetcher.timeout

    @retry_on_failure(max_retries=3, delay=2.0)
    def fetch_feed(
        self,
        rss_url: str,
        source_name: str,
        hours: int = 24,
        limit: int = 20,
    ) -> list[BlogPost]:
        """Fetch blog posts from a single RSS feed.

        Args:
            rss_url: URL of the RSS feed
            source_name: Name of the source
            hours: Only return posts from last N hours
            limit: Maximum number of posts to return
        """
        try:
            logger.info(f"Fetching RSS from {source_name}: {rss_url}")
            feed = feedparser.parse(rss_url, request_timeout=self.timeout)

            if feed.bozo:
                logger.warning(f"RSS feed malformed for {source_name}: {feed.bozo_exception}")

            posts = []
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            for entry in feed.entries[:limit]:
                try:
                    # Extract published date
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])
                    else:
                        published_at = datetime.utcnow()

                    # Skip old posts
                    if published_at < cutoff_time:
                        logger.debug(
                            "Skipping old post from %s: %s",
                            source_name,
                            entry.get('title', 'Untitled')[:50],
                        )
                        continue

                    # Extract content
                    content = entry.get('summary', entry.get('description', ''))
                    if isinstance(content, str):
                        # Remove HTML tags
                        content = re.sub(r'<[^>]+>', '', content)

                    url = entry.get('link', '')
                    if not url:
                        continue

                    post = BlogPost(
                        title=entry.get('title', 'Untitled'),
                        content=content[:2000],
                        url=url,
                        published_at=published_at,
                        source=source_name,
                        summary=entry.get('summary', '')[:500]
                    )
                    posts.append(post)
                    logger.debug(f"Fetched: {post.title[:50]}...")

                except Exception as e:
                    logger.warning(f"Error parsing entry from {source_name}: {e}")
                    continue

            logger.info(f"Successfully fetched {len(posts)} posts from {source_name}")
            return posts

        except Exception as e:
            logger.error(f"Failed to fetch RSS from {source_name}: {e}")
            return []

    def fetch_multiple_feeds(self, feeds: dict, hours: int = 24, limit: int = 20) -> list[BlogPost]:
        """Fetch from multiple RSS feeds.

        Args:
            feeds: Dict of {source_name: [urls]} pairs
            hours: Only return posts from last N hours
            limit: Maximum posts per feed
        """
        all_posts = []
        for source_name, urls in feeds.items():
            if isinstance(urls, list):
                for url in urls:
                    posts = self.fetch_feed(url, source_name, hours, limit)
                    all_posts.extend(posts)
            else:
                posts = self.fetch_feed(urls, source_name, hours, limit)
                all_posts.extend(posts)
        return all_posts

# Initialize scraper
rss_scraper = RSSFeedScraper()


# if __name__ == "__main__":
#     # Test fetching blogs
#     try:
#         openai_posts = fetch_openai_blog()
#         print(f"Fetched {len(openai_posts)} posts from OpenAI Blog")

#         anthropic_posts = fetch_anthropic_blog()
#         print(f"Fetched {len(anthropic_posts)} posts from Anthropic Blog")
#     except Exception as e:
#         logger.error(f"Blog fetching failed: {e}")
