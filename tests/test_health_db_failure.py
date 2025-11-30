"""Tests for health endpoint reflecting DB connectivity failures."""

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app as application


class BadEngine:
    def connect(self):
        raise SQLAlchemyError("connection failed")


def test_health_returns_503_on_db_failure(monkeypatch):
    """When the DB engine cannot connect, /health returns 503."""
    monkeypatch.setattr("app.db.engine", BadEngine())
    client = TestClient(application)
    resp = client.get("/health")
    assert resp.status_code == 503
    assert "DB connectivity" in resp.text or "Health check failed" in resp.text
