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

def test_create_review_twice_same_user_and_book_raises():
    content = ReviewCreate(
        isbn="034545104X",
        comment="Amazing book!"
    )

    service.create_review(1, content)

    with pytest.raises(ValueError):
        service.create_review(1, content)
