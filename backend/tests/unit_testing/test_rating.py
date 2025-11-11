import pytest
from app.services.rating_service import RatingService
from app.schemas.rating import RatingCreate, RatingRead

service = RatingService()

def test_create_rating_success():
    expected = RatingRead(user_id=1, isbn="034545104X", rating=8)
    result = service.create_rating(1, RatingCreate(isbn="034545104X", rating=8))
    assert result == expected

def test_prevent_duplicate_rating():
    with pytest.raises(ValueError):
        service.create_rating(1, RatingCreate(isbn="034545104X", rating=9))

def test_get_all_and_delete():
    service.create_rating(2, RatingCreate(isbn="1111111111", rating=6))
    rows = service.get_ratings_by_isbn("1111111111")
    assert len(rows) == 1
    assert rows[0].user_id == 2
    ok = service.delete_rating(2, "1111111111")
    assert ok is True
