import os
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import AnyHttpUrl, BaseModel
from sqlmodel import Session, select

from core.security import get_current_user
from db import get_session
from models import QRItem, User

import qrcode
import qrcode.image.svg as svg

router = APIRouter()
SVG_DIR = Path("generated_svgs")
SVG_DIR.mkdir(parents=True, exist_ok=True)


class QRCreate(BaseModel):
    title: str
    url: AnyHttpUrl


def _ensure_owner(session: Session, user: User, item_id: int) -> QRItem:
    item = session.exec(
        select(QRItem).where(QRItem.id == item_id, QRItem.user_id == user.id)
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR item not found")
    return item


@router.post("", response_model=QRItem, status_code=status.HTTP_201_CREATED)
def create_qr(
    payload: QRCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> QRItem:
    factory = svg.SvgImage
    img = qrcode.make(str(payload.url), image_factory=factory)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    filename = f"{uuid.uuid4()}.svg"
    path = SVG_DIR / filename
    with path.open("wb") as f:
        f.write(buf.read())

    now = datetime.now(timezone.utc)
    item = QRItem(
        user_id=current_user.id,
        title=payload.title.strip() or "Untitled QR",
        url=str(payload.url),
        svg_path=str(path),
        created_at=now,
        updated_at=now,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("", response_model=List[QRItem])
def list_qr(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[QRItem]:
    return session.exec(
        select(QRItem)
        .where(QRItem.user_id == current_user.id)
        .order_by(QRItem.created_at.desc())
    ).all()


@router.get("/history", response_model=List[QRItem])
def history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[QRItem]:
    return list_qr(session=session, current_user=current_user)


@router.delete("/{item_id}")
def delete_qr(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    item = _ensure_owner(session, current_user, item_id)
    try:
        if item.svg_path and Path(item.svg_path).exists():
            os.remove(item.svg_path)
        if item.png_path and Path(item.png_path).exists():
            os.remove(item.png_path)
    finally:
        session.delete(item)
        session.commit()
    return {"ok": True}


@router.get("/{item_id}/download")
def download_qr(
    item_id: int,
    format: str = Query(default="svg", pattern="^(svg|png)$"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = _ensure_owner(session, current_user, item_id)
    if format == "svg":
        if not item.svg_path or not Path(item.svg_path).exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SVG not available")
        return FileResponse(item.svg_path, media_type="image/svg+xml", filename=f"qr-{item.id}.svg")

    if not item.png_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PNG export not available yet")
    if not Path(item.png_path).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PNG not available")
    return FileResponse(item.png_path, media_type="image/png", filename=f"qr-{item.id}.png")
