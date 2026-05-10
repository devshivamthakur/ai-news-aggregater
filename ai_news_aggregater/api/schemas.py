"""Pydantic schemas for the HTTP API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=512)

    @field_validator("name")
    @classmethod
    def name_stripped(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Name is required")
        return s


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str | None
    digest_subscribed: bool
    interests: list[str] | None = None


class SubscriptionUpdate(BaseModel):
    digest_subscribed: bool
