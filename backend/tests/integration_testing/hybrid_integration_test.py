import pytest
from fastapi.testclient import TestClient
import pandas as pd

from app.main import app
from app.recommender.vectorizer_loader import GlobalVectorizer

client = TestClient(app)

# -----------------------------
# FIXTURE: RESET VECTORIZER
# -----------------------------
@pytest.fixture(autouse=True)
def reset_vectorizer():
    GlobalVectorizer.reset()

    df = pd.DataFrame([
        {"ISBN": "A", "combined_text": "alpha beta gamma lawyer crime"},
        {"ISBN": "B", "combined_text": "alpha beta delta mystery thriller"},
        {"ISBN": "C", "combined_text": "crime thriller courtroom lawyer"},
        {"ISBN": "D", "combined_text": "romance drama love"},
        {"ISBN": "E", "combined_text": "crime mystery investigation detective"},
    ])
    GlobalVectorizer.load_from_df(df)
    yield


# -----------------------------
# MOCK USER & AUTH
# -----------------------------
@pytest.fixture
def patch_current_user():
    from app.deps import get_current_user

    def override():
        return {"id": 999}

    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)

def mock_interactions(user_id):
    return [
        {"isbn": "A", "type": "reading_list"},
        {"isbn": "C", "type": "rating", "rating_value": 10},
    ]


@pytest.fixture
def patch_user_interactions(monkeypatch):
    from app.services.user_interaction_service import UserInteractionService
    monkeypatch.setattr(
        UserInteractionService, 
        "get_user_interactions",
        lambda self, uid: mock_interactions(uid)
    )


@pytest.fixture
def patch_book_repo(monkeypatch):
    from app.repositories.book_repository import BookRepository

    def fake_get(self, isbn):   # <-- add self here
        mapping = {
            "A": {"ISBN": "A", "Book-Title": "Book A", "Book-Author": "Author A"},
            "B": {"ISBN": "B", "Book-Title": "Book B", "Book-Author": "Author B"},
            "C": {"ISBN": "C", "Book-Title": "Book C", "Book-Author": "Author C"},
            "D": {"ISBN": "D", "Book-Title": "Book D", "Book-Author": "Author D"},
            "E": {"ISBN": "E", "Book-Title": "Book E", "Book-Author": "Author E"},
        }
        return mapping.get(isbn)

    monkeypatch.setattr(BookRepository, "get_book_by_isbn", fake_get)

# -----------------------------
# TEST 1: BASIC SUCCESS
# -----------------------------
def test_hybrid_success(
    patch_current_user,
    patch_user_interactions,
    patch_book_repo
):
    """Hybrid should return valid recommendations."""
    response = client.get("/hybrid/A?top_k=3")
    assert response.status_code == 200
    
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    # ensure hybrid_score exists
    assert "hybrid_score" in data[0]

    # shouldn't recommend books the user has interacted with
    for item in data:
        assert item["isbn"] not in {"A", "C"}

def test_hybrid_no_duplicates(
    patch_current_user,
    patch_user_interactions,
    patch_book_repo
):
    resp = client.get("/hybrid/A?top_k=10")
    assert resp.status_code == 200

    items = resp.json()
    seen = set()

    for item in items:
        assert item["isbn"] not in seen, "Duplicate ISBN returned!"
        seen.add(item["isbn"])
