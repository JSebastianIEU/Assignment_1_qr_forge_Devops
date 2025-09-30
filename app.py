from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from db import init_db
from routers import auth, export, qr, user

BASE_DIR = Path(__file__).parent

app = FastAPI(title="QR Forge")

init_db()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(qr.router, prefix="/api/qr", tags=["qr"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    template = BASE_DIR / "templates" / "index.html"
    return template.read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
