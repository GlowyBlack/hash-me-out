import csv
import pytest
from pydantic import ValidationError
from app.services.book_service import BookService
from app.schemas.book import BookCreate, BookRead, BookUpdate

@pytest.fixture
def percy():
    return BookCreate(
        isbn="9780307245304",
        book_title="Percy Jackson And The Lightning Thief",
        author="Rick Riordan",
    )
    
@pytest.fixture(autouse=True)
def fresh_service(tmp_path):
    """
    Fresh BookService instance for each test.
    Ensures a completely clean shard directory.
    """
    service = BookService()
    service.path = tmp_path  # directory where shards will be created

    # Ensure tmp_path starts completely empty
    for f in tmp_path.iterdir():
        f.unlink()

    return service


def create_shard_for_title(service, title):
    shard = service._determine_shard_from_title(title)
    shard_path = service.path / f"{shard}.csv"

    shard_path.parent.mkdir(parents=True, exist_ok=True)

    with open(shard_path, "w", encoding="latin-1", newline="") as f:
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

    return shard_path

def test_create_book_success(fresh_service, percy):
    service = fresh_service
    create_shard_for_title(service, percy.book_title)

    expected = BookRead(
        isbn="9780307245304",
        book_title="Percy Jackson And The Lightning Thief",
        author="Rick Riordan",
        year_of_publication=None,
        publisher=None,
        image_url_s=None,
        image_url_m=None,
        image_url_l=None,
    )

    result = service.create_book(percy)
    assert result == expected


def test_prevent_duplicate_book(fresh_service, percy):
    service = fresh_service
    create_shard_for_title(service, percy.book_title)

    service.create_book(percy)

    with pytest.raises(ValueError):
        service.create_book(percy)


def test_get_all_books_returns_list(fresh_service, percy):
    service = fresh_service
    create_shard_for_title(service, percy.book_title)

    service.create_book(percy)

    result = service.get_all_books()
    assert isinstance(result, list)
    assert any(book.isbn == percy.isbn for book in result)


def test_update_book_success(fresh_service, percy):
    service = fresh_service
    create_shard_for_title(service, percy.book_title)

    service.create_book(percy)

    update_data = BookUpdate(book_title="Updated Book", author="Updated Author")
    updated = service.update_book(percy.isbn, update_data)

    assert isinstance(updated, BookRead)
    assert updated.book_title == "Updated Book"
    assert updated.author == "Updated Author"


def test_delete_book_success(fresh_service, percy):
    service = fresh_service
    create_shard_for_title(service, percy.book_title)

    service.create_book(percy)

    assert service.delete_book(percy.isbn) is True


def test_update_book_fail_not_found(fresh_service):
    service = fresh_service
    result = service.update_book("0000000000000", BookUpdate(book_title="X"))
    assert result is None


def test_delete_book_fail(fresh_service):
    service = fresh_service
    assert service.delete_book("0000000000000") is False


def test_get_book_success(fresh_service, percy):
    service = fresh_service
    create_shard_for_title(service, percy.book_title)

    service.create_book(percy)
    result = service.get_book(percy.isbn)

    assert isinstance(result, BookRead)
    assert result.isbn == percy.isbn
    assert result.book_title == percy.book_title
    assert result.author == percy.author


def test_get_book_returns_none_when_not_found(fresh_service):
    service = fresh_service
    assert service.get_book("0000000000000") is None


@pytest.mark.parametrize("invalid_isbn", ["", "11", "111111111111111111111"])
def test_invalid_isbn_fail(invalid_isbn):
    with pytest.raises(ValidationError):
        BookCreate(
            isbn=invalid_isbn,
            book_title="Percy Jackson And The Lightning Thief",
            author="Rick Riordan",
        )
