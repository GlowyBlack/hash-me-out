import csv
import pytest
from pydantic import ValidationError
from app.services.book_service import BookService
from app.schemas.book import BookCreate, BookRead, BookUpdate

@pytest.fixture
def service(tmp_path):
    """Provide a fresh BookService with an empty temp CSV."""
    svc = BookService()
    svc.path = str(tmp_path / "Books.csv")

    # Initialize CSV with header row
    with open(svc.path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=svc.fields)
        writer.writeheader()

    return svc

@pytest.fixture
def book_data():
    """Reusable test data for Percy Jackson."""
    return BookCreate(
        isbn="9780307245304",
        book_title="Percy Jackson and the Lightning Thief",
        author="Rick Riordan",
    )

def test_create_book_success(service, book_data):
    expected = BookRead(
        isbn="9780307245304",
        book_title="Percy Jackson and the Lightning Thief",
        author="Rick Riordan",
        year_of_publication=None,
        publisher=None,
        image_url_s=None,
        image_url_m=None,
        image_url_l=None,
    )

    result = service.create_book(book_data)

    assert result == expected

def test_prevent_duplicate_book(service, book_data):
    # First creation succeeds
    service.create_book(book_data)

    # Second must fail
    with pytest.raises(ValueError, match="Book already exists in the database."):
        service.create_book(book_data)


def test_get_all_books_returns_list(service, book_data):
    # create one book first
    service.create_book(book_data)

    result = service.get_all_books()
    assert isinstance(result, list)
    assert any(book.isbn == "9780307245304" for book in result)

def test_update_book_success(service, book_data):
    service.create_book(book_data)

    update_data = BookUpdate(
        isbn="9780307245304",
        book_title="Updated Book",
        author="Updated Author",
    )

    updated = service.update_book("9780307245304", update_data)

    assert updated.book_title == "Updated Book"
    assert updated.author == "Updated Author"

def test_delete_book_success(service, book_data):
    service.create_book(book_data)

    result = service.delete_book("9780307245304")
    assert result is True


def test_update_book_fail_not_found(service):
    update_data = BookUpdate(
        isbn="0000000000000",
        book_title="Should Not Update"
    )
    result = service.update_book("0000000000000", update_data)
    assert result is None

def test_delete_book_fail(service):
    result = service.delete_book("0000000000000")
    assert result is False


def test_get_book_success(service, book_data):
    # book must exist to be found
    created = service.create_book(book_data)

    result = service.get_book("9780307245304")
    assert result is not None
    assert result.isbn == created.isbn
    assert result.book_title == created.book_title
    assert result.author == created.author

def test_get_book_returns_none_when_not_found(service):
    result = service.get_book("0000000000000")
    assert result is None


def test_empty_isbn_fail(service):
    with pytest.raises(ValidationError) as exc_info:
        invalid = BookCreate(
            isbn="",
            book_title="Percy Jackson",
            author="Rick Riordan"
        )
        service.create_book(invalid)
    assert "ISBN must contain exactly 10 or 13 digits" in str(exc_info.value)

def test_long_isbn_fail(service):
    with pytest.raises(ValidationError) as exc_info:
        invalid = BookCreate(
            isbn="1" * 40,
            book_title="Percy Jackson",
            author="Rick Riordan"
        )
        service.create_book(invalid)

    assert "ISBN must contain exactly 10 or 13 digits" in str(exc_info.value)