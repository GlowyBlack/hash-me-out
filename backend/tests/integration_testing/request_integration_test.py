import csv
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import request_router


@pytest.fixture(autouse=True)
def clean_request_csvs(tmp_path):

    request_router.service.path = tmp_path / "Requests.csv"
    request_router.service.totalpath = tmp_path / "Total_Requested.csv"

    with open(request_router.service.path, "w", newline = "", encoding = "utf-8") as f:
        writer = csv.DictWriter(f, fieldnames = request_router.service.fields)
        writer.writeheader()

    with open(request_router.service.totalpath, "w", newline = "", encoding = "utf-8") as f:
        writer = csv.DictWriter(f, fieldnames = request_router.service.total_fields)
        writer.writeheader()

    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_request_route_success(client):
    request = {
        "book_title": "Percy Jackson",
        "author": "Rick Riordan",
        "isbn": "9780307245304"
    }

    res = client.post("/requests/?user_id=1", json=request)
    assert res.status_code == 200
    
    data = res.json()
    assert data["book_title"] == "Percy Jackson"
    assert data["author"] == "Rick Riordan"
    assert data["isbn"] == "9780307245304"
    assert data["user_id"] == 1


def test_request_delete_success(client):
    req = {
        "book_title": "Test Book",
        "author": "Someone",
        "isbn": "1111111111"
    }

    created = client.post("/requests/?user_id=1", json=req)
    assert created.status_code == 200

    request_id = created.json()["request_id"]

    r = client.delete(f"/requests/{request_id}")
    assert r.status_code == 200
    assert r.json() == {"message": "Request deleted successfully"}
