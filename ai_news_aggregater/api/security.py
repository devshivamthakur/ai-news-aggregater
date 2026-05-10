"""Password hashing and JWT helpers for the HTTP API."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from ai_news_aggregater.config.settings import settings


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("ascii"))


def create_access_token(*, subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(
        payload,
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
    )


def decode_access_token(token: str) -> str | None:
    try:
        data = jwt.decode(
            token,
            settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        sub = data.get("sub")
        return str(sub) if sub is not None else None
    except JWTError:
        return None
