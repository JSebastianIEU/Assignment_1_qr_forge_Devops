import sys
from pathlib import Path

from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app import app
from db import get_session
from models import QRItem, User

TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


from typing import Generator

@pytest.fixture(autouse=True)
def _prepare_database() -> Generator[None, None, None]:
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client(tmp_path, monkeypatch):
    from typing import Generator

    def override_get_session() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    from routers import qr

    svg_dir = tmp_path / "svg"
    png_dir = tmp_path / "png"
    svg_dir.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(qr, "SVG_DIR", svg_dir, raising=False)
    monkeypatch.setattr(qr, "PNG_DIR", png_dir, raising=False)

    return TestClient(app)


def _auth_headers(client: TestClient) -> dict:
    signup_payload = {
        "email": "alice@example.com",
        "full_name": "Alice Example",
        "password": "secret123",
    }
    resp = client.post("/api/auth/signup", json=signup_payload)
    assert resp.status_code == 201, resp.text

    login_payload = {
        "email": signup_payload["email"],
        "password": signup_payload["password"],
    }
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_qr_requires_auth(client: TestClient) -> None:
    resp = client.post(
        "/api/qr",
        json={"title": "Unauth", "url": "https://example.com"},
    )
    assert resp.status_code == 401


def test_signup_login_and_me_endpoint(client: TestClient) -> None:
    headers = _auth_headers(client)

    resp = client.get("/api/user/me", headers=headers)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["email"] == "alice@example.com"


def test_qr_lifecycle_for_user(client: TestClient) -> None:
    headers = _auth_headers(client)

    create_resp = client.post(
        "/api/qr",
        json={
            "title": "My QR",
            "url": "https://example.com",
            "foreground_color": "#123456",
            "background_color": "#ffffff",
            "size": 320,
            "padding": 12,
            "border_radius": 24,
            "overlay_text": "QF",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    assert created["title"] == "My QR"
    assert created["user_id"]
    assert created["foreground_color"] == "#123456"
    assert created["border_radius"] == 24
    assert created["png_path"]
    assert Path(created["png_path"]).exists()

    list_resp = client.get("/api/qr", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["id"] == created["id"]

    download_png = client.get(
        f"/api/qr/{created['id']}/download",
        params={"format": "png"},
        headers=headers,
    )
    assert download_png.status_code == 200
    assert download_png.headers["content-type"] == "image/png"

    delete_resp = client.delete(f"/api/qr/{created['id']}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["ok"] is True

    empty_resp = client.get("/api/qr", headers=headers)
    assert empty_resp.status_code == 200
    assert empty_resp.json() == []
