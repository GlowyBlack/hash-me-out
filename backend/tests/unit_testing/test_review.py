import csv
import pytest
from app.services.review_service import ReviewService
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate


@pytest.fixture
def service(tmp_path):
    """
    Provide a fresh ReviewService with an isolated Reviews.csv
    for every test.
    """
    svc = ReviewService()
    svc.path = str(tmp_path / "Reviews.csv")

    with open(svc.path, "w", newline = "", encoding = "utf-8") as f:
        writer = csv.DictWriter(f, fieldnames = svc.fields)
        writer.writeheader()

    return svc


def test_create_review_success(service):
    content = ReviewCreate(
        comment = "This is great!"
    )
    result = service.create_review(user_id = 1, data = content, isbn = "034545104X")

    assert isinstance(result, ReviewRead)
    assert result.user_id == 1
    assert result.isbn == "034545104X"
    assert result.comment == "This is great!"
    assert result.review_id == 1  


def test_get_all_reviews(service):
    content = ReviewCreate(comment = "Garbage book.")
    created = service.create_review(user_id = 2, data = content, isbn = "1111111111")

    rows = service.get_all_reviews("1111111111")

    assert len(rows) == 1
    assert rows[0] == created


def test_delete_review(service):
    content = ReviewCreate(comment="Delete me")
    created = service.create_review(user_id = 2, data = content, isbn="1111111111")

    ok = service.delete_review(created.review_id)
    assert ok is True

    remaining = service.get_all_reviews("1111111111")
    assert all(r.review_id != created.review_id for r in remaining)


def test_create_review_twice_same_user_and_book_raises(service):
    content = ReviewCreate(comment = "This is great!")
    service.create_review(user_id = 1, data = content, isbn = "034545104X")

    with pytest.raises(ValueError):
        service.create_review(user_id = 1, data = content, isbn = "034545104X")