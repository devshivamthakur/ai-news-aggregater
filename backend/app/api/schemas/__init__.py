"""API schema exports for request/response validation."""

# Admin schemas
from .admin import AdminStatsOut, AdminUserOut, AdminUserUpdate

# Auth schemas
from .auth import (
    LocalEmailStr,
    PasswordChange,
    RefreshTokenIn,
    SubscriptionUpdate,
    TokenPairOut,
    UserLogin,
    UserMeOut,
    UserRegister,
    UserUpdate,
)

# Category schemas
from .category import CategoryCreate, CategoryOut, CategoryPatch

# Health schemas
from .health import HealthOut

# Job schemas
from .job import JobAccepted, JobStatusOut

# News schemas
from .news import NewsListOut, NewsOut, NewsSearchParams

# Source schemas
from .source import (
    SourceCreate,
    SourceHealthOut,
    SourceOut,
    SourcePatch,
    SyncDefaultsResult,
)

__all__ = [
    # Admin
    "AdminStatsOut",
    "AdminUserOut",
    "AdminUserUpdate",
    # Auth
    "LocalEmailStr",
    "PasswordChange",
    "RefreshTokenIn",
    "SubscriptionUpdate",
    "TokenPairOut",
    "UserLogin",
    "UserMeOut",
    "UserRegister",
    "UserUpdate",
    # Category
    "CategoryCreate",
    "CategoryOut",
    "CategoryPatch",
    # Health
    "HealthOut",
    # Job
    "JobAccepted",
    "JobStatusOut",
    # News
    "NewsListOut",
    "NewsOut",
    "NewsSearchParams",
    # Source
    "SourceCreate",
    "SourceHealthOut",
    "SourceOut",
    "SourcePatch",
    "SyncDefaultsResult",
]
