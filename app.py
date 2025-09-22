from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from db import init_db
from routers import qr, export

app = FastAPI(title="QR Forge")

init_db()
app.include_router(qr.router, prefix="/api/qr", tags=["qr"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    return open("templates/index.html", "r", encoding="utf-8").read()

@app.get("/health")
def health():
    return {"status": "ok"}
