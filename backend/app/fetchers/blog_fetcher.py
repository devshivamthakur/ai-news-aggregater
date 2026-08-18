from datetime import UTC, datetime, timedelta

import feedparser

from app.fetchers.models import BlogPost
from app.logging.logger import logger


class RSSScraper:
    """Scrape RSS feeds and return a list of blog posts."""

    def fetch_feed(
        self,
        feed_url: str,
        source_name: str,
        hours: int = 24,
        limit: int = 100,
    ) -> list[BlogPost]:
        """Fetch RSS feed and return a list of posts from the last N hours."""
        logger.info("Fetching RSS from %s: %s", source_name, feed_url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        try:
            feed = feedparser.parse(feed_url, request_headers=headers)
            if feed.bozo:
                logger.warning(
                    "RSS feed malformed for %s: %s",
                    source_name,
                    feed.bozo_exception,
                )

            cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
            posts = []

            for entry in feed.entries:
                published_time = self._parse_published_time(entry)
                if published_time and published_time < cutoff_time:
                    logger.debug("Skipping old post: %s", entry.title)
                    continue

                image_url = self._extract_image_url(entry)
                content = self._extract_content(entry)
                author = self._extract_author(entry)

                post = BlogPost(
                    title=entry.title,
                    url=entry.link,
                    source=source_name,
                    author=author,
                    content=content,
                    published_at=published_time,
                    image_url=image_url,
                )
                posts.append(post)
                if len(posts) >= limit:
                    logger.info("Reached limit of %d posts for %s", limit, source_name)
                    break

            logger.info("Successfully fetched %d posts from %s", len(posts), source_name)
            return posts

        except Exception as e:
            logger.error(
                "Error fetching or parsing RSS feed for %s: %s",
                source_name,
                e,
            )
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

    def _parse_published_time(self, entry) -> datetime | None:
        """Parse the published time from a feed entry.

        Falls back through the common feedparser date fields and returns a
        timezone-aware UTC datetime, or None if no date is available.
        """
        for field in ("published_parsed", "updated_parsed", "created_parsed"):
            parsed = getattr(entry, field, None)
            if parsed:
                try:
                    return datetime(*parsed[:6], tzinfo=UTC)
                except (TypeError, ValueError):
                    continue

        for field in ("published", "updated", "created"):
            raw = getattr(entry, field, None)
            if raw:
                try:
                    return datetime.fromisoformat(raw.replace("Z", "+00:00"))
                except (TypeError, ValueError):
                    continue

        return None

    def _extract_image_url(self, entry) -> str | None:
        """Extract a representative image URL from a feed entry if present."""
        # RSS media thumbnail / enclosure
        media_thumbnail = getattr(entry, "media_thumbnail", None)
        if isinstance(media_thumbnail, list) and media_thumbnail:
            url = media_thumbnail[0].get("url")
            if url:
                return url

        media_content = getattr(entry, "media_content", None)
        if isinstance(media_content, list) and media_content:
            url = media_content[0].get("url")
            if url:
                return url

        enclosure = getattr(entry, "enclosure", None)
        if enclosure and getattr(enclosure, "type", "").startswith("image/"):
            return getattr(enclosure, "href", None)

        return None

    def _extract_content(self, entry) -> str:
        """Extract the main content/summary text from a feed entry."""
        content = getattr(entry, "content", None)
        if isinstance(content, list) and content:
            value = content[0].get("value")
            if value:
                return value

        summary = getattr(entry, "summary", None)
        if summary:
            return summary

        description = getattr(entry, "description", None)
        return description or ""

    def _extract_author(self, entry) -> str | None:
        """Extract the author name from a feed entry if present."""
        author = getattr(entry, "author", None)
        if author:
            return author

        authors = getattr(entry, "authors", None)
        if isinstance(authors, list) and authors:
            return authors[0].get("name") if isinstance(authors[0], dict) else str(authors[0])

        return None

# Initialize scraper
rss_scraper = RSSScraper()


# if __name__ == "__main__":
#     # Test fetching blogs
#     try:
#         openai_posts = fetch_openai_blog()
#         print(f"Fetched {len(openai_posts)} posts from OpenAI Blog")

#         anthropic_posts = fetch_anthropic_blog()
#         print(f"Fetched {len(anthropic_posts)} posts from Anthropic Blog")
#     except Exception as e:
#         logger.error(f"Blog fetching failed: {e}")
