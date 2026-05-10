"""Authentication and account routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ai_news_aggregater.api.deps import get_current_user, get_db
from ai_news_aggregater.api.schemas import (
    SubscriptionUpdate,
    TokenOut,
    UserLogin,
    UserMeOut,
    UserRegister,
)
from ai_news_aggregater.api.security import create_access_token, hash_password, verify_password
from ai_news_aggregater.models import User

router = APIRouter()


@router.post("/register", response_model=TokenOut, tags=["auth"])
def register(body: UserRegister, db: Annotated[Session, Depends(get_db)]) -> TokenOut:
    user = User(
        email=body.email.lower().strip(),
        name=body.name.strip(),
        password_hash=hash_password(body.password),
        interests=[],
        digest_subscribed=True,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from e
    token = create_access_token(subject=str(user.id))
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut, tags=["auth"])
def login(body: UserLogin, db: Annotated[Session, Depends(get_db)]) -> TokenOut:
    email = body.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.is_active != 1:
        raise HTTPException(status_code=403, detail="Account inactive")
    token = create_access_token(subject=str(user.id))
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserMeOut, tags=["auth"])
def me(user: Annotated[User, Depends(get_current_user)]) -> UserMeOut:
    return UserMeOut(
        id=user.id,
        email=user.email,
        name=user.name,
        digest_subscribed=bool(user.digest_subscribed),
        interests=list(user.interests) if user.interests is not None else None,
    )


@router.patch("/me/subscription", response_model=UserMeOut, tags=["auth"])
def update_subscription(
    body: SubscriptionUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> UserMeOut:
    user.digest_subscribed = body.digest_subscribed
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserMeOut(
        id=user.id,
        email=user.email,
        name=user.name,
        digest_subscribed=bool(user.digest_subscribed),
        interests=list(user.interests) if user.interests is not None else None,
    )
