import csv
import pytest
from pydantic import ValidationError

from app.services.book_service import BookService
from app.schemas.book import BookCreate, BookRead, BookUpdate

service = BookService()


@pytest.fixture(autouse=True)
def clean_books_csv(tmp_path):
    service.path = str(tmp_path / "BX_Books.csv")

    with open(service.path, "w", encoding="latin-1", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ISBN",
                "Book-Title",
                "Book-Author",
                "Year-Of-Publication",
                "Publisher",
                "Image-URL-S",
                "Image-URL-M",
                "Image-URL-L",
            ],
            delimiter=";",
        )
        writer.writeheader()

    yield


@pytest.fixture
def percy() -> BookCreate:
    return BookCreate(
        isbn = "9780307245304",
        book_title = "Percy Jackson and the Lightning Thief",
        author = "Rick Riordan",
    )


def test_create_book_success(percy):
    expected_result = BookRead(
        isbn="9780307245304",
        book_title="Percy Jackson and the Lightning Thief",
        author="Rick Riordan",
        year_of_publication=None,
        publisher=None,
        image_url_s=None,
        image_url_m=None,
        image_url_l=None,
    )

    result = service.create_book(percy)
    assert result == expected_result


def test_prevent_duplicate_book(percy):
    service.create_book(percy)

    with pytest.raises(ValueError, match="Book already exists in the database."):
        service.create_book(percy)


def test_get_all_books_returns_list(percy):
    service.create_book(percy)

    result = service.get_all_books()
    assert isinstance(result, list)
    assert any(book.isbn == percy.isbn for book in result)


def test_update_book_success(percy):
    service.create_book(percy)

    update_data = BookUpdate(
        book_title="Updated Book",
        author="Updated Author",
    )

    updated_book = service.update_book(percy.isbn, update_data)
    assert isinstance(updated_book, BookRead)
    assert updated_book.book_title == "Updated Book"
    assert updated_book.author == "Updated Author"


def test_delete_book_success(percy):
    service.create_book(percy)

    result = service.delete_book(percy.isbn)
    assert result is True


def test_update_book_fail_not_found():
    update_data = BookUpdate(
        book_title="Should Not Update",
    )
    result = service.update_book("0000000000000", update_data)
    assert result is None


def test_delete_book_fail():
    result = service.delete_book("0000000000000")
    assert result is False


def test_get_book_success(percy):
    service.create_book(percy)

    result = service.get_book(percy.isbn)
    assert isinstance(result, BookRead)
    assert result.isbn == percy.isbn
    assert result.book_title == percy.book_title
    assert result.author == percy.author


def test_get_book_returns_none_when_not_found():
    result = service.get_book("0000000000000")
    assert result is None


@pytest.mark.parametrize("invalid_isbn", ["", "11", "111111111111111111111"])
def test_invalid_isbn_fail(invalid_isbn):
    with pytest.raises(ValidationError) as exc_info:
        BookCreate(
            isbn = invalid_isbn,
            book_title = "Percy Jackson and the Lightning Thief",
            author = "Rick Riordan",
        )
    assert "ISBN must contain exactly 10 or 13 digits" in str(exc_info.value)
