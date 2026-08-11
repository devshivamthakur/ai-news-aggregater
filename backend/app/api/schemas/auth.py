from datetime import datetime
from typing import Annotated

from email_validator import EmailNotValidError, validate_email
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator


def _email_local_ok(v: str) -> str:
    """Validate email format while allowing special-use/reserved domains
    (e.g. `.test`, `.local`) commonly used in local development."""
    try:
        result = validate_email(v, test_environment=True)
        return result.normalized
    except EmailNotValidError as e:
        domain = v.lower().rsplit("@", 1)[-1] if "@" in v else ""
        if domain.endswith(".local"):
            # RFC 6762 mDNS names (e.g. `user@host.local`) are valid locally.
            return v
        raise ValueError(str(e)) from e


LocalEmailStr = Annotated[str, AfterValidator(_email_local_ok)]


class UserRegister(BaseModel):
    email: LocalEmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def name_stripped(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Name is required")
        return s


class UserLogin(BaseModel):
    email: LocalEmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenIn(BaseModel):
    refresh_token: str


class UserMeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str | None = None
    role: str
    status: str
    digest_subscribed: bool
    digest_frequency: str
    interests: list[str]
    email_verified: bool
    last_login_at: datetime | None = None
    created_at: datetime


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    interests: list[str] | None = None
    preferred_language: str | None = None


class SubscriptionUpdate(BaseModel):
    digest_subscribed: bool | None = None
    digest_frequency: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
