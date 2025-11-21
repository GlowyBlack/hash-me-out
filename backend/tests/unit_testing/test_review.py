import csv
import pytest
from app.services.review_service import ReviewService
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate

service = ReviewService()

@pytest.fixture(autouse=True) 
def clean_reviews_csv(tmp_path):
    
    service.path = str(tmp_path / "Reviews.csv")

    with open(service.path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=service.fields)
        writer.writeheader()

    yield
    
    
def test_create_review_success():
    content = ReviewCreate(
        isbn="034545104X",       
        comment="This is great!"   
    )

    result = service.create_review(1, content)

    assert isinstance(result, ReviewRead)
    assert result.user_id == 1
    assert result.isbn == "034545104X"
    assert result.comment == "This is great!"
    assert result.review_id >= 1
    
    
def test_get_all_reviews():
    isbn = "1111111111"
    content = ReviewCreate(
        isbn=isbn,
        comment="Garbage book. Didn't like."
    )

    created = service.create_review(2, content)

    rows = service.get_all_reviews(isbn)

    assert len(rows) == 1
    assert rows[0].review_id == created.review_id
    assert rows[0].user_id == 2
    assert rows[0].isbn == isbn
    assert rows[0].comment == "Garbage book. Didn't like."


def test_delete_review():
    isbn = "1111111111"
    content = ReviewCreate(
        isbn=isbn,
        comment="To be deleted"
    )

    created = service.create_review(2, content)

    ok = service.delete_review(created.review_id)
    assert ok is True

    rows_after = service.get_all_reviews(isbn)

    assert all(rev.review_id != created.review_id for rev in rows_after)


def test_create_review_twice_same_user_and_book_raises():
    content = ReviewCreate(
        isbn="034545104X",
        comment="Amazing book!"
    )

    service.create_review(1, content)

    with pytest.raises(ValueError):
        service.create_review(1, content)
