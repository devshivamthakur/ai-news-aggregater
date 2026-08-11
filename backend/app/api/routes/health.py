from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import HealthOut
from app.config.settings import settings
from app.storage.cache import cached

router = APIRouter()


@router.get("/health", response_model=HealthOut, tags=["health"])
@cached("health")
def health(db: Annotated[Session, Depends(get_db)]) -> HealthOut:
    """Health check endpoint."""
    db_connected = True
    try:
        db.execute("SELECT 1")
    except Exception:
        db_connected = False

    return HealthOut(
        status="ok",
        version="2.0.0",
        environment=settings.environment,
        scheduler_enabled=settings.scheduler.enabled,
        database_connected=db_connected,
    )
