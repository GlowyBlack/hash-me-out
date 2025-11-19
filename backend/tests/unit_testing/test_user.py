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
