from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from sqlmodel import Session

from config import settings
from core.security import get_current_user
from db import get_session
from models import QRItem, User
from schemas import QRCreate, QRPreviewResponse
from services import qr_items

router = APIRouter(prefix="/api/qr", tags=["qr"])
SVG_DIR = settings.svg_dir
PNG_DIR = settings.png_dir


@router.post(
    "/preview",
    response_model=QRPreviewResponse,
    summary="Render a customised QR preview without saving",
    response_description="Inline base64 PNG and SVG markup",
)
def preview_qr(
    payload: QRCreate,
    current_user: User = Depends(get_current_user),
) -> QRPreviewResponse:
    _ = current_user
    return qr_items.preview_qr(payload)


@router.post(
    "",
    response_model=QRItem,
    status_code=status.HTTP_201_CREATED,
    summary="Persist a customised QR code",
    response_description="Saved QR item with asset paths",
)
def create_qr(
    payload: QRCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> QRItem:
    return qr_items.create_qr_item(
        session,
        payload,
        current_user,
        svg_dir=SVG_DIR,
        png_dir=PNG_DIR,
    )


@router.get(
    "",
    response_model=List[QRItem],
    summary="List QR codes owned by the authenticated user",
)
def list_qr(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[QRItem]:
    return qr_items.list_qr_items(session, current_user)


@router.get(
    "/history",
    response_model=List[QRItem],
    summary="Alias for listing QR history",
)
def history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[QRItem]:
    return qr_items.list_qr_items(session, current_user)


@router.delete(
    "/{item_id}",
    summary="Delete a saved QR code",
    response_description="Confirmation payload",
)
def delete_qr(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    qr_items.delete_qr_item(session, current_user, item_id)
    return {"ok": True}


@router.get(
    "/{item_id}/download",
    summary="Download a saved QR code",
    response_description="Binary SVG or PNG stream",
)
def download_qr(
    item_id: int,
    format: str = Query(default="svg", pattern="^(svg|png)$"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    path: Path = qr_items.download_path(session, current_user, item_id, format)
    media_type = "image/svg+xml" if format == "svg" else "image/png"
    return FileResponse(path, media_type=media_type, filename=f"qr-{item_id}.{format}")
