import csv
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import readinglist_router

@pytest.fixture(autouse = True)
def prepare_csv_for_testing(tmp_path):
    path = readinglist_router.service.path

    try:
        with open(path, "r", encoding="utf-8") as f:
            original_contents = f.read()
    except FileNotFoundError:
        original_contents = None 
    with open(path, "w", newline = "", encoding = "utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames = [
                "ListID",
                "UserID",
                "Name",
                "ISBNs",
                "IsPublic"
            ]
        )
        writer.writeheader()

    yield

    if original_contents is None:
        import os
        if os.path.exists(path):
            os.remove(path)
    else:
        with open(path, "w", encoding = "utf-8") as f:
            f.write(original_contents)

@pytest.fixture
def client():
    return TestClient(app)
        
def test_create_readinglist_route_failure(client):
    request = {"name": " "}
    r = client.post(
        "/readinglist/",
        params = {"user_id":1}, 
        json = request
    )   

    assert r.status_code == 422
    assert "Readinglist Name must be at least 1 letter" in str(r.json())   
    return

def test_create_readinglist_route_success(client):
    request = {"name": "My New ReadingList"}
    r = client.post(
        "/readinglist/",
        params = {"user_id": 1},
        json = request
    )    
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "My New ReadingList"
    assert data["books"] == []

def test_user_cannot_create_more_than_10_readinglists(client):
    for i in range(10):
        r = client.post(
            "/readinglist/",
            params = {"user_id": 1},
            json = {"name": f"List {i}"}
        )
        assert r.status_code == 200

    r = client.post(
        "/readinglist/",
        params = {"user_id": 1},
        json = {"name": "List 10"}
    )

    assert r.status_code == 400
    assert r.json()["detail"] == "You can only have 10 reading lists"


def test_delete_readinglist_route_failure(client):
    r = client.delete(
        "/readinglist/999", 
        params = {"user_id": 1}
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "ReadingList not found"
    
def test_delete_readinglist_route_success(client):
    create_result = client.post(
        "/readinglist/",
        params = {"user_id": 1}, 
        json = {"name": "Test List"}
    )
    assert create_result.status_code == 200
    created = create_result.json()
    list_id = created["list_id"]  

    delete_result = client.delete(
        f"/readinglist/{list_id}",
        params = {"user_id": 1}
    )
    assert delete_result.status_code == 200
    assert delete_result.json()["message"] == "ReadingList deleted successfully"

    delete_again = client.delete(
        f"/readinglist/{list_id}",
        params = {"user_id": 1}
    )
    assert delete_again.status_code == 404
    assert delete_again.json()["detail"] == "ReadingList not found"


def test_rename_readinglist_success(client):
    r = client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "Original"}
    )
    list_id = r.json()["list_id"]

    r = client.put(
        f"/readinglist/{list_id}",
        params = {"user_id": 1},
        json = {"new_name": "Renamed"}
    )
    assert r.status_code == 200
    assert r.json()["message"] == "ReadingList renamed successfully"

def test_rename_readinglist_not_found(client):
    r = client.put(
        "/readinglist/999",
        params = {"user_id": 1},
        json = {"new_name": "DoesNotExist"}
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "ReadingList not found"

def test_rename_readinglist_duplicate_name(client):
    r1 = client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "List1"}
    )

    r2 = client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "List2"}
    )

    list_id = r2.json()["list_id"]

    r = client.put(
        f"/readinglist/{list_id}",
        params = {"user_id": 1},
        json = {"new_name": "List1"}
    )
    assert r.status_code == 400
    assert r.json()["detail"] == 'A reading list named "List1" already exists.'
    
    
def test_toggle_visibility_success(client):
    create_res = client.post(
        "/readinglist/",
        params = {"user_id": 1},
        json = {"name": "My List"}
    )

    assert create_res.status_code == 200
    list_id = create_res.json()["list_id"]

    toggle_1 = client.put(
        f"/readinglist/{list_id}/visibility",
        params = {"user_id": 1}
    )
    assert toggle_1.status_code == 200
    assert toggle_1.json()["is_public"] is True

    toggle_2 = client.put(
        f"/readinglist/{list_id}/visibility",
        params = {"user_id": 1}
    )
    assert toggle_2.status_code == 200
    assert toggle_2.json()["is_public"] is False

def test_toggle_visibility_list_not_found(client):
    r = client.put(
        "/readinglist/999/visibility",
        params = {"user_id": 1}
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "ReadingList not found"

def test_toggle_visibility_wrong_user(client):
    create_res = client.post(
        "/readinglist/",
        params = {"user_id": 1},
        json = {"name": "User One List"}
    )
    list_id = create_res.json()["list_id"]

    r = client.put(
        f"/readinglist/{list_id}/visibility",
        params = {"user_id": 2}
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "ReadingList not found"


def test_add_book_success(client):
    create = client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "RL"}
    )
    list_id = create.json()["list_id"]

    r = client.post(
        f"/readinglist/{list_id}/books/9780307245304", 
        params = {"user_id": 1}
    )
    assert r.status_code == 200
    assert r.json()["message"] == "Book added successfully"

def test_add_book_duplicate(client):
    create = client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "RL"}
    )
    list_id = create.json()["list_id"]

    client.post(
        f"/readinglist/{list_id}/books/9780307245304", 
        params = {"user_id": 1}
    )
    r = client.post(
        f"/readinglist/{list_id}/books/9780307245304", 
        params = {"user_id": 1}
    )
    assert r.status_code == 400
    assert "already in the reading list" in r.json()["detail"]
    
def test_add_book_list_not_found(client):
    r = client.post(
        "/readinglist/999/books/9780307245304", 
        params = {"user_id": 1}
    )
    assert r.status_code == 404


def test_remove_book_success(client):
    create = client.post(
        "/readinglist/",
        params = {"user_id": 1},
        json = {"name": "MyList"}
    )
    list_id = create.json()["list_id"]

    client.post(
        f"/readinglist/{list_id}/books/9780307245304", 
        params = {"user_id": 1}
    )

    r = client.delete(
        f"/readinglist/{list_id}/books/9780307245304",
        params = {"user_id": 1}
    )

    assert r.status_code == 200
    assert r.json()["message"] == "Book removed successfully"

def test_remove_book_not_in_list(client):
    create = client.post(
        "/readinglist/",
        params = {"user_id": 1},
        json = {"name": "RL"}
    )
    list_id = create.json()["list_id"]

    r = client.delete(
        f"/readinglist/{list_id}/books/99999999999",
        params = {"user_id": 1}
    )

    assert r.status_code == 400
    assert "not found" in r.json()["detail"]

def test_remove_book_list_not_found(client):
    r = client.delete(
        "/readinglist/999/books/9780307245304",
        params = {"user_id": 1}
    )

    assert r.status_code == 404
    assert r.json()["detail"] == "ReadingList not found"


def test_get_user_public_empty(client):
    r = client.get("/readinglist/public/1")

    assert r.status_code == 200
    assert r.json()["message"] == "User has no public reading lists"

def test_get_user_public_single(client):
    res = client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "L1"}
    )
    list_id = res.json()["list_id"]

    client.put(
        f"/readinglist/{list_id}/visibility", 
        params={"user_id": 1}
    )

    r = client.get("/readinglist/public/1")
    assert r.status_code == 200

    data = r.json()
    assert len(data) == 1
    assert data[0]["name"] == "L1"
    assert data[0]["is_public"] is True

def test_get_user_public_excludes_private(client):
    client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "PrivateList"}
    )

    r = client.get("/readinglist/public/1")

    assert r.status_code == 200
    assert r.json()["message"] == "User has no public reading lists"

def test_get_user_public_mixed(client):
    client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "PrivateL"}
    )

    res = client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "PublicL"}
    )
    
    list_id = res.json()["list_id"]

    client.put(
        f"/readinglist/{list_id}/visibility", 
        params = {"user_id": 1}
    )

    r = client.get("/readinglist/public/1")
    data = r.json()

    assert len(data) == 1
    assert data[0]["name"] == "PublicL"

def test_get_user_public_does_not_include_other_users_lists(client):
    r1 = client.post(
        "/readinglist/", 
        params = {"user_id": 1}, 
        json = {"name": "U1List"}
    )

    id1 = r1.json()["list_id"]

    client.put(
        f"/readinglist/{id1}/visibility", 
        params = {"user_id": 1}
    )

    r2 = client.post(
        "/readinglist/", 
        params = {"user_id": 2}, 
        json = {"name": "U2List"}
    )

    id2 = r2.json()["list_id"]

    client.put(
        f"/readinglist/{id2}/visibility", 
        params = {"user_id": 2}
    )

    r = client.get("/readinglist/public/1")
    data = r.json()
    
    assert len(data) == 1
    assert data[0]["name"] == "U1List"


def test_get_readinglist_detail_success(client):
    res = client.post(
        "/readinglist/",
        params = {"user_id": 1},
        json = {"name": "MyList"}
    )
    assert res.status_code == 200
    list_id = res.json()["list_id"]

    client.post(
        f"/readinglist/{list_id}/books/ABC123", 
        params = {"user_id": 1}
    )

    r = client.get(
        f"/readinglist/{list_id}", 
        params={"user_id": 1}
    )

    assert r.status_code == 200

    data = r.json()
    assert data["name"] == "MyList"
    assert data["list_id"] == list_id
    assert data["user_id"] == 1
    assert isinstance(data["books"], list)
    assert len(data["books"]) == 1
    assert data["books"][0]["isbn"] == "ABC123"

def test_get_readinglist_detail_not_found(client):
    r = client.get(
        "/readinglist/999", 
        params={"user_id": 1}
    )

    assert r.status_code == 404
    assert r.json()["detail"] == "ReadingList not found"

def test_get_readinglist_detail_wrong_user(client):
    res = client.post(
        "/readinglist/",
        params={"user_id": 1},
        json={"name": "Hidden"}
    )
    list_id = res.json()["list_id"]

    r = client.get(
        f"/readinglist/{list_id}", 
        params={"user_id": 2}
    )

    assert r.status_code == 404 
