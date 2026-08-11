"""FastAPI dependencies with RBAC and enterprise patterns."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.security import decode_access_token
from app.config.settings import settings
from app.models import User, UserRole, UserStatus
from app.storage.db import SessionLocal

http_bearer = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
) -> User:
    """Get current authenticated user from JWT token."""
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")

    data = decode_access_token(creds.credentials)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        user_id = int(data["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token subject") from None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account inactive")

    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=403, detail="Account suspended")

    if user.is_locked:
        raise HTTPException(status_code=403, detail="Account temporarily locked")

    return user


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require admin role."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_super_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require super admin role."""
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_user


def require_role(*roles: UserRole):
    """Dependency factory to require specific roles."""
    def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(r.value for r in roles)}",
            )
        return current_user
    return role_checker


def require_admin_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    """Legacy API key check for backward compatibility."""
    expected = settings.api_key
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
