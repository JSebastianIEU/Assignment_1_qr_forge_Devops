from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.security import create_access_token, get_password_hash, verify_password
from db import get_session
from models import User
from schemas import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
    response_description="Newly created user profile",
)
def signup(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    if len(payload.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
    normalized_email = payload.email.lower()
    existing = session.exec(select(User).where(User.email == normalized_email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

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


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive an access token",
    response_description="Bearer token for subsequent requests",
)
def login(payload: UserLogin, session: Session = Depends(get_session)) -> Token:
    normalized_email = payload.email.lower()
    user = session.exec(select(User).where(User.email == normalized_email)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.post("/logout", summary="Client-side logout acknowledgement")
def logout() -> dict:
    return {"ok": True}
