import csv
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import book_router
from app.deps import get_current_user


# -----------------------------------------------------
# FIX: override the BookService path with a temp folder
# -----------------------------------------------------
@pytest.fixture(autouse=True)
def isolate_books_directory(tmp_path):

    service = book_router.service

    # Save original path (a directory)
    original_path = service.path

    # Override service.path → use temp directory for shards
    service.path = tmp_path
    tmp_path.mkdir(exist_ok=True)

    # Clean the temp directory
    for file in tmp_path.glob("*.csv"):
        file.unlink()

    yield

    # Restore original path after each test
    service.path = original_path


# -----------------------------
# CLIENT FIXTURE
# -----------------------------
@pytest.fixture
def client():
    return TestClient(app)


# -----------------------------
# ADMIN OVERRIDE FIXTURE
# -----------------------------
@pytest.fixture
def admin_override():
    def override():
        return {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "is_admin": True,
        }

    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)


# -----------------------------------------------------
# TESTS
# -----------------------------------------------------

def test_create_book_successful(client, admin_override):

    r = client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan",
        "year_of_publication": "2005",
        "publisher": "Disney Hyperion",
    })

    assert r.status_code == 200
    data = r.json()

    assert data["isbn"] == "9780307245304"
    assert data["book_title"] == "Percy Jackson"
    assert data["author"] == "Rick Riordan"
    assert data["year_of_publication"] == "2005"
    assert data["publisher"] == "Disney Hyperion"


def test_get_book_successful(client, admin_override):
    client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan",
    })

    r = client.get("/books/9780307245304")
    assert r.status_code == 200
    data = r.json()

    assert data["isbn"] == "9780307245304"
    assert data["book_title"] == "Percy Jackson"
    assert data["author"] == "Rick Riordan"


def test_update_book_successful(client, admin_override):
    client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan",
    })

    r_update = client.put("/books/9780307245304", json={
        "book_title": "Updated Title",
        "author": "Updated Author",
    })

    assert r_update.status_code == 200

    r_get = client.get("/books/9780307245304")
    data = r_get.json()

    assert data["book_title"] == "Updated Title"
    assert data["author"] == "Updated Author"


def test_delete_book_successful(client, admin_override):
    client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan",
    })

    r_delete = client.delete("/books/9780307245304")
    assert r_delete.status_code == 200

    r_delete_again = client.delete("/books/9780307245304")
    assert r_delete_again.status_code == 404
    assert r_delete_again.json() == {"detail": "Book not found"}


def test_create_book_fail_missing_required_fields(client, admin_override):
    r = client.post("/books/", json={"isbn": "9780307245304"})
    assert r.status_code == 422


def test_create_book_invalid_isbn_returns_422(client, admin_override):

    r_short = client.post("/books/", json={
        "isbn": "11",
        "book_title": "Bad ISBN",
        "author": "Someone",
    })
    assert r_short.status_code == 422

    r_long = client.post("/books/", json={
        "isbn": "1" * 40,
        "book_title": "Bad ISBN",
        "author": "Someone",
    })
    assert r_long.status_code == 422


def test_get_book_fail_not_found(client):
    r = client.get("/books/DOES_NOT_EXIST")
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}


def test_update_book_fail_not_found(client, admin_override):
    r = client.put("/books/NOPE", json={
        "book_title": "Should Not Update",
        "author": "Nobody",
    })
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}


def test_delete_book_fail_not_found(client, admin_override):
    r = client.delete("/books/IDONTEXIST")
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}
