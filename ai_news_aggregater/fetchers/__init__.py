from ai_news_aggregater.fetchers.web_fetcher import (
    WebScraper,
    fetch_web_content,
    fetch_medium_post,
    fetch_website_content,
)
from ai_news_aggregater.fetchers.blog_fetcher import (
    RSSFeedScraper
)
from ai_news_aggregater.fetchers.video_fetcher import (
    YouTubeScraper,
)
from ai_news_aggregater.fetchers.models import (
    NewsArticle,
    BlogPost,
    ChannelVideo,
    WebContent,
    Transcript,
)

__all__ = [
    # Classes
    "WebScraper",
    "RSSFeedScraper",
    "YouTubeScraper",
    # Web Scraper Functions
    "fetch_web_content",
    "fetch_medium_post",
    "fetch_website_content",
    # Blog Scraper Functions
    "fetch_openai_blog",
    "fetch_anthropic_blog",
    "fetch_google_ai_blog",
    "fetch_deepmind_blog",
    "fetch_all_blogs",
    "fetch_generic_blog",
    # Video Scraper Functions
    "fetch_video_transcript",
    "fetch_channel_videos",
    "scrape_youtube_channel",
    # Models
    "NewsArticle",
    "BlogPost",
    "ChannelVideo",
    "WebContent",
    "Transcript",
]
