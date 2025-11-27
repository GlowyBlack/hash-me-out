import csv
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import readinglist_router
from app.deps import get_current_user


@pytest.fixture(autouse=True)
def prepare_csv_for_testing(tmp_path):
    """
    Reset the CSV file before each test, restore after.
    """
    path = readinglist_router.service.path

    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
    except FileNotFoundError:
        original = None

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ListID", "UserID", "Name", "ISBNs", "IsPublic"],
        )
        writer.writeheader()

    yield

    if original is None:
        if os.path.exists(path):
            os.remove(path)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(original)


@pytest.fixture
def client():
    return TestClient(app)


# ----------------------------------------------
# Fixture: simulate logged-in user id=1
# ----------------------------------------------
@pytest.fixture(autouse=True)
def as_user1():
    """
    Override get_current_user for ALL tests.
    """
    def override_user():
        return {
            "id": 1,
            "username": "u1",
            "email": "u1@test.com",
            "is_admin": False,
        }

    app.dependency_overrides[get_current_user] = override_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

def test_create_readinglist_route_failure(client):
    r = client.post("/readinglist/", json={"name": " "})
    assert r.status_code == 422


def test_create_readinglist_route_success(client):
    r = client.post("/readinglist/", json={"name": "My New ReadingList"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "My New ReadingList"
    assert data["books"] == []


def test_user_cannot_create_more_than_10_readinglists(client):
    for i in range(10):
        r = client.post("/readinglist/", json={"name": f"List {i}"})
        assert r.status_code == 200

    r = client.post("/readinglist/", json={"name": "List 10"})
    assert r.status_code == 400


def test_delete_readinglist_route_failure(client):
    r = client.delete("/readinglist/999")
    assert r.status_code == 404


def test_delete_readinglist_route_success(client):
    create_result = client.post("/readinglist/", json={"name": "Test List"})
    list_id = create_result.json()["list_id"]

    delete_result = client.delete(f"/readinglist/{list_id}")
    assert delete_result.status_code == 200

    delete_again = client.delete(f"/readinglist/{list_id}")
    assert delete_again.status_code == 404


def test_rename_readinglist_success(client):
    r = client.post("/readinglist/", json={"name": "Original"})
    list_id = r.json()["list_id"]

    r = client.put(f"/readinglist/{list_id}", json={"new_name": "Renamed"})
    assert r.status_code == 200


def test_rename_readinglist_not_found(client):
    r = client.put("/readinglist/999", json={"new_name": "DoesNotExist"})
    assert r.status_code == 404


def test_rename_readinglist_duplicate_name(client):
    r1 = client.post("/readinglist/", json={"name": "List1"})
    r2 = client.post("/readinglist/", json={"name": "List2"})
    list_id = r2.json()["list_id"]

    r = client.put(f"/readinglist/{list_id}", json={"new_name": "List1"})
    assert r.status_code == 400


def test_toggle_visibility_success(client):
    create_res = client.post("/readinglist/", json={"name": "My List"})
    list_id = create_res.json()["list_id"]

    toggle_1 = client.put(f"/readinglist/{list_id}/visibility")
    assert toggle_1.status_code == 200

    toggle_2 = client.put(f"/readinglist/{list_id}/visibility")
    assert toggle_2.status_code == 200


def test_toggle_visibility_list_not_found(client):
    r = client.put("/readinglist/999/visibility")
    assert r.status_code == 404


def test_toggle_visibility_wrong_user(client):
    """
    Override user to id=2 for THIS test only.
    """
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2,
        "username": "u2",
        "email": "u2@test.com",
        "is_admin": False,
    }

    # Create list belonging to user 1
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "u1",
        "email": "u1@test.com",
        "is_admin": False,
    }
    res = client.post("/readinglist/", json={"name": "User One List"})
    list_id = res.json()["list_id"]

    # Switch to user 2
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2,
        "username": "u2",
        "email": "u2@test.com",
        "is_admin": False,
    }

    r = client.put(f"/readinglist/{list_id}/visibility")
    assert r.status_code == 404

    app.dependency_overrides.pop(get_current_user, None)


def test_add_book_success(client):
    create = client.post("/readinglist/", json={"name": "RL"})
    list_id = create.json()["list_id"]

    r = client.post(f"/readinglist/{list_id}/books/9780307245304")
    assert r.status_code == 200


def test_add_book_duplicate(client):
    create = client.post("/readinglist/", json={"name": "RL"})
    list_id = create.json()["list_id"]

    client.post(f"/readinglist/{list_id}/books/9780307245304")
    r = client.post(f"/readinglist/{list_id}/books/9780307245304")
    assert r.status_code == 400


def test_add_book_list_not_found(client):
    r = client.post("/readinglist/999/books/9780307245304")
    assert r.status_code == 404


def test_remove_book_success(client):
    create = client.post("/readinglist/", json={"name": "MyList"})
    list_id = create.json()["list_id"]

    client.post(f"/readinglist/{list_id}/books/9780307245304")

    r = client.delete(f"/readinglist/{list_id}/books/9780307245304")
    assert r.status_code == 200


def test_remove_book_not_in_list(client):
    create = client.post("/readinglist/", json={"name": "RL"})
    list_id = create.json()["list_id"]

    r = client.delete(f"/readinglist/{list_id}/books/99999999999")
    assert r.status_code == 400


def test_remove_book_list_not_found(client):
    r = client.delete("/readinglist/999/books/9780307245304")
    assert r.status_code == 404


def test_get_user_public_empty(client):
    r = client.get("/readinglist/public/1")
    assert r.status_code == 200


def test_get_user_public_single(client):
    res = client.post("/readinglist/", json={"name": "L1"})
    list_id = res.json()["list_id"]

    client.put(f"/readinglist/{list_id}/visibility")

    r = client.get("/readinglist/public/1")
    assert r.status_code == 200


def test_get_user_public_excludes_private(client):
    client.post("/readinglist/", json={"name": "PrivateList"})
    r = client.get("/readinglist/public/1")
    assert r.status_code == 200


def test_get_user_public_mixed(client):
    client.post("/readinglist/", json={"name": "PrivateL"})
    res = client.post("/readinglist/", json={"name": "PublicL"})
    list_id = res.json()["list_id"]

    client.put(f"/readinglist/{list_id}/visibility")

    r = client.get("/readinglist/public/1")
    assert r.status_code == 200


def test_get_user_public_does_not_include_other_users_lists(client):
    # Create list for user1
    res1 = client.post("/readinglist/", json={"name": "U1List"})
    id1 = res1.json()["list_id"]
    client.put(f"/readinglist/{id1}/visibility")

    # User2's list
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 2,
        "username": "u2",
        "email": "u2@test.com",
        "is_admin": False,
    }
    res2 = client.post("/readinglist/", json={"name": "U2List"})
    id2 = res2.json()["list_id"]
    client.put(f"/readinglist/{id2}/visibility")

    # Switch back to user1
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1,
        "username": "u1",
        "email": "u1@test.com",
        "is_admin": False,
    }

    r = client.get("/readinglist/public/1")
    assert r.status_code == 200


def test_get_readinglist_detail_success(client):
    res = client.post("/readinglist/", json={"name": "MyList"})
    list_id = res.json()["list_id"]

    client.post(f"/readinglist/{list_id}/books/ABC123")

    r = client.get(f"/readinglist/{list_id}", params={"user_id": 1})
    assert r.status_code == 200


def test_get_readinglist_detail_not_found(client):
    r = client.get("/readinglist/999", params={"user_id": 1})
    assert r.status_code == 404


def test_get_readinglist_detail_wrong_user(client):
    res = client.post("/readinglist/", json={"name": "Hidden"})
    list_id = res.json()["list_id"]

    r = client.get(f"/readinglist/{list_id}", params={"user_id": 2})
    assert r.status_code == 404
