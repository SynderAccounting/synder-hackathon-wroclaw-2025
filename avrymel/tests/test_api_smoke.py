import pytest
import httpx

BASE_URL = "http://localhost:8000/api/v1"

@pytest.fixture(scope="session")
def client():
    return httpx.Client(base_url=BASE_URL)

@pytest.fixture(scope="session")
def test_user():
    return {
        "username": "pytest_user",
        "email": "pytest_user@example.com",
        "password": "TestPass123!"
    }

def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200

def test_register_user(client, test_user):
    r = client.post("/users/register", json=test_user)
    # 422 = validation, 201 = created, 409 = conflict (already exists)
    assert r.status_code in (200, 201, 409), f"Unexpected status: {r.status_code}, {r.text}"

@pytest.fixture(scope="session")
def auth_token(client, test_user):
    # логинимся по username
    r = client.post("/users/login", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json().get("access_token") or r.json().get("token")
    assert token, f"No token returned: {r.text}"
    return token

def test_get_me(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.get("/users/me", headers=headers)
    assert r.status_code == 200, f"Get me failed: {r.text}"

def test_logout(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/users/logout", headers=headers)
    assert r.status_code in (200, 204), f"Logout failed: {r.text}"

@pytest.mark.parametrize("endpoint", [
    "/transactions",
    "/connectors",
    "/dashboard/metrics",
])
def test_protected_routes_require_auth(client, endpoint):
    r = client.get(endpoint)
    assert r.status_code in (401, 403), f"Endpoint {endpoint} should require auth"

@pytest.mark.parametrize("endpoint", [
    "/transactions",
    "/connectors",
    "/dashboard/metrics",
])
def test_protected_routes_with_auth(client, auth_token, endpoint):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.get(endpoint, headers=headers)
    assert r.status_code in (200, 204), f"Authorized request failed for {endpoint}: {r.text}"
