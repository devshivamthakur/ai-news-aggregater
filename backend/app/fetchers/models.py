from datetime import datetime

from pydantic import BaseModel


class NewsArticle(BaseModel):
    """Standard model for news articles across all sources."""
    title: str
    content: str
    url: str
    published_at: datetime
    source: str
    category: str | None = None


class BlogPost(BaseModel):
    """Model for blog posts from RSS feeds."""
    title: str
    content: str
    url: str
    published_at: datetime
    source: str
    summary: str | None = None


class Transcript(BaseModel):
    """Model for YouTube video transcript."""
    text: str


class ChannelVideo(BaseModel):
    """Model for YouTube channel videos with optional transcript."""
    title: str
    url: str
    video_id: str
    published_at: datetime
    description: str
    transcript: str | None = None
    source: str = "YouTube"


class WebContent(BaseModel):
    """Model for web page content."""
    title: str
    content: str
    url: str
    published_at: datetime
    source: str

