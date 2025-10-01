from fastapi.testclient import TestClient


def auth_headers(client: TestClient, email: str = "qrtester@example.com") -> dict:
    payload = {
        "email": email,
        "full_name": "QR Tester",
        "password": "strongpass123",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201
    resp = client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_create_qr_invalid_payload(client: TestClient) -> None:
    headers = auth_headers(client)
    resp = client.post(
        "/api/qr",
        json={
            "title": "Bad QR",
            "url": "not-a-url",
            "foreground_color": "#000000",
            "background_color": "#ffffff",
            "size": 320,
            "padding": -1,
            "border_radius": 10,
        },
        headers=headers,
    )
    assert resp.status_code == 422


def test_download_requires_authentication(client: TestClient) -> None:
    headers = auth_headers(client)
    payload = {
        "title": "Private",
        "url": "https://example.com",
        "foreground_color": "#000000",
        "background_color": "#ffffff",
        "size": 256,
        "padding": 8,
        "border_radius": 8,
    }
    create_resp = client.post("/api/qr", json=payload, headers=headers)
    assert create_resp.status_code == 201
    qr_id = create_resp.json()["id"]

    resp = client.get(f"/api/qr/{qr_id}/download")
    assert resp.status_code == 401


def test_history_only_returns_owner_items(client: TestClient) -> None:
    alice_headers = auth_headers(client)
    client.post(
        "/api/qr",
        json={
            "title": "Alice QR",
            "url": "https://alice.example.com",
            "foreground_color": "#123123",
            "background_color": "#ffffff",
            "size": 256,
            "padding": 8,
            "border_radius": 8,
        },
        headers=alice_headers,
    )

    # create second user
    headers_bob = auth_headers(client, email="bob@example.com")
    resp = client.get("/api/qr/history", headers=headers_bob)
    assert resp.status_code == 200
    assert resp.json() == []

    resp_alice = client.get("/api/qr/history", headers=alice_headers)
    assert len(resp_alice.json()) == 1

