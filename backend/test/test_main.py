from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search():
    r = client.get("/search/The Boy Who Cried Frog")
    assert r.status_code == 200
    assert r.json() == {"result": [], "message": "No matching books found"}