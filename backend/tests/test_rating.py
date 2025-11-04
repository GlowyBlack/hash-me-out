import csv
import pytest
from pathlib import Path
from app.services.rating_service import RatingService
from app.schemas.rating import RatingCreate

# fake repository 
class FakeCSVRepository:
    def read_all(self, path: Path, fieldnames=None):
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f, delimiter=";"))

    def write_all(self, path: Path, fieldnames, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            w.writeheader()
            w.writerows(rows)

    def append(self, path: Path, row_dict, fieldnames):
        file_exists = path.exists()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            if not file_exists:
                w.writeheader()
            w.writerow(row_dict)

@pytest.fixture()
def svc(tmp_path):
    s = RatingService()
    s.repo = FakeCSVRepository()
    s.ratings_path = tmp_path / "BX-Book-Ratings.csv"
    s.repo.write_all(s.ratings_path, s.fields, [])
    return s

def test_create_rating(svc):
    out = svc.create_rating(123, RatingCreate(isbn="034545104X", rating=8))
    assert out.user_id == 123
    assert out.isbn == "034545104X"
    assert out.rating == 8
    got = svc.get_user_rating(123, "034545104X")
    assert got is not None and got.rating == 8

def test_create_rating_duplicate_raises(svc):
    svc.create_rating(1, RatingCreate(isbn="A", rating=5))
    with pytest.raises(ValueError):
        svc.create_rating(1, RatingCreate(isbn="A", rating=7))

def test_get_user_rating_none_when_absent(svc):
    assert svc.get_user_rating(999, "NOPE") is None

def test_get_ratings_by_isbn(svc):
    svc.create_rating(1, RatingCreate(isbn="Z", rating=6))
    svc.create_rating(2, RatingCreate(isbn="Z", rating=9))
    svc.create_rating(3, RatingCreate(isbn="Y", rating=4))
    lst = svc.get_ratings_by_isbn("Z")
    assert len(lst) == 2
    assert sorted(r.user_id for r in lst) == [1, 2]
    assert sorted(r.rating for r in lst) == [6, 9]

def test_get_avg_rating_empty_is_zero(svc):
    avg = svc.get_avg_rating("NONE")
    assert avg.isbn == "NONE"
    assert avg.avg_rating == 0.0
    assert avg.count == 0

def test_get_avg_rating_value(svc):
    svc.create_rating(1, RatingCreate(isbn="X", rating=6))
    svc.create_rating(2, RatingCreate(isbn="X", rating=8))
    avg = svc.get_avg_rating("X")
    assert avg.avg_rating == 7.0
    assert avg.count == 2

def test_delete_rating(svc):
    svc.create_rating(42, RatingCreate(isbn="ABC", rating=5))
    ok = svc.delete_rating(42, "ABC")
    assert ok is True
    assert svc.get_user_rating(42, "ABC") is None

def test_delete_rating_not_found(svc):
    ok = svc.delete_rating(7, "NOPE")
    assert ok is False
