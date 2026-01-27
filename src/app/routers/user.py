from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.security import get_current_user
from app.db import get_session
from app.models import User
from app.schemas import UserRead, UserUpdate
from app.services.user import delete_user_and_assets, update_profile

router = APIRouter(prefix="/api/user", tags=["users"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Return the authenticated user's profile",
    response_description="Current user record",
)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Update profile details",
    response_description="Updated user record",
)
def update_current_user(
    payload: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> User:
    return update_profile(session, current_user, payload)


@router.delete(
    "/me",
    summary="Delete the authenticated user and all owned QR codes",
    response_description="Confirmation payload",
)
def delete_current_user(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    delete_user_and_assets(session, current_user)
    return {"ok": True}
