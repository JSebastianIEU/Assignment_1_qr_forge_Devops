import os, uuid
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, AnyHttpUrl
from sqlmodel import Session, select

from db import engine
from models import QRItem

import qrcode
import qrcode.image.svg as svg

router = APIRouter()
SVG_DIR = "generated_svgs"
os.makedirs(SVG_DIR, exist_ok=True)

class QRCreate(BaseModel):
    title: str
    url: AnyHttpUrl

@router.post("", response_model=QRItem)
def create_qr(payload: QRCreate):
    # generate SVG
    factory = svg.SvgImage
    img = qrcode.make(str(payload.url), image_factory=factory)
    buf = BytesIO()
    img.save(buf); buf.seek(0)

    # save to disk
    filename = f"{uuid.uuid4()}.svg"
    path = os.path.join(SVG_DIR, filename)
    with open(path, "wb") as f:
        f.write(buf.read())

    # persist row
    item = QRItem(
        title=payload.title.strip(),
        url=str(payload.url),
        svg_path=path,
        created_at=datetime.utcnow()
    )
    with Session(engine) as s:
        s.add(item); s.commit(); s.refresh(item)
        return item

@router.get("", response_model=list[QRItem])
def list_qr():
    with Session(engine) as s:
        return s.exec(select(QRItem).order_by(QRItem.created_at.desc())).all()

@router.delete("/{item_id}")
def delete_qr(item_id: int):
    with Session(engine) as s:
        item = s.get(QRItem, item_id)
        if not item:
            raise HTTPException(404, "Not found")
        try:
            if os.path.exists(item.svg_path):
                os.remove(item.svg_path)
        finally:
            s.delete(item); s.commit()
        return {"ok": True}

@router.get("/{item_id}/download")
def download_svg(item_id: int):
    with Session(engine) as s:
        item = s.get(QRItem, item_id)
        if not item:
            raise HTTPException(404, "Not found")
        return FileResponse(item.svg_path, media_type="image/svg+xml", filename="qr.svg")
