import csv
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import book_router
from app.deps import get_current_user


# -------------------------------
# FIX: override BookService.path
# -------------------------------
@pytest.fixture(autouse=True)
def isolate_books_folder(tmp_path):
    """
    Replace the BookService path with a temporary directory
    and clear all shard files before each test.
    """

    # Override BookService's books directory
    service = book_router.service
    original_path = service.path
    service.path = tmp_path  # MUST be a folder

    # Ensure folder exists
    tmp_path.mkdir(exist_ok=True)

    # Remove any leftover files from previous tests
    for file in tmp_path.glob("*.csv"):
        file.unlink()

    yield

    # Restore original path after test
    service.path = original_path

def seed_dataset(client, admin_override):
    """Insert the sample data provided in question."""
    rows = [
        ("190415123X", "Practical Intranet Development", "John Colby"),
        ("0440207460", "Pious Deception", "Susan Dunlap"),
        ("0345362667", "Philly Stakes", "GILLIAN ROBERTS"),
        ("1591823641", "Pet Shop of Horrors", "Matsuri Akino"),
        ("1591823633", "Pet Shop of Horrors", "Matsuri Akino"),
        ("1931514186", "Peach Girl, Book 8", "Miwa Ueda"),
        ("1931514178", "Peach Girl, Book 7", "Miwa Ueda"),
        ("193151416X", "PEACH GIRL #6", "Miwa Ueda"),
        ("1931514151", "Peach Girl #5", "Miwa Ueda"),
        ("0747272522", "Pastures Nouveaux", "Wendy Holden"),
        ("0451450442", "Pyramids", "Terry Pratchett"),
        ("1880033100", "Prayer of the Warrior", "Michael H. Brown"),
        ("0553247727", "Pritikin Program for Diet and Exercise", "Nathan Pritikin"),
        ("067178501X", "PALMISTRY", "Roz Levine"),
        ("0205131999", "Perspectives on Personality", "Charles S. Carver"),
    ]

    for isbn, title, author in rows:
        client.post("/books/", json={
            "isbn": isbn,
            "book_title": title,
            "author": author
        })



# -------------------------------
# ADMIN override fixture
# -------------------------------
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

@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------
# TESTS
# -------------------------------

def test_create_book_successful(client, admin_override):

    r = client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan",
        "year_of_publication": "2005",
        "publisher": "Disney Hyperion"
    })
    assert r.status_code == 200
    data = r.json()
    assert data["isbn"] == "9780307245304"
    assert data["book_title"] == "Percy Jackson"
    assert data["author"] == "Rick Riordan"


def test_get_book_successful(client, admin_override):
    client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan"
    })

    r = client.get("/books/9780307245304")
    assert r.status_code == 200
    data = r.json()
    assert data["isbn"] == "9780307245304"
    assert data["book_title"] == "Percy Jackson"


def test_update_book_successful(client, admin_override):

    client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan"
    })

    update_response = client.put("/books/9780307245304", json={
        "book_title": "Updated Title",
        "author": "Updated Author"
    })
    assert update_response.status_code == 200

    get_response = client.get("/books/9780307245304")
    data = get_response.json()
    assert data["book_title"] == "Updated Title"
    assert data["author"] == "Updated Author"


def test_delete_book_successful(client, admin_override):

    client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan"
    })

    delete_response = client.delete("/books/9780307245304")
    assert delete_response.status_code == 200

    delete_again = client.delete("/books/9780307245304")
    assert delete_again.status_code == 404
    assert delete_again.json() == {"detail": "Book not found"}


def test_create_book_fail_missing_fields(client, admin_override):
    r = client.post("/books/", json={"isbn": "9780307245304"})
    assert r.status_code == 422


def test_get_book_fail_not_found(client):
    r = client.get("/books/DOES_NOT_EXIST")
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}


def test_update_book_fail_not_found(client, admin_override):
    r = client.put("/books/NOPE", json={
        "book_title": "No Title",
        "author": "No Author"
    })
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}


def test_delete_book_fail_not_found(client, admin_override):
    r = client.delete("/books/IDONTEXIST")
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}

# -----------------------------------------------------------
# TEST: live search for "159"
# -----------------------------------------------------------
def test_live_search_for_159(client, admin_override):
    seed_dataset(client, admin_override)

    r = client.get("/books/live-search", params={"query": "159", "limit": 10})
    assert r.status_code == 200

    data = r.json()

    # Should return EXACTLY the two ISBNs starting with 159
    returned_isbns = {item["isbn"] for item in data}

    assert returned_isbns == {"1591823641", "1591823633"}


# -----------------------------------------------------------
# TEST: full search for "159"
# -----------------------------------------------------------
def test_full_search_for_159(client, admin_override):
    seed_dataset(client, admin_override)

    r = client.get("/books/search", params={"query": "159"})
    assert r.status_code == 200

    data = r.json()
    returned_isbns = {item["isbn"] for item in data}

    # full search matches ISBN substring "159"
    assert returned_isbns == {"1591823641", "1591823633"}

    # Should NOT match books whose ISBN just contain "1" or "5"
    assert "1931514186" not in returned_isbns  # Peach Girl
    assert "190415123X" not in returned_isbns  # Practical Intranet