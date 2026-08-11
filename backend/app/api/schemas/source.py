from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SourceCreate(BaseModel):
    source_type: str = Field(pattern="^(rss|youtube|medium|twitter|reddit|podcast)$")
    display_name: str = Field(min_length=1, max_length=512)
    identifier: str = Field(min_length=1, max_length=2048)
    description: str | None = None
    category: str | None = None
    is_active: bool = True
    fetch_interval_minutes: int = Field(default=60, ge=5, le=1440)
    priority: int = Field(default=0, ge=0, le=100)
    max_items_per_fetch: int = Field(default=50, ge=1, le=200)


class SourcePatch(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=512)
    identifier: str | None = Field(None, min_length=1, max_length=2048)
    description: str | None = None
    category: str | None = None
    is_active: bool | None = None
    fetch_interval_minutes: int | None = Field(None, ge=5, le=1440)
    priority: int | None = Field(None, ge=0, le=100)
    max_items_per_fetch: int | None = Field(None, ge=1, le=200)


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: str
    display_name: str
    identifier: str
    description: str | None = None
    category: str | None = None
    status: str
    is_active: bool
    fetch_interval_minutes: int
    priority: int
    max_items_per_fetch: int
    last_fetched_at: datetime | None = None
    last_error_at: datetime | None = None
    consecutive_errors: int
    total_fetches: int
    total_items_fetched: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SourceHealthOut(BaseModel):
    id: int
    display_name: str
    source_type: str
    status: str
    last_fetched_at: datetime | None = None
    last_error_at: datetime | None = None
    consecutive_errors: int
    total_fetches: int
    total_items_fetched: int


class SyncDefaultsResult(BaseModel):
    created: int
    updated: int
    rss_feed_urls: int
    youtube_channels: int
    medium_sources: int
