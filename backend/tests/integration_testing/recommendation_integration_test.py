# tests/integration_testing/recommendation_integration_test.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.deps import get_current_user
from app.recommender.vectorizer_loader import GlobalVectorizer



app.router.on_startup = []


@pytest.fixture
def user_override():
    def override():
        return {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_admin": False,
        }
    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_vectorizer(tmp_path):

    # Create a tiny enriched CSV
    enriched = tmp_path / "Enriched_Books.csv"
    enriched.write_text(
        "ISBN,Book-Title,Book-Author,Genre\n"
        "111,A Book,Author A,Fiction\n"
        "222,B Book,Author B,Fantasy\n"
        "333,C Book,Author C,Romance\n"
    )

    # Reset vectorizer before loading
    GlobalVectorizer.reset()
    GlobalVectorizer.load(str(enriched))

    yield
    GlobalVectorizer.reset()

@pytest.fixture
def patch_book_repo(monkeypatch):
    from app.repositories.book_repository import BookRepository

    def fake_get(self, isbn):
        mapping = {
            "111": {"ISBN": "111", "Book-Title": "Book 111", "Book-Author": "Author 111"},
            "222": {"ISBN": "222", "Book-Title": "Book 222", "Book-Author": "Author 222"},
            "333": {"ISBN": "333", "Book-Title": "Book 333", "Book-Author": "Author 333"},
        }
        return mapping.get(isbn)

    monkeypatch.setattr(BookRepository, "get_book_by_isbn", fake_get)


def test_recommendation_route(client, user_override, patch_book_repo):
    """
    Ensures the book-to-book recommendation engine works using
    a tiny fake vector space.
    """

    test_isbn = "111"  # must exist in our test dataset

    # Hit the endpoint
    r = client.get(f"/recommendation/{test_isbn}?top_k=2")
    assert r.status_code == 200

    data = r.json()

    assert isinstance(data, list)
    assert len(data) <= 2

    if data:
        sample = data[0]

        assert "isbn" in sample
        assert "title" in sample
        assert "author" in sample
        assert "score" in sample
        assert isinstance(sample["score"], float)

        assert sample["isbn"] != test_isbn

    if len(data) > 1:
        scores = [item["score"] for item in data]
        assert scores == sorted(scores, reverse=True)
