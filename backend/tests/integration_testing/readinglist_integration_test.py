import csv
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import readinglist_router
from fastapi import HTTPException
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def prepare_csv_for_testing(tmp_path):
    path = readinglist_router.service.path

    try:
        with open(path, "r", encoding="utf-8") as f:
            original_contents = f.read()
    except FileNotFoundError:
        original_contents = None 
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ListID",
                "UserID",
                "Name",
                "ISBNs",
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
        
def test_create_readinglist_route_failure(client):
    request = {"name": " "}
    r = client.post("/readinglist/",
                    params={"user_id":1}, 
                    json=request)   
    assert r.status_code == 422
    assert "Readinglist Name must be at least 1 letter" in str(r.json())   
    return

def test_create_readinglist_route_success(client):
    request = {"name": "My New ReadingList"}
    r = client.post(
        "/readinglist/",
        params={"user_id": 1},
        json=request,
    )    
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "My New ReadingList"
    assert data["books"] == []

def test_delete_readinglist_route_failure(client):
    r = client.delete(
        "/readinglist/999", 
        params={"user_id": 1}
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "ReadingList not found"
    
def test_delete_readinglist_route_success(client):
    create_result = client.post(
        "/readinglist/",
        params={"user_id": 1}, 
        json={"name": "Test List"}
    )
    assert create_result.status_code == 200
    created = create_result.json()
    list_id = created["list_id"]  

    delete_result = client.delete(
        f"/readinglist/{list_id}",
        params={"user_id": 1}
    )
    assert delete_result.status_code == 200
    assert delete_result.json()["message"] == "ReadingList deleted successfully"

    delete_again = client.delete(
        f"/readinglist/{list_id}"
        , params={"user_id": 1}
    )
    assert delete_again.status_code == 404
    assert delete_again.json()["detail"] == "ReadingList not found"
