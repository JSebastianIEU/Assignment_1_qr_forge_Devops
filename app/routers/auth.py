from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.db import get_session
from app.models import User
from app.schemas import Token, UserCreate, UserLogin, UserRead
from app.services.auth import login_user, signup_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
    response_description="Newly created user profile",
)
def signup(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    return signup_user(session, payload)


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive an access token",
    response_description="Bearer token for subsequent requests",
)
def login(payload: UserLogin, session: Session = Depends(get_session)) -> Token:
    return login_user(session, payload)


@router.post("/logout", summary="Client-side logout acknowledgement")
def logout() -> dict:
    return {"ok": True}
