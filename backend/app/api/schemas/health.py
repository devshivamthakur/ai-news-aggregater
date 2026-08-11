
from pydantic import BaseModel


class HealthOut(BaseModel):
    status: str
    version: str
    environment: str
    scheduler_enabled: bool
    database_connected: bool
    uptime_seconds: float | None = None
