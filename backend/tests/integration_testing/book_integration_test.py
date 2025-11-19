import csv
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import book_router

@pytest.fixture(autouse=True)
def prepare_csv_for_testing(tmp_path):
    path = book_router.service.path

    try:
        with open(path, "r", encoding="utf-8") as f:
            original_contents = f.read()
    except FileNotFoundError:
        original_contents = None 
    
    with open(path, "w", newline="", encoding="utf-8") as f:
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
            ]
        )
        writer.writeheader()
    
    yield

    if original_contents is None:
        import os
        if os.path.exists(path):
            os.remove(path)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(original_contents)

@pytest.fixture
def client():
    return TestClient(app)

def test_create_book(client):

    r = client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson", 
        "author": "Rick Riordan", 
        "year_of_publication": "2005",
        "publisher": "Disney Hyperion"
    })
    assert r.status_code == 200
    data = r.json()
    # print(data)
    assert data["isbn"] == "9780307245304"
    assert data["book_title"] == "Percy Jackson"
    assert data["author"] == "Rick Riordan"
    
    
def test_get_book(client):
    # first, create the book
    client.post("/books/", json={
        "isbn": "9780307245304",
        "book_title": "Percy Jackson",
        "author": "Rick Riordan"
    })

    # then retrieve it
    r = client.get("/books/9780307245304")
    assert r.status_code == 200
    data = r.json()
    assert data["isbn"] == "9780307245304"
    assert data["book_title"] == "Percy Jackson"

# update, delete

