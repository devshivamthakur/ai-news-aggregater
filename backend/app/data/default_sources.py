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
    "Google AI Blog": [
        "https://blog.google/technology/ai/rss/",
    ],
    "DeepMind Blog": [
        "https://deepmind.google/blog/rss.xml",
    ],
    "Hugging Face Blog": [
        "https://huggingface.co/blog/feed.xml",
    ],
    "MIT News - AI": [
        "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml",
    ],
}

# YouTube channel IDs (channel_id, display_name)
DEFAULT_YOUTUBE_CHANNELS: list[tuple[str, str]] = [
    ("UCn8ujwUInbJkBhffxqAPBVQ", "Two Minute Papers"),
    ("UCSWj8mqQCcrcBlXPi4ThRDQ", "Yannic Kilcher"),
    ("UCiOq7YZ5_4VIqZ0RxBzC-_Q", "Lex Fridman"),
    ("UCbfYPyITQ-7l4upoX8nvctg", "Two Minute Papers Alt"),
    ("UC4JX40jDee_tINbkjycV4Sg", "Tech With Tim"),
    ("UC8wZnXY3hz3L9Nf3q7v6RgA", "AI Explained"),
]

# Medium publication/tag RSS feeds
# Medium provides RSS feeds at https://medium.com/feed/@{username} or https://medium.com/feed/{publication-name}
DEFAULT_MEDIUM_SOURCES: list[tuple[str, str]] = [
    ("https://medium.com/feed/@thomas-shu", "Thomas Shu"),
    ("https://medium.com/feed/@towardsdatascience", "Towards Data Science"),
    ("https://medium.com/feed/@analyticsvidhya", "Analytics Vidhya"),
    ("https://medium.com/feed/@machinelearningworld", "Machine Learning World"),
    ("https://medium.com/@dev_shivam_thakur", "Dev Shivam Thakur"),
]
