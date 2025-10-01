from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.security import get_current_user, get_password_hash
from db import get_session
from models import QRItem, User
from schemas import UserRead, UserUpdate

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserRead)
def update_current_user(
    payload: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> User:
    updated = False
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()
        updated = True
    if payload.password:
        if len(payload.password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
        current_user.hashed_password = get_password_hash(payload.password)
        updated = True
    if not updated:
        return current_user
    current_user.updated_at = datetime.now(timezone.utc)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.delete("/me")
def delete_current_user(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    qrs = session.exec(select(QRItem).where(QRItem.user_id == current_user.id)).all()
    for item in qrs:
        if item.svg_path and Path(item.svg_path).exists():
            Path(item.svg_path).unlink()
        if item.png_path and Path(item.png_path).exists():
            Path(item.png_path).unlink()
        session.delete(item)
    session.delete(current_user)
    session.commit()
    return {"ok": True}
