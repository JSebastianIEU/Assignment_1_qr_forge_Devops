from fastapi.testclient import TestClient


def test_signup_invalid_email(client: TestClient) -> None:
    payload = {
        "email": "not-an-email",
        "full_name": "Bad",
        "password": "password123",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 422


def test_login_missing_password(client: TestClient) -> None:
    # Missing password field should return 422
    resp = client.post("/api/auth/login", json={"email": "a@b.com"})
    assert resp.status_code == 422
