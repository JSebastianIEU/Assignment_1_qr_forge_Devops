from pathlib import Path

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from core.security import get_current_user
from db import get_session
from models import QRItem, User
from schemas import UserRead

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
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
