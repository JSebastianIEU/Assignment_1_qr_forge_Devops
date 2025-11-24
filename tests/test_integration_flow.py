import base64
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from models import QRItem, User


def _auth_headers(client: TestClient) -> dict:
    signup_payload = {
        "email": "flow@example.com",
        "full_name": "Flow User",
        "password": "complexpass123",
    }
    resp = client.post("/api/auth/signup", json=signup_payload)
    assert resp.status_code == 201, resp.text

    login_payload = {"email": signup_payload["email"], "password": signup_payload["password"]}
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_full_qr_lifecycle(client: TestClient, engine, tmp_path: Path) -> None:
    headers = _auth_headers(client)
    payload = {
        "title": "Lifecycle",
        "url": "https://example.com",
        "foreground_color": "#111111",
        "background_color": "#ffffff",
        "size": 256,
        "padding": 12,
        "border_radius": 16,
    }

    preview = client.post("/api/qr/preview", json=payload, headers=headers)
    assert preview.status_code == 200, preview.text
    base64.b64decode(preview.json()["png_data"])

    create_resp = client.post("/api/qr", json=payload, headers=headers)
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()

    with Session(engine) as session:
        record = session.exec(select(QRItem)).first()
        assert record is not None
        assert Path(record.svg_path).exists()
        assert Path(record.png_path).exists()

    svg_download = client.get(f"/api/qr/{created['id']}/download", headers=headers)
    assert svg_download.status_code == 200
    assert svg_download.headers["content-type"] == "image/svg+xml"

    png_download = client.get(
        f"/api/qr/{created['id']}/download",
        params={"format": "png"},
        headers=headers,
    )
    assert png_download.status_code == 200
    assert png_download.headers["content-type"] == "image/png"

    delete_resp = client.delete(f"/api/qr/{created['id']}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["ok"] is True

    with Session(engine) as session:
        assert session.exec(select(QRItem)).all() == []
        assert session.exec(select(User)).first() is not None
