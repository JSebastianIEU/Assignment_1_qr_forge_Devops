from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import QRItem, User
from app.schemas import UserUpdate


def update_profile(session: Session, current_user: User, payload: UserUpdate) -> User:
    updated = False
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()
        updated = True
    if payload.password:
        current_user.hashed_password = get_password_hash(payload.password)
        updated = True

    if not updated:
        return current_user

    current_user.updated_at = datetime.now(timezone.utc)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


def delete_user_and_assets(session: Session, current_user: User) -> None:
    qrs = session.exec(select(QRItem).where(QRItem.user_id == current_user.id)).all()
    for item in qrs:
        _delete_asset_file(item.svg_path)
        _delete_asset_file(item.png_path)
        session.delete(item)
    session.delete(current_user)
    session.commit()


def _delete_asset_file(path: str | None) -> None:
    if not path:
        return
    p = Path(path)
    if p.exists():
        p.unlink()
