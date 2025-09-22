import csv, io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from db import engine
from models import QRItem

router = APIRouter()

@router.get("/csv")
def export_csv():
    with Session(engine) as s:
        rows = s.exec(select(QRItem)).all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["title","url","created_at","svg_file"])
    for r in rows:
        w.writerow([r.title, r.url, r.created_at.isoformat(), r.svg_path.split("/")[-1]])
    buf.seek(0)

    return StreamingResponse(
        iter([buf.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=qr_items.csv"}
    )
