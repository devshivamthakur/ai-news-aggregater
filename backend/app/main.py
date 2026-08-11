"""Main entry point for AI News Aggregator API server."""

from dotenv import load_dotenv

load_dotenv()

from app.api.main import app  # noqa: E402

__all__ = ["app"]

