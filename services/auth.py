from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from core.security import create_access_token, get_password_hash, verify_password
from models import User
from schemas import Token, UserCreate, UserLogin


def _normalize_email(email: str) -> str:
    return email.lower()


def signup_user(session: Session, payload: UserCreate) -> User:
    normalized_email = _normalize_email(payload.email)
    existing = session.exec(select(User).where(User.email == normalized_email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    now = datetime.now(timezone.utc)
    user = User(
        email=normalized_email,
        full_name=payload.full_name or "",
        hashed_password=get_password_hash(payload.password),
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login_user(session: Session, payload: UserLogin) -> Token:
    normalized_email = _normalize_email(payload.email)
    user = session.exec(select(User).where(User.email == normalized_email)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(subject=user.id)
    return Token(access_token=token)
