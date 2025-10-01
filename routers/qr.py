from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from core.security import get_current_user
from db import get_session
from models import QRItem, User
from schemas import QRCreate, QRPreviewResponse
from services.qr import QRConfig, encode_render, generate_qr_assets, render_qr

router = APIRouter()
SVG_DIR = Path("generated_svgs")
PNG_DIR = Path("generated_pngs")
SVG_DIR.mkdir(parents=True, exist_ok=True)
PNG_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_owner(session: Session, user: User, item_id: int) -> QRItem:
    item = session.exec(
        select(QRItem).where(QRItem.id == item_id, QRItem.user_id == user.id)
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR item not found")
    return item


def _to_config(payload: QRCreate) -> QRConfig:
    return QRConfig(
        url=str(payload.url),
        foreground_color=payload.foreground_color,
        background_color=payload.background_color,
        size=payload.size,
        padding=payload.padding,
        border_radius=payload.border_radius,
    )


@router.post("/preview", response_model=QRPreviewResponse)
def preview_qr(
    payload: QRCreate,
    current_user: User = Depends(get_current_user),
) -> QRPreviewResponse:
    _ = current_user
    render = render_qr(_to_config(payload))
    preview = encode_render(render)
    return QRPreviewResponse(svg_data=preview.svg_data, png_data=preview.png_data)


@router.post("", response_model=QRItem, status_code=status.HTTP_201_CREATED)
def create_qr(
    payload: QRCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> QRItem:
    now = datetime.now(timezone.utc)
    assets = generate_qr_assets(_to_config(payload), svg_dir=SVG_DIR, png_dir=PNG_DIR)

    item = QRItem(
        user_id=current_user.id,
        title=payload.title.strip() or "Untitled QR",
        url=str(payload.url),
        foreground_color=payload.foreground_color,
        background_color=payload.background_color,
        size=payload.size,
        padding=payload.padding,
        border_radius=payload.border_radius,
        overlay_text=None,
        svg_path=str(assets.svg_path),
        png_path=str(assets.png_path),
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
            Path(item.svg_path).unlink()
        if item.png_path and Path(item.png_path).exists():
            Path(item.png_path).unlink()
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
