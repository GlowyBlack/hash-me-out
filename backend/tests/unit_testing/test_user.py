import csv
import pytest

from app.services.user_service import CSVUserService, FIELDNAMES
from app.utils.data_manager import CSVRepository

_repo = CSVRepository()
service = CSVUserService(_repo)


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

