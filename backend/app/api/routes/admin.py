from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin, require_super_admin
from app.api.rate_limit import ADMIN_LIMIT, limiter
from app.api.schemas import (
    AdminStatsOut,
    AdminUserOut,
    AdminUserUpdate,
)
from app.models import IngestionSource, News, NewsStatus, SourceStatus, User, UserRole, UserStatus
from app.storage.cache import cache, cached, invalidate_on_update

router = APIRouter()


@router.post(
    "/admin/cache/flush",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)
@limiter.limit(ADMIN_LIMIT)
def admin_flush_cache(request: Request, response: Response) -> dict:
    """Flush the Redis response cache (admin only)."""
    deleted = cache.flush()
    return {"status": "ok", "deleted_keys": deleted}


@router.get(
    "/admin/stats",
    response_model=AdminStatsOut,
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)
@cached("admin_stats", ttl=60)  # Cache for 60 seconds
def admin_stats(db: Annotated[Session, Depends(get_db)]) -> AdminStatsOut:
    """Get comprehensive admin dashboard statistics."""
    today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    return AdminStatsOut(
        total_users=db.query(User).count(),
        active_users=db.query(User).filter(
            User.is_active, User.status == UserStatus.ACTIVE
        ).count(),
        suspended_users=db.query(User).filter(User.status == UserStatus.SUSPENDED).count(),
        total_admins=db.query(User).filter(
            User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
        ).count(),
        subscribed_users=db.query(User).filter(User.digest_subscribed).count(),
        total_news_items=db.query(News).count(),
        pending_news_items=db.query(News).filter(News.status == NewsStatus.PENDING).count(),
        analyzed_news_items=db.query(News).filter(News.status == NewsStatus.ANALYZED).count(),
        total_sources=db.query(IngestionSource).count(),
        active_sources=db.query(IngestionSource).filter(IngestionSource.is_active).count(),
        error_sources=db.query(IngestionSource).filter(
            IngestionSource.status == SourceStatus.ERROR
        ).count(),
        total_fetches=db.query(func.sum(IngestionSource.total_fetches)).scalar() or 0,
        total_items_fetched=db.query(func.sum(IngestionSource.total_items_fetched)).scalar() or 0,
        news_today=db.query(News).filter(News.created_at >= today).count(),
        news_this_week=db.query(News).filter(News.created_at >= week_ago).count(),
    )


@router.get(
    "/admin/users",
    response_model=list[AdminUserOut],
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)
@cached("admin_users_list")
def admin_list_users(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[AdminUserOut]:
    """List all users with pagination (admin only)."""
    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    return [AdminUserOut.model_validate(u) for u in users]


@router.get(
    "/admin/users/{user_id}",
    response_model=AdminUserOut,
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)
@cached("admin_user_by_id")
def admin_get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> AdminUserOut:
    """Get a specific user by ID (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return AdminUserOut.model_validate(user)


@router.patch(
    "/admin/users/{user_id}",
    response_model=AdminUserOut,
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)
@limiter.limit(ADMIN_LIMIT)
@invalidate_on_update("admin_stats", "admin_users_list", "admin_user_by_id")
def admin_update_user(
    request: Request,
    response: Response,
    user_id: int,
    body: AdminUserUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> AdminUserOut:
    """Update a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.role is not None:
        user.role = UserRole(body.role)
    if body.status is not None:
        user.status = UserStatus(body.status)
    if body.digest_subscribed is not None:
        user.digest_subscribed = body.digest_subscribed

    db.commit()
    db.refresh(user)
    return AdminUserOut.model_validate(user)


@router.delete(
    "/admin/users/{user_id}",
    status_code=204,
    tags=["admin"],
    dependencies=[Depends(require_super_admin)],
)
@limiter.limit(ADMIN_LIMIT)
@invalidate_on_update("admin_stats", "admin_users_list", "admin_user_by_id")
def admin_delete_user(
    request: Request,
    response: Response,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Soft delete a user (super admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.deleted_at = datetime.now(UTC)
    db.commit()
