from unittest.mock import patch
from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
        
def test_create_readinglist_route_failure():
    request = {"name": " "}
    with patch("app.routers.readinglist_router.service.create_list", return_value=False):
        r = client.post("/readinglist/?user_id=1", json=request)
        assert r.status_code == 422
        assert "Readinglist Name must be at least 1 letter" in str(r.json())    

def test_create_readinglist_route_success():
    request = {"name": "My New ReadingList"}
    with patch("app.routers.readinglist_router.service.create_list", return_value={
    "list_id": 1,
    "user_id": 1,
    "name": "My New ReadingList",
    "books": []
    }):
        r = client.post("/readinglist/?user_id=1", json=request)
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "My New ReadingList"
        assert data["books"] == []

def test_delete_readinglist_route_failure():
    with patch("app.routers.readinglist_router.service.delete_list", return_value=False):
        r = client.delete("/readinglist/1?user_id=1")
        assert r.status_code == 404
        data = r.json()
        assert data["detail"] == "ReadingList not found"

def test_delete_readinglist_route_success():
    with patch("app.routers.readinglist_router.service.delete_list", return_value=True):
        r = client.delete("/readinglist/1?user_id=1")
        
        assert r.status_code == 200
        data = r.json()
        assert data["message"] == "ReadingList deleted successfully"