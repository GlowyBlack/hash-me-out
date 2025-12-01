import csv
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import review_router
from app.deps import get_current_user, get_review_service
from app.services.review_service import ReviewService


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
# Fixture: temp Reviews.csv for all review routes (not a reset per test)
# -------------------------------------------------------------------
@pytest.fixture(autouse=True)
def override_review_service(tmp_path):
    """
    Override get_review_service so that all review routes
    use a Reviews.csv file under tmp_path, isolated per test run.
    """
    reviews_path = tmp_path / "Reviews.csv"

    temp_service = ReviewService()
    with open(reviews_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=temp_service.fields)
        writer.writeheader()

    def _override():
        svc = ReviewService()
        svc.path = str(reviews_path)
        return svc

    app.dependency_overrides[get_review_service] = _override
    yield
    app.dependency_overrides.pop(get_review_service, None)


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
    body = r2.json()
    assert body["detail"]["code"] == "already_reviewed"
    assert "reviewed" in body["detail"]["message"].lower()


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
