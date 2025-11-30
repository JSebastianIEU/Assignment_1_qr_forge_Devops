"""ASGI entrypoint that exposes the FastAPI `app` instance.

This separate module avoids package/module name collisions and keeps the
container entrypoint simple: `uvicorn server:app`.
"""

from __future__ import annotations

from fastapi import FastAPI

# Import the top-level app instance defined in `app.py`.
from app import app as application  # type: ignore


app: FastAPI = application
