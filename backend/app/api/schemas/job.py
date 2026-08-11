from datetime import datetime

from pydantic import BaseModel


class JobAccepted(BaseModel):
    status: str = "accepted"
    detail: str


class JobStatusOut(BaseModel):
    job_id: str
    status: str  # pending, running, completed, failed
    started_at: datetime | None = None
    completed_at: datetime | None = None
    items_processed: int = 0
    errors: int = 0
