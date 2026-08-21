from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.schemas import (
    NewsListOut,
    NewsOut,
    NewsSearchParams,
)
from app.models import News, User
from app.storage.cache import cached

router = APIRouter()


@router.get("/news", response_model=NewsListOut, tags=["news"])
@cached("news_list")
def list_news(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    params: Annotated[NewsSearchParams, Depends()],
) -> NewsListOut:
    """List news with pagination and filtering.

    Admins see all active news. Regular users see only news whose
    category matches one of their configured interests (the ``User.interests``
    JSON list). When a user has no interests set, all news is returned as a
    graceful fallback.
    """
    query = db.query(News).filter(News.is_active)

    # Admins see everything; regular users are scoped to their interests.
    if not current_user.is_admin:
        interests = current_user.interests or []
        if interests:
            query = query.filter(News.category.in_(interests))

    if params.q:
        search = f"%{params.q}%"
        query = query.filter(
            (News.title.ilike(search)) | (News.summary.ilike(search))
        )
    if params.category:
        query = query.filter(News.category == params.category)
    if params.source:
        query = query.filter(News.source == params.source)
    if params.news_type:
        query = query.filter(News.news_type == params.news_type)

    total = query.count()
    offset = (params.page - 1) * params.page_size
    rows = query.order_by(News.created_at.desc()).offset(offset).limit(params.page_size).all()

    items = [
        NewsOut(
            id=n.id,
            title=n.title,
            summary=n.summary,
            category=n.category,
            source=n.source,
            source_url=n.source_url,
            url=n.url,
            image_url=n.image_url,
            author=n.author,
            news_type=n.news_type.value if hasattr(n.news_type, 'value') else str(n.news_type),
            status=n.status.value if hasattr(n.status, 'value') else str(n.status),
            sentiment_score=n.sentiment_score,
            keywords=n.keywords,
            reading_time_minutes=n.reading_time_minutes,
            language=n.language,
            published_at=n.published_at,
            created_at=n.created_at,
        )
        for n in rows
    ]

    return NewsListOut(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        has_next=(offset + params.page_size) < total,
    )


@router.get("/news/{news_id}", response_model=NewsOut, tags=["news"])
@cached("news_by_id")
def get_news(
    news_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
) -> NewsOut:
    """Get a specific news item by ID."""
    n = db.query(News).filter(News.id == news_id, News.is_active).first()
    if not n:
        raise HTTPException(status_code=404, detail="News not found")
    return NewsOut(
        id=n.id,
        title=n.title,
        summary=n.summary,
        category=n.category,
        source=n.source,
        source_url=n.source_url,
        url=n.url,
        image_url=n.image_url,
        author=n.author,
        news_type=n.news_type.value if hasattr(n.news_type, 'value') else str(n.news_type),
        status=n.status.value if hasattr(n.status, 'value') else str(n.status),
        sentiment_score=n.sentiment_score,
        keywords=n.keywords,
        reading_time_minutes=n.reading_time_minutes,
        language=n.language,
        published_at=n.published_at,
        created_at=n.created_at,
    )
