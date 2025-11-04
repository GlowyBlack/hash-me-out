from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_route_no_result():
    r = client.get("/search/Percy Jackson")
    assert r.status_code == 200
    assert r.json() == {"result": [], "message": "No matching books found"}
    

def test_search_route_one_result():
    r = client.get("/search/Nonexistent")
    assert r.status_code == 200
    assert r.json() == {"results":[{"isbn":"0156659751","title":"The Nonexistent Knight and The Cloven Viscount","author":"Italo Calvino","year":"1977","publisher":"Harcourt"}]}
    
# r = client.get("/search/Nonexistent")
# print(r.json())
