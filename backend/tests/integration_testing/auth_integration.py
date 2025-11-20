import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.deps import get_user_service
from app.services.user_service import CSVUserService
from app.utils.data_manager import CSVRepository
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


def _patch_pwd_context():
    dummy = DummyPwdContext()
    old_deps_ctx = deps_module.pwd_context
    old_auth_ctx = auth_module.pwd_context
    deps_module.pwd_context = dummy
    auth_module.pwd_context = dummy
    return dummy, old_deps_ctx, old_auth_ctx


def _restore_pwd_context(old_deps_ctx, old_auth_ctx):
    deps_module.pwd_context = old_deps_ctx
    auth_module.pwd_context = old_auth_ctx


def test_register_route_success(client, tmp_path):
    svc = make_temp_user_service(tmp_path)
    app.dependency_overrides[get_user_service] = lambda: svc

    dummy, old_deps_ctx, old_auth_ctx = _patch_pwd_context()

    try:
        response = client.post(
            "/register",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "password": "secretpw",
            },
        )

        assert response.status_code in (200, 201)
        data = response.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    finally:
        _restore_pwd_context(old_deps_ctx, old_auth_ctx)
        app.dependency_overrides.pop(get_user_service, None)


def test_register_route_username_taken(client, tmp_path):
    svc = make_temp_user_service(tmp_path)
    app.dependency_overrides[get_user_service] = lambda: svc

    dummy, old_deps_ctx, old_auth_ctx = _patch_pwd_context()

    try:
        r1 = client.post(
            "/register",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "password": "pw1",
            },
        )
        assert r1.status_code in (200, 201)

        r2 = client.post(
            "/register",
            json={
                "username": "alice",
                "email": "different@example.com",
                "password": "pw2",
            },
        )

        assert r2.status_code == 400
        assert r2.json()["detail"] == "username_taken"

    finally:
        _restore_pwd_context(old_deps_ctx, old_auth_ctx)
        app.dependency_overrides.pop(get_user_service, None)


def test_register_route_email_taken(client, tmp_path):
    svc = make_temp_user_service(tmp_path)
    app.dependency_overrides[get_user_service] = lambda: svc

    dummy, old_deps_ctx, old_auth_ctx = _patch_pwd_context()

    try:
        r1 = client.post(
            "/register",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "password": "pw1",
            },
        )
        assert r1.status_code in (200, 201)

        r2 = client.post(
            "/register",
            json={
                "username": "bob",
                "email": "alice@example.com",
                "password": "pw2",
            },
        )

        assert r2.status_code == 400
        assert r2.json()["detail"] == "email_taken"

    finally:
        _restore_pwd_context(old_deps_ctx, old_auth_ctx)
        app.dependency_overrides.pop(get_user_service, None)
