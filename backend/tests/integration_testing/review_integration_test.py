import csv
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import review_router
from app.deps import get_current_user


# -------------------------------------------------------------------
# Fixture: ALL tests run as logged-in user with id = 1
# -------------------------------------------------------------------
@pytest.fixture(autouse=True)
def override_user():
    """
    Review routes use get_current_user.
    This fixture makes EVERY test run as user_id = 1.
    """
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "testuser",
        "email": "test@test.com",
        "is_admin": False,
    }
    yield
    app.dependency_overrides.pop(get_current_user, None)


# -------------------------------------------------------------------
# Reset Reviews.csv before each test
# -------------------------------------------------------------------
@pytest.fixture(autouse=True)
def prepare_reviews_csv_for_testing():
    path = review_router.service.path
    fields = review_router.service.fields

    # Backup original
    try:
        with open(path, "r", encoding="utf-8") as f:
            original_contents = f.read()
    except FileNotFoundError:
        original_contents = None

    # Create clean file for testing
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

    yield

    # Restore after test
    if original_contents is None:
        if os.path.exists(path):
            os.remove(path)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(original_contents)


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_create_review(client):
    content = {"comment": "Great book indeed"}

    r = client.post("/reviews/?isbn=1234567890", json=content)
    assert r.status_code == 200

    data = r.json()
    assert data["user_id"] == 1
    assert data["isbn"] == "1234567890"
    assert data["comment"] == "Great book indeed"
    assert data["review_id"] == 1

def test_get_all_reviews_for_isbn(client):

    # user 1
    client.post("/reviews/?isbn=1111111111", json={"comment": "First review"})

    # user 2
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2,
        "username": "u2",
        "email": "u2@test.com",
        "is_admin": False,
    }
    client.post("/reviews/?isbn=1111111111", json={"comment": "Second review"})

    # user 3
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 3,
        "username": "u3",
        "email": "u3@test.com",
        "is_admin": False,
    }
    client.post("/reviews/?isbn=2222222222", json={"comment": "Other book"})

    # restore user 1
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "u1",
        "email": "u1@test.com",
        "is_admin": False,
    }

    r = client.get("/reviews/1111111111")
    rows = r.json()

    assert len(rows) == 2
    assert sorted([r["user_id"] for r in rows]) == [1, 2]


def test_duplicate_review_same_user_and_isbn_returns_400(client):
    r1 = client.post("/reviews/?isbn=3333333333", json={"comment": "Nice long review"})
    assert r1.status_code == 200

    r2 = client.post("/reviews/?isbn=3333333333", json={"comment": "Nice long review"})
    assert r2.status_code == 400
    assert "already" in r2.json()["detail"].lower()


def test_edit_review(client):
    create_resp = client.post("/reviews/?isbn=4444444444", json={"comment": "Original text"})
    assert create_resp.status_code == 200

    review_id = create_resp.json()["review_id"]

    update_content = {"comment": "Updated comment here"}

    r_edit = client.put(f"/reviews/{review_id}", json=update_content)
    assert r_edit.status_code == 200

    updated = r_edit.json()
    assert updated["review_id"] == review_id
    assert updated["comment"] == "Updated comment here"


def test_delete_review(client):
    create_resp = client.post(
        "/reviews/?isbn=5555555555",
        json={"comment": "To be deleted"},
    )
    assert create_resp.status_code == 200

    review_id = create_resp.json()["review_id"]

    r_del = client.delete(f"/reviews/{review_id}")
    assert r_del.status_code == 200
    assert r_del.json() == {"message": "Review deleted successfully"}

    r_del2 = client.delete(f"/reviews/{review_id}")
    assert r_del2.status_code == 404
    assert r_del2.json() == {"detail": "Review not found"}
