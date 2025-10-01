from fastapi.testclient import TestClient


def register_user(client: TestClient, email: str, password: str) -> None:
    payload = {
        "email": email,
        "full_name": "Test User",
        "password": password,
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201, resp.text


def authenticate(client: TestClient, email: str, password: str) -> dict:
    register_user(client, email, password)
    resp = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_signup_duplicate_email(client: TestClient) -> None:
    register_user(client, "dup@example.com", "password123")
    resp = client.post(
        "/api/auth/signup",
        json={
            "email": "dup@example.com",
            "full_name": "Another",
            "password": "password123",
        },
    )
    assert resp.status_code == 409
    assert "Email already registered" in resp.text


def test_login_invalid_password(client: TestClient) -> None:
    register_user(client, "bob@example.com", "password123")
    resp = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "wrongpass"},
    )
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.text


def test_logout_endpoint(client: TestClient) -> None:
    headers = authenticate(client, "logout@example.com", "password123")
    resp = client.post("/api/auth/logout", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_login_missing_user(client: TestClient) -> None:
    resp = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert resp.status_code == 401
