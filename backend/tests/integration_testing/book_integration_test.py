import csv
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import book_router

@pytest.fixture(autouse=True)
def prepare_csv_for_testing(tmp_path):
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
             delimiter=";" 
        )
        writer.writeheader()

    yield

    if original_contents is None:
        import os
        if os.path.exists(path):
            os.remove(path)
    else:
        with open(path, "w", encoding="latin-1") as f:
            f.write(original_contents)

@pytest.fixture
def client():
    return TestClient(app)

def test_create_book_successful(client):

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
    
    
def test_get_book_successful(client):
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


def test_update_book_successful(client):

    create_response = client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan"
    })

    assert create_response.status_code == 200
    
    update_response = client.put("/books/9780307245304", json={
        "isbn": "9780307245304",
        "book_title": "Updated Title",
        "author": "Updated Author"
    })
    
    assert update_response.status_code == 200

    get_response = client.get("/books/9780307245304")
    data = get_response.json()

    assert get_response.status_code == 200
    assert data["isbn"] == "9780307245304"
    assert data["book_title"] == "Updated Title"
    assert data["author"] == "Updated Author"

def test_delete_book_successful(client):

    client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan"
    })

    delete_response = client.delete("/books/9780307245304")
    assert delete_response.status_code == 204

    delete_again_response = client.delete("/books/9780307245304")
    assert delete_again_response.status_code == 404
    assert delete_again_response.json() == {"detail": "Book not found"} 

def test_create_book_fail_missing_fields(client):
    r = client.post("/books/", json={
        "isbn": "9780307245304",
    })
    assert r.status_code == 422

def test_get_book_fail_not_found(client):
    r = client.get("/books/DOES_NOT_EXIST")
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}

def test_update_book_fail_not_found(client):
    update_response = client.put("/books/NOPE", json={
        "isbn": "NOPE",
        "book_title": "No Title",
        "author": "No Author"
    })
    assert update_response.status_code == 404
    assert update_response.json() == {"detail": "Book not found"}

def test_delete_book_fail_not_found(client):
    r = client.delete("/books/IDONTEXIST")
    assert r.status_code == 404
    assert r.json() == {"detail": "Book not found"}
