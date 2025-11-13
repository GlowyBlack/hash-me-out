from unittest.mock import patch
from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_readinglist_route_success():
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