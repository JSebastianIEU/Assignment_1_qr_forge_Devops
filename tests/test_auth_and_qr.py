import base64

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from models import QRItem, User


def _auth_headers(client: TestClient, email: str = "alice@example.com", password: str = "secret123") -> dict:
    signup_payload = {
        "email": email,
        "full_name": "Alice Example",
        "password": password,
    }
    resp = client.post("/api/auth/signup", json=signup_payload)
    assert resp.status_code == 201, resp.text

    login_payload = {"email": email, "password": password}
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


def test_preview_requires_auth(client: TestClient) -> None:
    resp = client.post(
        "/api/qr/preview",
        json={
            "title": "No auth",
            "url": "https://example.com",
            "foreground_color": "#000000",
            "background_color": "#ffffff",
            "size": 256,
            "padding": 8,
            "border_radius": 8,
        },
    )
    assert resp.status_code == 401


def test_preview_and_lifecycle(client: TestClient) -> None:
    headers = _auth_headers(client)

    payload = {
        "title": "My QR",
        "url": "https://example.com",
        "foreground_color": "#123456",
        "background_color": "transparent",
        "size": 320,
        "padding": 12,
        "border_radius": 24,
    }
    preview_resp = client.post("/api/qr/preview", json=payload, headers=headers)
    assert preview_resp.status_code == 200, preview_resp.text
    preview = preview_resp.json()
    assert preview["png_data"]
    base64.b64decode(preview["png_data"])

    create_resp = client.post("/api/qr", json=payload, headers=headers)
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    assert created["background_color"] == "transparent"

    list_resp = client.get("/api/qr", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1

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


def test_delete_user_removes_qrs(client: TestClient, engine) -> None:
    headers = _auth_headers(client)
    payload = {
        "title": "Keep",
        "url": "https://example.com",
        "foreground_color": "#000000",
        "background_color": "#ffffff",
        "size": 256,
        "padding": 8,
        "border_radius": 12,
    }
    resp = client.post("/api/qr", json=payload, headers=headers)
    assert resp.status_code == 201

    del_resp = client.delete("/api/user/me", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["ok"] is True

    with Session(engine) as session:
        assert session.exec(select(User)).first() is None
        assert session.exec(select(QRItem)).all() == []


def test_update_profile_and_password_flow(client: TestClient) -> None:
    headers = _auth_headers(client, email="bob@example.com", password="initial123")

    update_resp = client.patch(
        "/api/user/me",
        json={"full_name": "Bob Builder", "password": "newsecret456"},
        headers=headers,
    )
    assert update_resp.status_code == 200, update_resp.text
    updated = update_resp.json()
    assert updated["full_name"] == "Bob Builder"

    me_resp = client.get("/api/user/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["full_name"] == "Bob Builder"

    old_login = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "initial123"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "newsecret456"},
    )
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()
