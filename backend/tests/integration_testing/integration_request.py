import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_request_route_success():
    request = {"book_title": "Percy Jackson", "author": "Rick Riordan", "isbn": "9780307245304"}
    r = client.post("/requests/?user_id=1", json=request)
    assert r.status_code == 200
    data = r.json()
    assert data["Book Title"] == "Percy Jackson"
    assert data["UserID"] == 1
    

# def test_search_route_one_result():
#     r = client.get("/search/Nonexistent")
#     assert r.status_code == 200
#     assert r.json() == {"results":[{"isbn":"0156659751","title":"The Nonexistent Knight and The Cloven Viscount","author":"Italo Calvino","year":"1977","publisher":"Harcourt"}]}
    
