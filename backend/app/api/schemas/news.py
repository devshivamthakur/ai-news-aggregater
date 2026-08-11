from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NewsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None = None
    category: str | None = None
    source: str | None = None
    source_url: str | None = None
    url: str
    image_url: str | None = None
    author: str | None = None
    news_type: str
    status: str
    sentiment_score: float | None = None
    keywords: str | None = None
    reading_time_minutes: int | None = None
    language: str
    published_at: datetime | None = None
    created_at: datetime


class NewsListOut(BaseModel):
    items: list[NewsOut]
    total: int
    page: int
    page_size: int
    has_next: bool


class NewsSearchParams(BaseModel):
    q: str | None = None
    category: str | None = None
    source: str | None = None
    news_type: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
