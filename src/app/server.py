"""ASGI entrypoint that exposes the FastAPI `app` instance.

This separate module avoids package/module name collisions and keeps the
container entrypoint simple: `uvicorn app.server:app`.
"""

from __future__ import annotations

from fastapi import FastAPI

# Import the top-level app instance defined in `app/main.py`.
from app.main import app as application

app: FastAPI = application
