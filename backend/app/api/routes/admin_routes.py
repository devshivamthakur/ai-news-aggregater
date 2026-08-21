from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api import deps
from app.api.rate_limit import ADMIN_LIMIT, limiter
from app.models.user import User
from app.services.news_service import NewsService

router = APIRouter()


@router.delete("/admin/news", status_code=status.HTTP_200_OK)
@limiter.limit(ADMIN_LIMIT)
def delete_all_news(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_admin),
):
    """
    Delete all news from the database.

    - **db**: an active database session
    - **current_user**: the currently authenticated admin user
    """
    news_service = NewsService(db)
    deleted_count = news_service.delete_all_news()
    return {"message": f"Successfully deleted {deleted_count} news articles."}
