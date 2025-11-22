import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.deps import get_user_service, get_current_user
from app.services.user_service import CSVUserService
from app.repositories.csv_repository import CSVRepository
import app.deps as deps_module
import app.routers.auth as auth_module


class DummyPwdContext:
    def hash(self, password: str) -> str:
        return "hashed:" + password

    def verify(self, password: str, hashed: str) -> bool:
        return hashed == "hashed:" + password


@pytest.fixture
def client():
    return TestClient(app)


def make_temp_user_service(tmp_path):
    users_csv = tmp_path / "users.csv"
    repo = CSVRepository()
    return CSVUserService(repo=repo, path=str(users_csv))


@pytest.fixture
def dummy_pwd_context():
    dummy = DummyPwdContext()
    old_deps_ctx = deps_module.pwd_context
    old_auth_ctx = auth_module.pwd_context

    deps_module.pwd_context = dummy
    auth_module.pwd_context = dummy

    try:
        yield dummy
    finally:
        deps_module.pwd_context = old_deps_ctx
        auth_module.pwd_context = old_auth_ctx


@pytest.fixture
def temp_user_service(tmp_path):
    svc = make_temp_user_service(tmp_path)
    app.dependency_overrides[get_user_service] = lambda: svc
    try:
        yield svc
    finally:
        app.dependency_overrides.pop(get_user_service, None)


def test_register_route_success(client, temp_user_service, dummy_pwd_context):
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secretpw",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_route_username_taken(client, temp_user_service, dummy_pwd_context):
    r1 = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "pw1",
        },
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "different@example.com",
            "password": "pw2",
        },
    )

    assert r2.status_code == 400
    assert r2.json()["detail"] == "username_taken"


def test_register_route_email_taken(client, temp_user_service, dummy_pwd_context):
    r1 = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "pw1",
        },
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/auth/register",
        json={
            "username": "bob",
            "email": "alice@example.com",
            "password": "pw2",
        },
    )

    assert r2.status_code == 400
    assert r2.json()["detail"] == "email_taken"


def test_login_route_success_returns_token(client, temp_user_service, dummy_pwd_context):
    svc = temp_user_service
    dummy = dummy_pwd_context

    svc.create_user(
        username="alice",
        email="alice@example.com",
        password_hash=dummy.hash("pw1"),
    )

    response = client.post(
        "/auth/token",
        data={"username": "alice", "password": "pw1"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_route_wrong_password_401(client, temp_user_service, dummy_pwd_context):
    svc = temp_user_service
    dummy = dummy_pwd_context

    svc.create_user(
        username="alice",
        email="alice@example.com",
        password_hash=dummy.hash("correctpw"),
    )

    response = client.post(
        "/auth/token",
        data={"username": "alice", "password": "wrongpw"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "invalid_credentials"


def test_login_route_unknown_user_401(client, temp_user_service, dummy_pwd_context):
    response = client.post(
        "/auth/token",
        data={"username": "ghost", "password": "whatever"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "invalid_credentials"


def test_me_with_valid_token_returns_user(client):
    def override_current_user():
        return {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "is_admin": False,
        }

    app.dependency_overrides[get_current_user] = override_current_user

    try:
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer faketoken"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"


def test_me_with_no_token_401(client):
    app.dependency_overrides.pop(get_current_user, None)
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token_401(client):
    app.dependency_overrides.pop(get_current_user, None)
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == 401


def test_admin_can_access_users(client, temp_user_service, dummy_pwd_context):
    svc = temp_user_service
    dummy = dummy_pwd_context

    svc.create_user(
        username="admin",
        email="admin@example.com",
        password_hash=dummy.hash("pw"),
        is_admin=True,
    )

    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "pw"},
    )

    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    resp = client.get(
        "/auth/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(u["username"] == "admin" and u["is_admin"] for u in data)


def test_non_admin_blocked_from_admin_users(client, temp_user_service, dummy_pwd_context):
    svc = temp_user_service
    dummy = dummy_pwd_context

    svc.create_user(
        username="bob",
        email="bob@example.com",
        password_hash=dummy.hash("pw"),
        is_admin=False,
    )

    login_resp = client.post(
        "/auth/token",
        data={"username": "bob", "password": "pw"},
    )

    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    resp = client.get(
        "/auth/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 403
    body = resp.json()
    assert body["detail"] == "Admin privileges required"

def test_admin_can_suspend_user(client, temp_user_service, dummy_pwd_context):
    svc = temp_user_service
    dummy = dummy_pwd_context

    svc.create_user(username="admin", email="admin@example.com", password_hash=dummy.hash("pw"), is_admin=True)
    user = svc.create_user(username="bob", email="bob@example.com", password_hash=dummy.hash("pw2"))

    login_resp = client.post("/auth/token", data={"username": "admin", "password": "pw"})
    token = login_resp.json()["access_token"]

    resp = client.post(
        f"/auth/suspend/{user['id']}?duration_minutes=60",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert "suspended_until" in resp.json()


def test_suspended_user_cannot_login(client, temp_user_service, dummy_pwd_context):
    svc = temp_user_service
    dummy = dummy_pwd_context

    svc.create_user(username="admin", email="admin@example.com", password_hash=dummy.hash("pw"), is_admin=True)
    user = svc.create_user(username="bob", email="bob@example.com", password_hash=dummy.hash("pw2"))

    login_resp = client.post("/auth/token", data={"username": "admin", "password": "pw"})
    admin_token = login_resp.json()["access_token"]

    client.post(
        f"/auth/suspend/{user['id']}?duration_minutes=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    r = client.post("/auth/token", data={"username": "bob", "password": "pw2"})
    assert r.status_code == 403
    assert "suspended" in r.json()["detail"].lower()


def test_admin_can_unsuspend_user(client, temp_user_service, dummy_pwd_context):
    svc = temp_user_service
    dummy = dummy_pwd_context

    svc.create_user(username="admin", email="admin@example.com", password_hash=dummy.hash("pw"), is_admin=True)
    user = svc.create_user(username="bob", email="bob@example.com", password_hash=dummy.hash("pw2"))

    login_resp = client.post("/auth/token", data={"username": "admin", "password": "pw"})
    admin_token = login_resp.json()["access_token"]

    client.post(
        f"/auth/suspend/{user['id']}?duration_minutes=30",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    resp = client.post(
        f"/auth/unsuspend/{user['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 200

    login_resp = client.post("/auth/token", data={"username": "bob", "password": "pw2"})
    assert login_resp.status_code == 200
