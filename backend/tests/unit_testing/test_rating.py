import pytest
from app.services.rating_service import RatingService
from app.schemas.rating import RatingRead

service = RatingService()

def test_create_rating_success():
    expected = RatingRead(user_id=1, isbn="034545104X", rating=8)
    result = service.create_rating(1, "034545104X", 8)
    assert result == expected

def test_update_rating_overwrites_value():
    service.create_rating(1, "034545104X", 6)
    service.create_rating(1, "034545104X", 8)  # upsert/update
    r = service.get_user_rating(1, "034545104X")
    assert r and r.rating == 8

def test_get_all_and_delete():
    service.create_rating(2, "1111111111", 6)
    rows = service.get_ratings_by_isbn("1111111111")
    assert len(rows) == 1
    assert rows[0].user_id == 2
    ok = service.delete_rating(2, "1111111111")
    assert ok is True
