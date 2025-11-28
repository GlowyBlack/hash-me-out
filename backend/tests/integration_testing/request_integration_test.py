import csv
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import request_router
from app.deps import get_current_user


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
        "isbn": "9780307245304",
    }

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "x",
        "email": "x@x.com",
        "is_admin": False,
    }

    try:
        res = client.post("/requests/", json=request)
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert res.status_code == 200
    data = res.json()
    assert data["book_title"] == "Percy Jackson"
    assert data["author"] == "Rick Riordan"
    assert data["isbn"] == "9780307245304"
    assert data["user_id"] == 1

def test_request_delete_success(client):
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "bob",
        "email": "bob@example.com",
        "is_admin": False,
    }

    created = client.post(
        "/requests/",
        json={"book_title": "Test Book", "author": "Someone", "isbn": "1111111111"},
    )
    request_id = created.json()["request_id"]

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 99,
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
    }

    try:
        r = client.delete(f"/requests/{request_id}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert r.status_code == 200
    assert r.json() == {"message": "Request deleted successfully"}

def test_delete_nonexistent_request(client):

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
    }

    try:
        r = client.delete("/requests/999")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert r.status_code == 404
    assert r.json() == {"detail": "Request not found"}

def test_get_all_requests(client):


    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2, 
        "username": "user1", 
        "email": "user1@test.com", 
        "is_admin": False
    }


    client.post(
        "/requests/",
        json={"book_title": "Book A", "author": "A", "isbn": "1111111111"},
    )
    client.post(
        "/requests/",
        json={"book_title": "Book B", "author": "B", "isbn": "2222222222"},
    )

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
    }

    try:
        r = client.get("/requests/")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["request_id"] == 1
    assert data[1]["request_id"] == 2
    
def test_user_cannot_request_same_book_twice(client):
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2, 
        "username": "user2", 
        "email": "user2@example.com", 
        "is_admin": False
    }

    r1 = client.post(
        "/requests/",
        json={"book_title": "Repeat Book", "author": "X", "isbn": "1231231231"},
    )
    assert r1.status_code == 200

    r2 = client.post(
        "/requests/",
        json={"book_title": "Repeat Book", "author": "X", "isbn": "1231231231"},
    )

    app.dependency_overrides.pop(get_current_user, None)

    assert r2.status_code == 400
    assert r2.json()["detail"] == "This user has already requested this book."

def test_admin_deletes_only_one_of_multiple_requests(client):
    def user2():
        return {"id": 2, "username": "user2", "email": "user20@gmail.com", "is_admin": False}

    def user3():
        return {"id": 3, "username": "user3", "email": "user3@gmail.com", "is_admin": False}

    app.dependency_overrides[get_current_user] = user2
    client.post(
        "/requests/",
        json={"book_title": "Shared Book", "author": "Someone", "isbn": "9999999999"},
    )

    app.dependency_overrides[get_current_user] = user3
    client.post(
        "/requests/",
        json={"book_title": "Shared Book", "author": "Someone", "isbn": "9999999999"},
    )

    def admin():
        return {"id": 1, "username": "admin", "email": "admin@example.com", "is_admin": True}

    app.dependency_overrides[get_current_user] = admin

    resp = client.delete("/requests/1")

    app.dependency_overrides.pop(get_current_user, None)

    assert resp.status_code == 200
    assert resp.json() == {"message": "Request deleted successfully"}

    app.dependency_overrides[get_current_user] = admin
    r_all = client.get("/requests/")
    app.dependency_overrides.pop(get_current_user, None)

    data = r_all.json()
    assert len(data) == 1
    assert data[0]["user_id"] == 3
    assert data[0]["request_id"] == 1    

def test_request_stats_sorted_by_total_requests(client):
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2,
        "username": "user2",
        "email": "user2@example.com",
        "is_admin": False,
    }

    client.post(
        "/requests/",
        json={"book_title": "Book A", "author": "A", "isbn": "1111111111"},
    )
    client.post(
        "/requests/",
        json={"book_title": "Book B", "author": "B", "isbn": "2222222222"},
    )

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 3,
        "username": "user3",
        "email": "user3@example.com",
        "is_admin": False,
    }

    client.post(
        "/requests/",
        json={"book_title": "Book A again", "author": "A", "isbn": "1111111111"},
    )

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
    }

    try:
        r_desc = client.get("/requests/stats?order=desc")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert r_desc.status_code == 200
    data_desc = r_desc.json()

    assert [row["ISBN"] for row in data_desc] == ["1111111111", "2222222222"]
    assert data_desc[0]["Total Requested"] == 2
    assert data_desc[1]["Total Requested"] == 1

    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
    }

    try:
        r_asc = client.get("/requests/stats?order=asc")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert r_asc.status_code == 200
    data_asc = r_asc.json()

    assert [row["ISBN"] for row in data_asc] == ["2222222222", "1111111111"]
    assert data_asc[0]["Total Requested"] == 1
    assert data_asc[1]["Total Requested"] == 2
