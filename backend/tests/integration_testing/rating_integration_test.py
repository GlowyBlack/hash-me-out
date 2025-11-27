import csv
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import rating_router
from app.deps import get_current_user


@pytest.fixture(autouse=True)
def prepare_csv_for_testing():
    """
    Integration fixture for ratings, will reset Ratings.csv before each test and restore it afterward.
    """
    path = rating_router.service.ratings_path

    try:
        with open(path, "r", encoding="utf-8") as f:
            original_contents = f.read()
    except FileNotFoundError:
        original_contents = None

    # Reset file with header for each test
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rating_router.service.fields)
        writer.writeheader()

    yield

    # Restore original file after test
    if original_contents is None:
        if os.path.exists(path):
            os.remove(path)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(original_contents)


@pytest.fixture
def client():
    """
    FastAPI test client for /ratings endpoints.
    """
    return TestClient(app)


# ---------------------------------------------------------
# User override fixture (simulates ANY logged-in user)
# ---------------------------------------------------------
@pytest.fixture
def as_user1():
    """
    Override get_current_user to simulate user with id=1.
    """
    def override():
        return {"id": 1, "username": "u1", "email": "u1@test.com", "is_admin": False}

    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def as_user2():
    """
    Override get_current_user to simulate user with id=2.
    """
    def override():
        return {"id": 2, "username": "u2", "email": "u2@test.com", "is_admin": False}

    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def as_user3():
    """
    Override get_current_user to simulate user with id=3.
    """
    def override():
        return {"id": 3, "username": "u3", "email": "u3@test.com", "is_admin": False}

    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)



# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

def test_add_rating(client, as_user1):
    r = client.post(
        "/ratings/books/12345",
        json={"rating": 4},
    )
    assert r.status_code == 200
    assert r.json() == {"user_id": 1, "isbn": "12345", "rating": 4}

    r2 = client.get("/ratings/users/1/books/12345")
    assert r2.status_code == 200
    assert r2.json()["rating"] == 4


def test_update_rating_and_average(client, as_user2):
    client.post("/ratings/books/999", json={"rating": 2})

    r = client.post("/ratings/books/999", json={"rating": 5})
    assert r.status_code == 200
    assert r.json()["rating"] == 5

    r2 = client.get("/ratings/books/999/average")
    assert r2.status_code == 200
    assert r2.json() == {"isbn": "999", "avg_rating": 5.0, "count": 1}


def test_delete_rating(client, as_user3):
    client.post("/ratings/books/ABC", json={"rating": 3})

    r = client.delete("/ratings/?isbn=ABC")
    assert r.status_code == 204

    r2 = client.delete("/ratings/?isbn=ABC")
    assert r2.status_code == 404
    assert r2.json() == {"detail": "Rating not found"}


# ---------------------------------------------------------------------------
# Aggregation tests
# ---------------------------------------------------------------------------
def test_avg_rating_multiple_users(client, as_user1):
    client.post("/ratings/books/555", json={"rating": 4})

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2, "username": "u2", "email": "u2@test.com", "is_admin": False
    }
    client.post("/ratings/books/555", json={"rating": 8})

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 3, "username": "u3", "email": "u3@test.com", "is_admin": False
    }
    client.post("/ratings/books/555", json={"rating": 6})

    app.dependency_overrides.pop(get_current_user, None)

    r = client.get("/ratings/books/555/average")
    assert r.status_code == 200
    assert r.json() == {"isbn": "555", "avg_rating": 6.0, "count": 3}

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1, "username": "u1", "email": "u1@test.com", "is_admin": False
    }
    r2 = client.post("/ratings/books/123", json={"rating": -1})
    assert r2.status_code == 422

    app.dependency_overrides.pop(get_current_user, None)


def test_get_all_and_get_by_isbn(client, as_user1):
    client.post("/ratings/books/111", json={"rating": 3})

    app.dependency_overrides[get_current_user] = lambda: {"id": 2, "username": "u2", "email": "u2@test.com", "is_admin": False}
    client.post("/ratings/books/111", json={"rating": 7})

    app.dependency_overrides[get_current_user] = lambda: {"id": 1, "username": "u1", "email": "u1@test.com", "is_admin": False}
    client.post("/ratings/books/222", json={"rating": 5})

    app.dependency_overrides.pop(get_current_user, None)

    r_all = client.get("/ratings/")
    assert r_all.status_code == 200
    data = r_all.json()
    assert len(data) == 3
    assert {d["isbn"] for d in data} == {"111", "222"}

    r_isbn = client.get("/ratings/books/111")
    assert r_isbn.status_code == 200
    isbn_data = r_isbn.json()
    assert len(isbn_data) == 2
    user_ids = {d["user_id"] for d in isbn_data}
    assert user_ids == {1, 2}


def test_avg_rating_when_no_ratings(client):
    r = client.get("/ratings/books/NO_RATINGS/average")
    assert r.status_code == 200
    assert r.json() == {"isbn": "NO_RATINGS", "avg_rating": 0.0, "count": 0}


# ---------------------------------------------------------------------------
# Equivalence/boundary tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", [11, -1])
def test_create_rating_invalid_value_returns_422(client, as_user1, value):
    r = client.post("/ratings/books/123", json={"rating": value})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Quick, extra exception handling test
# ---------------------------------------------------------------------------

def test_get_user_rating_not_found_returns_null(client):
    r = client.get("/ratings/users/999/books/UNKNOWN")
    assert r.status_code == 200
    assert r.json() is None
