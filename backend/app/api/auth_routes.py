"""Enterprise authentication and account routes with RBAC and refresh tokens."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_client_ip, get_current_user, get_db, require_admin
from app.api.schemas import (
    PasswordChange,
    RefreshTokenIn,
    SubscriptionUpdate,
    TokenPairOut,
    UserLogin,
    UserMeOut,
    UserRegister,
    UserUpdate,
)
from app.api.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models import User, UserRole, UserStatus

router = APIRouter()


@router.post("/register", response_model=TokenPairOut, tags=["auth"], dependencies=[Depends(require_admin)])
def register(
    body: UserRegister,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> TokenPairOut:
    """Register a new user account."""
    user = User(
        email=body.email,
        name=body.name,
        password_hash=hash_password(body.password),
        interests=[],
        digest_subscribed=True,
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        email_verified=False,
        last_login_ip=get_client_ip(request),
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from e

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenPairOut(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/login", response_model=TokenPairOut, tags=["auth"])
def login(
    body: UserLogin,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> TokenPairOut:
    """Authenticate user and return token pair."""
    email = body.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.is_locked:
        raise HTTPException(
            status_code=423,
            detail="Account temporarily locked due to too many failed attempts",
        )

    if not verify_password(body.password, user.password_hash):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(UTC) + datetime.timedelta(minutes=30)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active or user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=403, detail="Account inactive or suspended")

    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(UTC)
    user.last_login_ip = get_client_ip(request)
    db.commit()

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenPairOut(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenPairOut, tags=["auth"])
def refresh_token(body: RefreshTokenIn) -> TokenPairOut:
    """Refresh access token using refresh token."""
    data = decode_refresh_token(body.refresh_token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = data["sub"]
    # In production, check if refresh token is blacklisted
    access_token = create_access_token(subject=user_id)
    new_refresh_token = create_refresh_token(subject=user_id)

    return TokenPairOut(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserMeOut, tags=["auth"])
def me(user: Annotated[User, Depends(get_current_user)]) -> UserMeOut:
    """Get current user profile."""
    return UserMeOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        status=user.status.value,
        digest_subscribed=bool(user.digest_subscribed),
        digest_frequency=user.digest_frequency,
        interests=list(user.interests) if user.interests is not None else [],
        email_verified=user.email_verified,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.patch("/me", response_model=UserMeOut, tags=["auth"])
def update_profile(
    body: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> UserMeOut:
    """Update current user profile."""
    if body.name is not None:
        user.name = body.name
    if body.interests is not None:
        user.interests = body.interests
    if body.preferred_language is not None:
        user.preferred_language = body.preferred_language

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserMeOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        status=user.status.value,
        digest_subscribed=bool(user.digest_subscribed),
        digest_frequency=user.digest_frequency,
        interests=list(user.interests) if user.interests is not None else [],
        email_verified=user.email_verified,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.patch("/me/subscription", response_model=UserMeOut, tags=["auth"])
def update_subscription(
    body: SubscriptionUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> UserMeOut:
    """Update digest subscription settings."""
    if body.digest_subscribed is not None:
        user.digest_subscribed = body.digest_subscribed
    if body.digest_frequency is not None:
        user.digest_frequency = body.digest_frequency

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserMeOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        status=user.status.value,
        digest_subscribed=bool(user.digest_subscribed),
        digest_frequency=user.digest_frequency,
        interests=list(user.interests) if user.interests is not None else [],
        email_verified=user.email_verified,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.post("/me/change-password", tags=["auth"])
def change_password(
    body: PasswordChange,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Change user password."""
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.password_hash = hash_password(body.new_password)
    user.password_changed_at = datetime.now(UTC)
    db.commit()

    return {"message": "Password changed successfully"}
