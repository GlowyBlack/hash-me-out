from unittest.mock import patch
from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_create_book_success():
    request = {"book_title": "Percy Jackson", "author": "Rick Riordan", "isbn": "9780307245304", "year_of_publication": "2005",
        "publisher": "Disney Hyperion",}
    with patch("app.routers.book_router.service.create_book", return_value = {
    "book_title": "Percy Jackson",
    "author": "Rick Riordan",
    "isbn": "9780307245304",
    "year_of_publication": "2005",
    "publisher": "Disney Hyperion"
    }):
        r = client.post("/books/", json=request)
        assert r.status_code == 200
        data = r.json()
        # print(data)
        assert data["book_title"] == "Percy Jackson"
        assert data["author"] == "Rick Riordan"
        assert data["isbn"] == "9780307245304"
    
def test_create_book_fail_duplicate():
    with patch("app.routers.book_router.service.create_book", side_effect=ValueError("Book already exists in the database.")):
        r = client.post("/books/", json={
            "book_title": "Percy Jackson",
            "author": "Rick Riordan",
            "isbn": "9780307245304"})
        assert r.status_code == 400
        assert r.json() == {"detail": "Book already exists in the database."}


