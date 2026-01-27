from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, Response
from sqlmodel import Session

from app.core.security import get_current_user
from app.db import get_session
from app.models import QRItem, User
from app.schemas import QRCreate, QRPreviewResponse
from app.services import qr_items

router = APIRouter(prefix="/api/qr", tags=["qr"])


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
    item = qr_items.create_qr_item(
        session,
        payload,
        current_user,
    )
    # Convert filesystem paths to public URLs
    item_dict = item.model_dump()
    item_dict['svg_path'] = qr_items.path_to_url(item.svg_path)
    if item.png_path:
        item_dict['png_path'] = qr_items.path_to_url(item.png_path)
    return QRItem(**item_dict)


@router.get(
    "",
    response_model=List[QRItem],
    summary="List QR codes owned by the authenticated user",
)
def list_qr(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[QRItem]:
    items = qr_items.list_qr_items(session, current_user)
    # Convert filesystem paths to public URLs for frontend access
    # Create new items with converted paths
    converted_items = []
    for item in items:
        # Convert to dict, modify paths, and convert back
        item_dict = item.model_dump()
        item_dict['svg_path'] = qr_items.path_to_url(item.svg_path)
        if item.png_path:
            item_dict['png_path'] = qr_items.path_to_url(item.png_path)
        converted_items.append(QRItem(**item_dict))
    return converted_items


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
    from app.storage import get_storage_backend

    # Try to get filesystem path (local storage)
    path = qr_items.download_path(session, current_user, item_id, format)
    media_type = "image/svg+xml" if format == "svg" else "image/png"

    if path is None:
        # Blob storage: download from blob and stream
        item = qr_items.get_owned_item(session, current_user, item_id)
        path_str = item.svg_path if format == "svg" else item.png_path
        if not path_str:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{format.upper()} not available",
            )

        storage = get_storage_backend()
        content = storage.read_file(path_str)

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="qr-{item_id}.{format}"'
            },
        )

    # Local storage: serve file directly
    return FileResponse(path, media_type=media_type, filename=f"qr-{item_id}.{format}")
