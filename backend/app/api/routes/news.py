from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import (
    NewsListOut,
    NewsOut,
    NewsSearchParams,
)
from app.models import News
from app.storage.cache import cached

router = APIRouter()


@router.get("/news", response_model=NewsListOut, tags=["news"])
@cached("news_list")
def list_news(
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[NewsSearchParams, Depends()],
) -> NewsListOut:
    """List news with pagination and filtering."""
    query = db.query(News).filter(News.is_active)

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
