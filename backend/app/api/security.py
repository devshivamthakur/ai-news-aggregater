"""Enterprise security module with JWT refresh tokens, RBAC, and rate limiting."""

from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.config.settings import settings


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("ascii"))


def create_access_token(*, subject: str, role: str = "user") -> str:
    """Create a JWT access token with role claims."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "exp": expire,
        "role": role,
        "type": "access",
    }
    return jwt.encode(
        payload,
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
    )


def create_refresh_token(*, subject: str) -> str:
    """Create a JWT refresh token with longer expiry."""
    expire = datetime.now(UTC) + timedelta(days=settings.jwt.refresh_token_expire_days)
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        payload,
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
    )


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token.

    Returns:
        dict with 'sub', 'role', 'exp' if valid, None otherwise.
    """
    try:
        data = jwt.decode(
            token,
            settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        if data.get("type") != "access":
            return None
        return data
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict | None:
    """Decode and validate a JWT refresh token.

    Returns:
        dict with 'sub', 'exp' if valid, None otherwise.
    """
    try:
        data = jwt.decode(
            token,
            settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        if data.get("type") != "refresh":
            return None
        return data
    except JWTError:
        return None
