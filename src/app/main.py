from __future__ import annotations

import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.bootstrap import ensure_dirs
from app.core.logging import configure_logging, get_logger
from app.db import init_db
from app.routers import auth, export, qr, user

# Prometheus metrics (use prometheus_client directly to ensure /metrics works in prod)
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )
except Exception:
    # Fallback no-op implementations so tests and environments without
    # prometheus_client can still import the application module.
    class _NoopMetric:
        def __init__(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

        def inc(self, *args, **kwargs):
            return None

        def observe(self, *args, **kwargs):
            return None

    Counter = _NoopMetric
    Histogram = _NoopMetric

    def generate_latest():
        return b""

    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"

BASE_DIR = Path(__file__).parent
SPA_DIR = BASE_DIR / "static-frontend"
SPA_INDEX = SPA_DIR / "index.html"

TAGS_METADATA = [
    {
        "name": "auth",
        "description": "Authentication endpoints: signup, login and logout",
    },
    {
        "name": "users",
        "description": "Profile endpoints for viewing, updating, or deleting a user",
    },
    {
        "name": "qr",
        "description": "QR generation, preview, download and history for a user",
    },
    {
        "name": "export",
        "description": "CSV export of a user's QR history",
    },
]

app = FastAPI(
    title="QR Forge",
    description=(
        "Generate, preview, customise and manage QR codes locally with FastAPI."
    ),
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

# Prometheus metrics definitions
REQUEST_COUNT = Counter(
    "qr_forge_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "qr_forge_request_latency_seconds",
    "Request latency seconds",
    ["method", "endpoint"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    if path == "/metrics":
        return await call_next(request)
    import time

    start = time.time()
    try:
        response = await call_next(request)
        status = str(response.status_code)
    except Exception:  # capture exceptions as 500
        status = "500"
        REQUEST_COUNT.labels(method=method, endpoint=path, http_status=status).inc()
        raise
    finally:
        elapsed = time.time() - start
        try:
            REQUEST_LATENCY.labels(method=method, endpoint=path).observe(elapsed)
            REQUEST_COUNT.labels(method=method, endpoint=path, http_status=status).inc()
        except Exception:
            pass
    return response


@app.get("/metrics", include_in_schema=False)
def metrics():
    """Prometheus metrics endpoint (always available)."""
    data = generate_latest()
    return PlainTextResponse(content=data, media_type=CONTENT_TYPE_LATEST)


def _setup_application_insights(app: FastAPI, logger: "logging.Logger") -> None:
    """Attempt to enable Application Insights/OpenTelemetry instrumentation.

    Imported lazily because these dependencies are optional in tests and
    some developer environments.
    """
    try:
        if not settings.app_insights_connection_string:
            return

        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        resource = Resource.create({"service.name": "qr-forge"})
        provider = TracerProvider(resource=resource)

        # Try to create an exporter only if available; exporter packages are
        # optional in some environments so we handle ImportError gracefully.
        try:
            from azure.monitor.opentelemetry.exporter import (
                AzureMonitorTraceExporter,
            )

            exporter = AzureMonitorTraceExporter(
                connection_string=settings.app_insights_connection_string
            )
            provider.add_span_processor(BatchSpanProcessor(exporter))
        except Exception:
            # No exporter available; continue without span export
            logger.debug("No OTLP/Azure exporter available; skipping exporter setup")

        trace.set_tracer_provider(provider)
        FastAPIInstrumentor().instrument_app(app)
        logger.info("Application Insights instrumentation enabled")
    except Exception:
        logger.exception("Failed to enable Application Insights instrumentation")


def _setup_prometheus_instrumentator(app: FastAPI, logger: "logging.Logger") -> None:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app)
        logger.info("Prometheus instrumentation enabled (exposes /metrics)")
    except Exception:
        logger.info(
            "prometheus_fastapi_instrumentator not available; using builtin metrics"
        )


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Application lifespan context: configure logging, ensure dirs and DB.

    Replaces the older `on_event('startup')` approach and provides a single
    async context for startup and shutdown operations.
    """
    # Configure structured logging once at startup
    configure_logging()
    logger = get_logger("qr_forge.app")
    logger.info("Application startup: initializing DB and directories")

    # Ensure asset directories exist (moved out of import-time side-effects)
    created = ensure_dirs(settings)
    for p in created:
        logger.info("Ensured directory exists: %s", str(p))

    try:
        init_db()
    except Exception:
        logger.exception("init_db() raised an exception during startup")

    # Telemetry and metrics
    _setup_application_insights(app, logger)
    _setup_prometheus_instrumentator(app, logger)

    try:
        yield
    finally:
        logger.info("Application shutdown completed")


app.router.lifespan_context = app_lifespan


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(qr.router)
app.include_router(export.router)

app.mount("/assets", StaticFiles(directory=str(BASE_DIR / "assets")), name="assets")

# Mount QR assets directory for serving generated SVG/PNG files
qr_assets_svg = settings.assets_dir
qr_assets_png = settings.temp_dir
try:
    if qr_assets_svg.exists():
        app.mount(
            "/qr-assets/svg",
            StaticFiles(directory=str(qr_assets_svg)),
            name="qr-svg",
        )
    if qr_assets_png.exists():
        app.mount(
            "/qr-assets/png",
            StaticFiles(directory=str(qr_assets_png)),
            name="qr-png",
        )
except Exception:
    # Log but don't fail if directories don't exist yet
    pass

if SPA_DIR.exists():
    app.mount(
        "/frontend-assets",
        StaticFiles(directory=str(SPA_DIR / "frontend-assets")),
        name="spa-assets",
    )


__all__ = ("app",)


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "favicon.ico")


@app.get("/health", summary="Simple health check", include_in_schema=False)
def health() -> dict:
    """Health check that reflects DB connectivity.

    Attempts a short-lived connection to the configured database engine
    and returns 200 when healthy or 503 when the DB cannot be reached.
    """
    from sqlalchemy.exc import SQLAlchemyError

    try:
        # perform a quick connection test
        from app.db import engine

        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return {"status": "ok"}
    except SQLAlchemyError:
        return PlainTextResponse(
            content="DB connectivity failure",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception:
        return PlainTextResponse(
            content="Health check failed",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_catch_all(full_path: str):
    """Serve the SPA for all non-API routes, or 404 for excluded paths."""
    if full_path.startswith(("api", "metrics", "health", "docs", "openapi")):
        return PlainTextResponse(
            content="Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return FileResponse(SPA_INDEX)
