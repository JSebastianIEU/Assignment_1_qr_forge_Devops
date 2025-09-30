import csv
import io
from pathlib import Path
from typing import Iterable

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from core.security import get_current_user
from db import get_session
from models import QRItem, User

router = APIRouter()


@router.get("/csv")
def export_csv(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    rows = session.exec(
        select(QRItem).where(QRItem.user_id == current_user.id).order_by(QRItem.created_at.desc())
    ).all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "title",
        "url",
        "created_at",
        "foreground_color",
        "background_color",
        "size",
        "padding",
        "border_radius",
        "overlay_text",
        "svg_file",
        "png_file",
    ])
    for r in rows:
        writer.writerow([
            r.title,
            r.url,
            r.created_at.isoformat(),
            r.foreground_color,
            r.background_color,
            r.size,
            r.padding,
            r.border_radius,
            r.overlay_text or "",
            Path(r.svg_path).name if r.svg_path else "",
            Path(r.png_path).name if r.png_path else "",
        ])
    buf.seek(0)

    def iter_buf() -> Iterable[str]:
        yield buf.read()

    return StreamingResponse(
        iter_buf(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=qr_items.csv"},
    )
