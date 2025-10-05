from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import init_db
from routers import auth, export, qr, user

BASE_DIR = Path(__file__).parent

TAGS_METADATA = [
    {
        "name": "auth",
        "description": "Authentication endpoints for signing up, logging in, and logging out.",
    },
    {
        "name": "users",
        "description": "Profile management endpoints for viewing, updating, or deleting the current user.",
    },
    {
        "name": "qr",
        "description": "QR generation, preview, download, and history endpoints scoped to the authenticated user.",
    },
    {
        "name": "export",
        "description": "CSV export of the authenticated user's QR history.",
    },
]

app = FastAPI(
    title="QR Forge",
    description="Generate, preview, customise, and manage QR codes locally with FastAPI.",
    version="1.0.0",
    contact={
        "name": "QR Forge",
        "url": "https://github.com/",
        "email": "support@example.com",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url=None,
)

init_db()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(qr.router)
app.include_router(export.router)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/static", StaticFiles(directory="static"), name="static")


__all__ = ("app",)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "favicon.ico")


@app.get("/", response_class=HTMLResponse, name="home", summary="Serve the landing page")
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "active_page": "home"},
    )


@app.get("/generator", response_class=HTMLResponse, name="generator_page", summary="Serve the QR generator UI")
def generator_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "active_page": "generator"},
    )


@app.get("/history", response_class=HTMLResponse, name="history_page", summary="Serve the saved history UI")
def history_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "active_page": "history"},
    )


@app.get("/profile", response_class=HTMLResponse, name="profile_page", summary="Serve the profile management UI")
def profile_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "active_page": "profile"},
    )


@app.get("/login", response_class=HTMLResponse, name="login_page", summary="Serve the login UI")
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "active_page": "login"},
    )


@app.get("/signup", response_class=HTMLResponse, name="signup_page", summary="Serve the signup UI")
def signup_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "active_page": "signup"},
    )


@app.get("/health", summary="Simple health check")
def health() -> dict:
    return {"status": "ok"}
