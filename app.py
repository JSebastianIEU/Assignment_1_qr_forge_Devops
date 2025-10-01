from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import init_db
from routers import auth, export, qr, user

BASE_DIR = Path(__file__).parent

app = FastAPI(title="QR Forge")

init_db()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(qr.router, prefix="/api/qr", tags=["qr"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse, name="home")
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "active_page": "home"},
    )


@app.get("/generator", response_class=HTMLResponse, name="generator_page")
def generator_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "active_page": "generator"},
    )


@app.get("/history", response_class=HTMLResponse, name="history_page")
def history_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "active_page": "history"},
    )


@app.get("/profile", response_class=HTMLResponse, name="profile_page")
def profile_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "active_page": "profile"},
    )


@app.get("/login", response_class=HTMLResponse, name="login_page")
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "active_page": "login"},
    )


@app.get("/signup", response_class=HTMLResponse, name="signup_page")
def signup_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "active_page": "signup"},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
