from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import HTTPException, status
from sqlmodel import Session, select

from models import QRItem, User
from schemas import QRCreate, QRPreviewResponse
from services.qr import QRConfig, QRPreview, encode_render, generate_qr_assets, render_qr


def build_config(payload: QRCreate) -> QRConfig:
    return QRConfig(
        url=str(payload.url),
        foreground_color=payload.foreground_color,
        background_color=payload.background_color,
        size=payload.size,
        padding=payload.padding,
        border_radius=payload.border_radius,
    )


def preview_qr(payload: QRCreate) -> QRPreviewResponse:
    preview: QRPreview = encode_render(render_qr(build_config(payload)))
    return QRPreviewResponse(svg_data=preview.svg_data, png_data=preview.png_data)


def create_qr_item(
    session: Session,
    payload: QRCreate,
    current_user: User,
    *,
    svg_dir: Path,
    png_dir: Path,
) -> QRItem:
    now = datetime.now(timezone.utc)
    assets = generate_qr_assets(build_config(payload), svg_dir=svg_dir, png_dir=png_dir)

    item = QRItem(
        user_id=current_user.id,
        title=payload.title.strip() or "Untitled QR",
        url=str(payload.url),
        foreground_color=payload.foreground_color,
        background_color=payload.background_color,
        size=payload.size,
        padding=payload.padding,
        border_radius=payload.border_radius,
        overlay_text=payload.overlay_text,
        svg_path=str(assets.svg_path),
        png_path=str(assets.png_path),
        created_at=now,
        updated_at=now,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def list_qr_items(session: Session, current_user: User) -> List[QRItem]:
    return session.exec(
        select(QRItem)
        .where(QRItem.user_id == current_user.id)
        .order_by(QRItem.created_at.desc())
    ).all()


def get_owned_item(session: Session, current_user: User, item_id: int) -> QRItem:
    item = session.exec(
        select(QRItem).where(QRItem.id == item_id, QRItem.user_id == current_user.id)
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR item not found")
    return item


def delete_qr_item(session: Session, current_user: User, item_id: int) -> None:
    item = get_owned_item(session, current_user, item_id)
    _delete_if_exists(item.svg_path)
    _delete_if_exists(item.png_path)
    session.delete(item)
    session.commit()


def download_path(session: Session, current_user: User, item_id: int, format: str) -> Path:
    item = get_owned_item(session, current_user, item_id)
    if format == "svg":
        path = Path(item.svg_path)
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SVG not available")
        return path

    if not item.png_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PNG export not available yet")
    path = Path(item.png_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PNG not available")
    return path


def _delete_if_exists(path: str | None) -> None:
    if not path:
        return
    p = Path(path)
    if p.exists():
        p.unlink()
