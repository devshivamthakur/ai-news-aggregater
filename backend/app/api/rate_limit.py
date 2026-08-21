"""Centralized rate limiter configuration built on slowapi.

slowapi wraps the `limits` library and integrates with FastAPI. A single
:class:`Limiter` instance is created here and shared across the application so
that counters are consistent. The default limit is applied globally via
``SlowAPIMiddleware`` (see ``app/api/main.py``), while stricter per-route limits
can be attached with the ``@limiter.limit(...)`` decorator on sensitive
endpoints such as auth and admin mutations.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config.settings import settings


def _key_func(request) -> str:
    """Build a rate-limit key from the client IP and authenticated subject.

    When a request carries a bearer token we key on the user id (``sub`` claim)
    so that a single authenticated account cannot be rate-limited on behalf of
    others sharing a NAT. Anonymous requests fall back to the remote address.
    """
    auth = request.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]
        try:
            from jose import jwt

            data = jwt.get_unverified_claims(token)
            sub = data.get("sub")
            if sub:
                return f"user:{sub}"
        except Exception:
            pass
    return get_remote_address(request)


# A single shared Limiter instance for the whole app.
limiter = Limiter(
    key_func=_key_func,
    default_limits=[settings.rate_limit.default_limit] if settings.rate_limit.enabled else [],
    storage_uri=settings.rate_limit.storage_uri,
    strategy=settings.rate_limit.strategy,
    headers_enabled=True,
    swallow_errors=True,
)

# Convenience limit strings for stricter endpoints.
AUTH_LIMIT = settings.rate_limit.auth_limit
ADMIN_LIMIT = settings.rate_limit.admin_limit
