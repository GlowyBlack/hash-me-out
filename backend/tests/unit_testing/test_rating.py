import csv
import pytest
from app.services.rating_service import RatingService
from app.schemas.rating import RatingRead


@pytest.fixture
def service(tmp_path):
    """Return a fresh RatingService with isolated Ratings.csv."""
    svc = RatingService()
    svc.ratings_path = str(tmp_path / "Ratings.csv")

    with open(svc.ratings_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=svc.fields)
        writer.writeheader()

    return svc


def test_create_rating_success(service):
    expected = RatingRead(user_id=1, isbn="034545104X", rating=8)
    result = service.create_rating(1, "034545104X", 8)
    assert result == expected


def test_update_rating_overwrites_value(service):
    service.create_rating(1, "034545104X", 6)
    service.create_rating(1, "034545104X", 8)
    r = service.get_user_rating(1, "034545104X")
    assert r.rating == 8


def test_get_all_and_delete(service):
    service.create_rating(2, "1111111111", 6)

    rows = service.get_ratings_by_isbn("1111111111")
    assert len(rows) == 1
    assert rows[0].user_id == 2

    ok = service.delete_rating(2, "1111111111")
    assert ok is True


def test_get_user_rating_returns_none_when_missing(service):
    result = service.get_user_rating(99, "UNKNOWN_ISBN")
    assert result is None


def test_delete_rating_returns_false_when_missing(service):
    ok = service.delete_rating(123, "NOPE")
    assert ok is False


def test_get_ratings_by_isbn_empty_for_unknown(service):
    rows = service.get_ratings_by_isbn("UNKNOWN_ISBN")
    assert rows == []


def test_get_all_ratings_initially_empty(service):
    all_ratings = service.get_all_ratings()
    assert all_ratings == []
