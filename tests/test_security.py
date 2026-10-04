from fastapi.testclient import TestClient

from app.main import app


def create_client():
    return TestClient(app)


def get_authenticated_client():
    client = create_client()

    response = client.get("/")

    assert response.status_code == 200

    return client


def test_protected_endpoint_accepts_valid_session():
    client = get_authenticated_client()

    response = client.get("/api/protected")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_protected_endpoint_rejects_missing_protection_token():
    client = get_authenticated_client()

    client.cookies.delete("lab_protection")

    response = client.get("/api/protected")

    assert response.status_code == 403


def test_protected_endpoint_rejects_tampered_token():
    client = get_authenticated_client()

    original_token = client.cookies.get("lab_protection")

    assert original_token is not None

    client.cookies.set(
        "lab_protection",
        "X" + original_token[1:],
    )

    response = client.get("/api/protected")

    assert response.status_code == 403


def test_protected_endpoint_rejects_wrong_user_agent():
    client = get_authenticated_client()

    response = client.get(
        "/api/protected",
        headers={
            "User-Agent": "Security-Test-Agent",
        },
    )

    assert response.status_code == 403


def test_protected_action_requires_csrf():
    client = get_authenticated_client()

    response = client.post("/api/protected-action")

    assert response.status_code == 403
    assert response.json()["detail"] == "CSRF token required"


def test_protected_action_accepts_valid_csrf():
    client = get_authenticated_client()

    csrf_token = client.cookies.get("lab_csrf")

    assert csrf_token is not None

    response = client.post(
        "/api/protected-action",
        headers={
            "X-CSRF-Token": csrf_token,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
def test_protected_action_rejects_tampered_csrf():
    client = get_authenticated_client()

    csrf_token = client.cookies.get("lab_csrf")

    assert csrf_token is not None

    tampered_csrf = "X" + csrf_token[1:]

    response = client.post(
        "/api/protected-action",
        headers={
            "X-CSRF-Token": tampered_csrf,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid CSRF token"


def test_logout_revokes_session():
    client = get_authenticated_client()

    response = client.get("/api/protected")

    assert response.status_code == 200

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["status"] == "logged_out"

    response = client.get("/api/protected")

    assert response.status_code == 403