import asyncio

from fastapi import APIRouter, Depends, Request

from app.api.deps import require_admin
from app.api.rate_limit import ADMIN_LIMIT, limiter
from app.api.schemas import JobAccepted
from app.core.pipeline import aggregate_and_email
from app.logging.logger import logger

router = APIRouter()


async def _aggregate_job() -> None:
    """Background aggregation job."""
    try:
        await aggregate_and_email()
    except Exception:
        logger.exception("Background aggregation job failed")


@router.post(
    "/jobs/aggregate",
    response_model=JobAccepted,
    tags=["jobs"],
    dependencies=[Depends(require_admin)],
)
@limiter.limit(ADMIN_LIMIT)
async def trigger_aggregate(request: Request) -> JobAccepted:
    """Trigger a full aggregation cycle (admin only)."""
    asyncio.create_task(_aggregate_job())
    return JobAccepted(detail="Aggregation task scheduled")
