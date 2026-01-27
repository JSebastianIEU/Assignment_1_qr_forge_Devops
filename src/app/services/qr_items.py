from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.config import settings
from app.models import QRItem, User
from app.schemas import QRCreate, QRPreviewResponse
from app.services.qr import (
    QRConfig,
    QRPreview,
    encode_render,
    render_qr,
)
from app.storage import get_storage_backend


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
) -> QRItem:
    now = datetime.now(timezone.utc)
    storage = get_storage_backend()

    # Generate QR code
    config = build_config(payload)
    render = render_qr(config)

    # Generate unique filenames
    import uuid

    base_name = str(uuid.uuid4())
    svg_filename = f"{base_name}.svg"
    png_filename = f"{base_name}.png"

    # Save to storage (returns URL for blob storage, path for local)
    svg_path = storage.save_file(render.svg_text, svg_filename, "image/svg+xml")
    png_path = storage.save_file(render.png_bytes, png_filename, "image/png")

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
        svg_path=svg_path,
        png_path=png_path,
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="QR item not found"
        )
    return item


def delete_qr_item(session: Session, current_user: User, item_id: int) -> None:
    item = get_owned_item(session, current_user, item_id)
    storage = get_storage_backend()
    storage.delete_file(item.svg_path)
    if item.png_path:
        storage.delete_file(item.png_path)
    session.delete(item)
    session.commit()


def download_path(
    session: Session, current_user: User, item_id: int, format: str
) -> Path | None:
    """Get filesystem path for download (local storage only).

    Returns None for blob storage (download endpoint will redirect to blob URL).
    """
    item = get_owned_item(session, current_user, item_id)
    storage = get_storage_backend()

    path_str = item.svg_path if format == "svg" else item.png_path
    if not path_str:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{format.upper()} not available",
        )

    # For blob storage, return None (will use URL redirect)
    file_path = storage.get_file_path(path_str)
    if file_path is None:
        return None

    # For local storage, verify file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{format.upper()} file not found",
        )
    return file_path


def get_download_url(
    session: Session, current_user: User, item_id: int, format: str
) -> str:
    """Get direct download URL (for blob storage) or relative path."""
    item = get_owned_item(session, current_user, item_id)
    path_str = item.svg_path if format == "svg" else item.png_path
    if not path_str:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{format.upper()} not available",
        )
    return path_str


def path_to_url(path_or_url: str) -> str:
    """Convert filesystem path to URL, or return blob URL as-is.

    For Azure Blob Storage: returns the URL directly (already public).
    For local filesystem: converts to /qr-assets/svg/filename format.
    """
    if not path_or_url:
        return path_or_url

    # If it's already a URL (blob storage), return as-is
    if path_or_url.startswith(("http://", "https://")):
        return path_or_url

    # For local filesystem, convert to relative URL
    path = Path(path_or_url)
    filename = path.name

    # Check if it's in the SVG assets directory
    try:
        path.relative_to(settings.assets_dir)
        return f"/qr-assets/svg/{filename}"
    except ValueError:
        pass

    try:
        path.relative_to(settings.temp_dir)
        return f"/qr-assets/png/{filename}"
    except ValueError:
        pass

    # If we can't map it, return as-is (shouldn't happen in normal operation)
    return path_or_url
