import csv
import pytest

from app.services.user_service import CSVUserService, FIELDNAMES
from app.repositories.csv_repository import CSVRepository

service = CSVUserService(CSVRepository())


@pytest.fixture(autouse=True)
def clean_users_csv(tmp_path):
    service.path = str(tmp_path / "Users.csv")

    with open(service.path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
    yield


def test_create_user_success():
    result = service.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="hashed_pw_here",
    )

    assert isinstance(result, dict)
    assert result["username"] == "alice"
    assert result["email"] == "alice@example.com"
    assert isinstance(result["id"], int)
    assert result["id"] >= 1


def test_create_user_username_taken_raises():
    service.create_user(
        username="alice",
        email="alice1@example.com",
        password_hash="pw1",
    )

    with pytest.raises(ValueError) as excinfo:
        service.create_user(
            username="alice",
            email="alice2@example.com",
            password_hash="pw2",
        )
    assert str(excinfo.value) == "username_taken"


def test_create_user_email_taken_raises():
    service.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="pw1",
    )

    with pytest.raises(ValueError) as excinfo:
        service.create_user(
            username="bob",
            email="alice@example.com",
            password_hash="pw2",
        )
    assert str(excinfo.value) == "email_taken"


def test_get_by_username_success():
    u1 = service.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="pw1",
    )

    service.create_user(
        username="bob",
        email="bob@example.com",
        password_hash="pw2",
    )

    found = service.get_by_username("  ALIce  ")

    assert found is not None
    assert found["id"] == u1["id"]
    assert found["username"] == u1["username"]
    assert found["email"] == u1["email"]


def test_get_by_username_unknown_returns_none():
    result = service.get_by_username("nonexistent_user")
    assert result is None


def test_update_user_success():
    u1 = service.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="pw1",
    )

    service.create_user(
        username="bob",
        email="bob@example.com",
        password_hash="pw2",
    )

    updated = service.update_user(
        user_id=u1["id"],
        username="newalice",
        email="newalice@example.com",
    )

    assert updated["id"] == u1["id"]
    assert updated["username"] == "newalice"
    assert updated["email"] == "newalice@example.com"

    found = service.get_by_username("  NEWALICE  ")
    assert found is not None
    assert found["id"] == u1["id"]
    assert found["email"] == "newalice@example.com"


def test_update_user_username_taken():
    u1 = service.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="pw1",
    )
    u2 = service.create_user(
        username="bob",
        email="bob@example.com",
        password_hash="pw2",
    )

    with pytest.raises(ValueError) as excinfo:
        service.update_user(
            user_id=u2["id"],
            username="alice",
        )

    assert str(excinfo.value) == "username_taken"


def test_update_user_email_taken():
    u1 = service.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="pw1",
    )
    u2 = service.create_user(
        username="bob",
        email="bob@example.com",
        password_hash="pw2",
    )

    with pytest.raises(ValueError) as excinfo:
        service.update_user(
            user_id=u2["id"],
            email="alice@example.com",
        )

    assert str(excinfo.value) == "email_taken"


def test_update_user_not_found():
    with pytest.raises(ValueError) as excinfo:
        service.update_user(
            user_id=999,
            username="ghost",
        )

    assert str(excinfo.value) == "user_not_found"

def test_create_user_defaults_to_non_admin():
    result = service.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="pw",
    )

    assert result["is_admin"] is False
    
    
def test_set_admin_updates_flag():
    u1 = service.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="pw",
    )

    updated = service.update_user(user_id=u1["id"], is_admin=True)

    assert updated["is_admin"] is True
    
def test_create_user_preserves_username_casing():
    created = service.create_user(
        username="JanakiCute123",
        email="JaNaKi@example.com",
        password_hash="pw1",
    )

    assert created["username"] == "JanakiCute123"
    assert created["email"] == "JaNaKi@example.com"

    found = service.get_by_username("   JANAKICUTE123   ")
    assert found is not None
    assert found["id"] == created["id"]
    assert found["username"] == "JanakiCute123"

   
def test_suspend_user_sets_flag_and_time(tmp_path):
    service.path = str(tmp_path / "Users.csv")
    with open(service.path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

    admin = service.create_user(username="admin", email="admin@example.com", password_hash="pw", is_admin=True)
    user = service.create_user(username="bob", email="bob@example.com", password_hash="pw2")

    suspended = service.suspend_user(admin["id"], user["id"], duration_minutes=30)

    assert suspended["is_suspended"] == "true"
    assert suspended["suspended_until"] != ""


def test_unsuspend_user_clears_flags(tmp_path):
    service.path = str(tmp_path / "Users.csv")
    with open(service.path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

    admin = service.create_user(username="admin", email="admin@example.com", password_hash="pw", is_admin=True)
    user = service.create_user(username="bob", email="bob@example.com", password_hash="pw2")

    service.suspend_user(admin["id"], user["id"], duration_minutes=30)
    unsuspended = service.unsuspend_user(admin["id"], user["id"])

    assert unsuspended["is_suspended"] == "false"
    assert unsuspended["suspended_until"] == ""
