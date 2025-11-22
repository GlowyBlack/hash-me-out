import csv
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import book_router


@pytest.fixture(autouse=True)
def prepare_csv_for_testing():
    """
    Integration fixture for Book endpoints.
    """
    path = book_router.service.path

    try:
        with open(path, "r", encoding="latin-1") as f:
            original_contents = f.read()
    except FileNotFoundError:
        original_contents = None

    with open(path, "w", newline="", encoding="latin-1") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ISBN",
                "Book-Title",
                "Book-Author",
                "Year-Of-Publication",
                "Publisher",
                "Image-URL-S",
                "Image-URL-M",
                "Image-URL-L",
            ],
            delimiter=";", 
        )
        writer.writeheader()

    yield

    if original_contents is None:
        if os.path.exists(path):
            os.remove(path)
    else:
        with open(path, "w", encoding="latin-1") as f:
            f.write(original_contents)


@pytest.fixture
def client():
    """
    FastAPI test client for exercising the /books API endpoints.
    """
    return TestClient(app)


# ---------------------------------------------------------------------------
# Basic integration test for books
# ---------------------------------------------------------------------------

def test_create_book_successful(client):
    payload = {
        "isbn": "9780307245304",
        "book_title": "Percy Jackson and the Lightning Thief",
        "author": "Rick Riordan",
        "year_of_publication": "2005",
        "publisher": "Disney Hyperion",
    }

    r = client.post("/books/", json=payload)
    assert r.status_code == 200
    data = r.json()

    assert data["isbn"] == payload["isbn"]
    assert data["book_title"] == payload["book_title"]
    assert data["author"] == payload["author"]
    assert data["year_of_publication"] == payload["year_of_publication"]
    assert data["publisher"] == payload["publisher"]


def test_get_book_successful(client):
    payload = {
        "isbn": "9780307245304",
        "book_title": "Percy Jackson and the Lightning Thief",
        "author": "Rick Riordan",
    }
    client.post("/books/", json=payload)

    r = client.get("/books/9780307245304")
    assert r.status_code == 200
    data = r.json()

    assert data["isbn"] == payload["isbn"]
    assert data["book_title"] == payload["book_title"]
    assert data["author"] == payload["author"]


def test_update_book_successful(client):
    create_payload = {
        "isbn": "9780307245304",
        "book_title": "Percy Jackson and the Lightning Thief",
        "author": "Rick Riordan",
    }
    r_create = client.post("/books/", json=create_payload)
    assert r_create.status_code == 200

    update_payload = {
        "book_title": "Updated Title",
        "author": "Updated Author",
    }

    r_update = client.put("/books/9780307245304", json=update_payload)
    assert r_update.status_code == 200

    r_get = client.get("/books/9780307245304")
    assert r_get.status_code == 200
    data = r_get.json()
    assert data["isbn"] == "9780307245304"
    assert data["book_title"] == "Updated Title"
    assert data["author"] == "Updated Author"


def test_delete_book_successful(client):
    """
    Create and then delete a book
    First delete should have 204.
    Second delete exercises exception handling and should return 404.
    """
    payload = {
        "isbn": "9780307245304",
        "book_title": "Percy Jackson and the Lightning Thief",
        "author": "Rick Riordan",
    }
    client.post("/books/", json=payload)

    r_delete = client.delete("/books/9780307245304")
    assert r_delete.status_code == 204

    r_delete_again = client.delete("/books/9780307245304")
    assert r_delete_again.status_code == 404
    assert r_delete_again.json() == {"detail": "Book not found"}


# ---------------------------------------------------------------------------
# Validation + equivalence/boundary-based tests
# ---------------------------------------------------------------------------

def test_create_book_fail_missing_required_fields(client):
    """
    Request body missing required fields should trigger 422 validation error.
    """
    r = client.post("/books/", json={"isbn": "9780307245304"})
    assert r.status_code == 422


def test_create_book_invalid_isbn_returns_422(client):
    """
    Equivalence / boundary-style test for ISBN validation. Partitions are:
    - Valid ISBNs (10 or 13 digits) → accepted
    - Invalid ISBNs (other lengths) → 422
    """

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


# ---------------------------------------------------------------------------
# Exception handling: non-existent resources
# ---------------------------------------------------------------------------

def test_get_book_fail_not_found(client):
    r = client.get("/books/DOES_NOT_EXIST")
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}


def test_update_book_fail_not_found(client):
    update_payload = {
        "book_title": "Should Not Update",
        "author": "Nobody",
    }
    r = client.put("/books/NOPE", json=update_payload)
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}


def test_delete_book_fail_not_found(client):
    r = client.delete("/books/IDONTEXIST")
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}
