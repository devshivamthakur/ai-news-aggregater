from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminStatsOut(BaseModel):
    total_users: int
    active_users: int
    suspended_users: int
    total_admins: int
    subscribed_users: int
    total_news_items: int
    pending_news_items: int
    analyzed_news_items: int
    total_sources: int
    active_sources: int
    error_sources: int
    total_fetches: int
    total_items_fetched: int
    news_today: int
    news_this_week: int


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    # Plain str: output schemas must serialize whatever is in the DB.
    # Strict EmailStr re-validation rejects valid local/dev domains
    # (e.g. `shivam@ainews.local`) and 500s the admin users endpoint.
    email: str
    name: str | None = None
    role: str
    status: str
    is_active: bool
    digest_subscribed: bool
    last_login_at: datetime | None = None
    created_at: datetime


class AdminUserUpdate(BaseModel):
    role: str | None = None
    status: str | None = None
    digest_subscribed: bool | None = None
