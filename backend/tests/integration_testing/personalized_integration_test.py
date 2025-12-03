import csv
import pytest
from fastapi.testclient import TestClient
from app.main import app
app.router.on_startup = [] 

from app.deps import get_current_user
from app.recommender.vectorizer_loader import GlobalVectorizer

# ------------------------------------------------------------
# Override logged-in user
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Load small vectorizer
# ------------------------------------------------------------
@pytest.fixture(autouse=True)
def setup_vectorizer(tmp_path):

    enriched = tmp_path / "Enriched_Books.csv"
    enriched.write_text(
        "ISBN,Book-Title,Book-Author,Genre\n"
        "111,A Book,Author A,Fiction\n"
        "222,B Book,Author B,Fantasy\n"
        "333,C Book,Author C,Romance\n"
    )

    GlobalVectorizer.reset()
    GlobalVectorizer.load(str(enriched))

    # Create fake user interaction CSVs in same folder as your app expects
    ratings = tmp_path / "Ratings.csv"
    ratings.write_text("UserID,ISBN,Book-Rating\n1,111,8\n")

    reviews = tmp_path / "Reviews.csv"
    reviews.write_text("ReviewID,UserID,ISBN,Comment,Time\n1,1,111,Good,2024\n")

    reading = tmp_path / "ReadingList.csv"
    reading.write_text("ListID,UserID,Name,ISBNs,IsPublic\n1,1,List1,\"111|222\",true\n")

    # patch CSVRepository paths by monkeypatch if needed
    # but if your repository uses fixed paths:
    import app.services.user_interaction_service as svc
    svc.CSV_PATH_RATINGS = str(ratings)
    svc.CSV_PATH_REVIEWS = str(reviews)
    svc.CSV_PATH_READINGLIST = str(reading)

    yield
    GlobalVectorizer.reset()


# ------------------------------------------------------------
# TEST personalized recommendations
# ------------------------------------------------------------
def test_personalized_route(client, user_override):
    r = client.get("/personalized?top_k=5")

    # either OK or insufficient data
    assert r.status_code in (200, 400)

    if r.status_code == 400:
        assert "Not enough user interactions" in r.json()["detail"]
        return

    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 5

    if data:
        b = data[0]
        assert "isbn" in b
        assert "title" in b
        assert "author" in b
        assert "score" in b
        assert isinstance(b["score"], float)
