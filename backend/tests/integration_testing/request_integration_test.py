from unittest.mock import patch
from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_request_route_success():
    request = {"book_title": "Percy Jackson", "author": "Rick Riordan", "isbn": "9780307245304"}
    with patch("app.routers.request_router.service.create_request", return_value={
    "book_title": "Percy Jackson",
    "author": "Rick Riordan",
    "isbn": "9780307245304",
    "user_id": 1
    }):
        r = client.post("/requests/?user_id=1", json=request)
        assert r.status_code == 200
        data = r.json()
        # print(data)
        assert data["book_title"] == "Percy Jackson"
        assert data["user_id"] == 1
    
def test_request_delete_fail():
    with patch("app.routers.request_router.service.delete_request", return_value=False):
        r = client.delete("/requests/2")
        assert r.status_code == 404
        assert r.json() == {"detail": "Request not found"}

def test_request_delete_success():
    with patch("app.routers.request_router.service.delete_request", return_value=True):
        r = client.delete("/requests/1")
        print("test")
        print(r.json())
        assert r.status_code == 200

        assert r.json() == {"message": "Request deleted successfully"}

# test_request_route_success()
# test_request_delete_success()