"""Pydantic schemas for the HTTP API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SourceCreate(BaseModel):
    source_type: str = Field(pattern="^(rss|youtube)$")
    display_name: str = Field(min_length=1, max_length=512)
    identifier: str = Field(min_length=1, max_length=2048)
    is_active: bool = True


class SourcePatch(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=512)
    identifier: str | None = Field(None, min_length=1, max_length=2048)
    is_active: bool | None = None


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: str
    display_name: str
    identifier: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SyncDefaultsResult(BaseModel):
    created: int
    updated: int
    rss_feed_urls: int
    youtube_channels: int


class JobAccepted(BaseModel):
    status: str = "accepted"
    detail: str


class HealthOut(BaseModel):
    status: str
    environment: str
    scheduler_enabled: bool


class NewsOut(BaseModel):
    id: int
    title: str
    summary: str | None
    category: str | None
    source: str | None
    url: str
    news_type: str
