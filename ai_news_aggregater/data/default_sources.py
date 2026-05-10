"""Canonical default ingestion sources used only by the sync service to populate the database."""

# Map display name -> list of RSS feed URLs
DEFAULT_RSS_FEEDS: dict[str, list[str]] = {
    "OpenAI Blog": [
        "https://openai.com/news/rss.xml",
        "https://openai.com/feed.xml",
    ],
    "Anthropic Blog": [
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
    ],
}

# YouTube channel IDs (optional label for display when syncing)
DEFAULT_YOUTUBE_CHANNELS: list[tuple[str, str]] = [
    ("UCn8ujwUInbJkBhffxqAPBVQ", "YouTube UCn8ujwU"),
    ("UCSWj8mqQCcrcBlXPi4ThRDQ", "YouTube UCSWj8mq"),
    ("UCiOq7YZ5_4VIqZ0RxBzC-_Q", "YouTube UCiOq7YZ"),
]
