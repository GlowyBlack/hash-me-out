import csv
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import rating_router


@pytest.fixture(autouse=True)
def prepare_csv_for_testing():
    path = rating_router.service.ratings_path

    try:
        with open(path, "r", encoding="utf-8") as f:
            original_contents = f.read()
    except FileNotFoundError:
        original_contents = None 
    
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["UserID", "ISBN", "Book-Rating"])
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


def test_add_rating(client):
    r = client.post(
        "/ratings/books/12345?user_id=1",
        json={"rating": 4},
    )
    assert r.status_code == 200
    assert r.json() == {"user_id": 1, "isbn": "12345", "rating": 4}

    r2 = client.get("/ratings/users/1/books/12345")
    assert r2.status_code == 200
    assert r2.json()["rating"] == 4


def test_update_rating_and_average(client):
    client.post("/ratings/books/999?user_id=2", json={"rating": 2})

    r = client.post("/ratings/books/999?user_id=2", json={"rating": 5})
    assert r.status_code == 200
    assert r.json()["rating"] == 5

    r2 = client.get("/ratings/books/999/average")
    assert r2.status_code == 200
    assert r2.json() == {"isbn": "999", "avg_rating": 5.0, "count": 1}


def test_delete_rating(client):
    client.post("/ratings/books/ABC?user_id=3", json={"rating": 3})

    r = client.delete("/ratings/?user_id=3&isbn=ABC")
    assert r.status_code == 204

    r2 = client.delete("/ratings/?user_id=3&isbn=ABC")
    assert r2.status_code == 404
    assert r2.json() == {"detail": "Rating not found"}

def test_avg_rating_multiple_users(client):
    client.post("/ratings/books/555?user_id=1", json={"rating": 4})
    client.post("/ratings/books/555?user_id=2", json={"rating": 8})
    client.post("/ratings/books/555?user_id=3", json={"rating": 6})

    r = client.get("/ratings/books/555/average")
    assert r.status_code == 200
    data = r.json()
    assert data == {"isbn": "555", "avg_rating": 6.0, "count": 3}
