import csv
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import review_router


@pytest.fixture(autouse=True)
def prepare_reviews_csv_for_testing():
    """
    Reset Reviews.csv to an empty file with header before each test,
    then restore or remove it afterward.
    """
    path = review_router.service.path
    fields = review_router.service.fields

    try:
        with open(path, "r", encoding="utf-8") as f:
            original_contents = f.read()
    except FileNotFoundError:
        original_contents = None

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

    yield

    if original_contents is None:
        if os.path.exists(path):
            os.remove(path)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(original_contents)


@pytest.fixture
def client():
    """
    FastAPI TestClient for exercising the /reviews endpoints.
    """
    return TestClient(app)


def test_create_review(client):
    content = {
        "isbn": "1234567890",
        "comment": "Great book indeed",
    }

    r = client.post("/reviews/?user_id=1", json=content)
    assert r.status_code == 200

    data = r.json()
    assert data["user_id"] == 1
    assert data["isbn"] == "1234567890"
    assert data["comment"] == "Great book indeed"
    assert data["review_id"] == 1


def test_get_all_reviews_for_isbn(client):
    client.post("/reviews/?user_id=1", json={"isbn": "1111111111", "comment": "First review"})
    client.post("/reviews/?user_id=2", json={"isbn": "1111111111", "comment": "Second review"})
    client.post("/reviews/?user_id=3", json={"isbn": "2222222222", "comment": "Other book"})

    r = client.get("/reviews/1111111111")
    assert r.status_code == 200

    rows = r.json()
    assert len(rows) == 2
    user_ids = sorted(rev["user_id"] for rev in rows)
    assert user_ids == [1, 2]


def test_duplicate_review_same_user_and_isbn_returns_400(client):
    content = {
        "isbn": "3333333333",
        "comment": "Nice long review",
    }

    r1 = client.post("/reviews/?user_id=10", json=content)
    assert r1.status_code == 200

    r2 = client.post("/reviews/?user_id=10", json=content)
    assert r2.status_code == 400
    data = r2.json()
    assert "already reviewed" in data["detail"].lower()


def test_edit_review(client):
    create_resp = client.post(
        "/reviews/?user_id=5",
        json={"isbn": "4444444444", "comment": "Original text"},
    )
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
        "/reviews/?user_id=7",
        json={"isbn": "5555555555", "comment": "To be deleted"},
    )
    assert create_resp.status_code == 200
    review_id = create_resp.json()["review_id"]

    r_del = client.delete(f"/reviews/{review_id}")
    assert r_del.status_code == 200
    assert r_del.json() == {"message": "Review deleted successfully"}

    r_del2 = client.delete(f"/reviews/{review_id}")
    assert r_del2.status_code == 404
    assert r_del2.json() == {"detail": "Review not found"}
