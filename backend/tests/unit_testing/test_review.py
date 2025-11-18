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


def test_edit_review_updates_comment():
    isbn = "2222222222"
    original = ReviewCreate(
        isbn=isbn,
        comment="Old comment here"
    )

    created = service.create_review(3, original)

    updated = service.edit_review(
        review_id=created.review_id,
        data=ReviewUpdate(comment="Updated comment!")
    )

    assert updated.review_id == created.review_id
    assert updated.comment == "Updated comment!"

    rows = service.get_all_reviews(isbn)
    found = [rev for rev in rows if rev.review_id == created.review_id]
    assert len(found) == 1
    assert found[0].comment == "Updated comment!"

