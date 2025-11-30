"""Database helpers and engine configuration.

This module centralises engine creation and session management. It configures
connection pooling for production databases and keeps an SQLite-friendly
fallback for local development and tests.
"""

from collections.abc import Generator
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

logger = logging.getLogger("qr_forge.db")


def _ensure_sqlite_dir(database_url: str) -> None:
    """Ensure the parent directory for a sqlite file exists."""
    if not database_url.startswith("sqlite"):
        return
    url = make_url(database_url)
    if url.database:
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)


def get_engine(database_url: Optional[str] = None):
    """Create and return a SQLAlchemy engine configured for the provided URL.

    Production Postgres engines enable pooling and pre-ping to avoid stale
    connections. For sqlite we set `check_same_thread` so the file-based DB
    works in multi-threaded test scenarios.
    """
    url = database_url or settings.database_url
    if not url:
        raise RuntimeError("No database URL provided; set POSTGRES_URL or DATABASE_URL")
    is_sqlite = url.startswith("sqlite")
    if is_sqlite:
        _ensure_sqlite_dir(url)
    # Default connect_args for sqlite
    connect_args = {"check_same_thread": False} if is_sqlite else {}

    # Pooling options for production DBs
    engine_kwargs = {
        "echo": False,
    }
    if not is_sqlite:
        # Production Postgres pooling and resiliency
        engine_kwargs.update(
            {
                "pool_pre_ping": True,
                "pool_size": 5,
                "max_overflow": 10,
            }
        )
        # If the connection string does not specify sslmode and we're on Azure
        # enforce sslmode=require by appending the parameter.
        if "sslmode" not in url and url.startswith("postgres"):
            if "?" in url:
                url = f"{url}&sslmode=require"
            else:
                url = f"{url}?sslmode=require"

    logger.debug("Creating engine for URL: %s (sqlite=%s)", url, is_sqlite)
    return create_engine(url, connect_args=connect_args, **engine_kwargs)


engine = get_engine()


def init_db(db_engine=None) -> None:
    """Initialize database schema (create tables) on the provided engine."""
    active_engine = db_engine or engine
    SQLModel.metadata.create_all(active_engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLModel session for use in dependencies and services."""
    with Session(engine) as session:
        yield session
