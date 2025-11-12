import pytest
from app.services.book_service import BookService
from app.schemas.book import BookCreate, BookRead, BookUpdate

service = BookService()

def test_create_book_success():
    expected_result = BookRead(
                        isbn = "9780307245304",
                        book_title = "Percy Jackson and the Lightning Thief",
                        author = "Rick Riordan",
                        year_of_publication = None,
                        publisher = None,
                        image_url_s=None,
                        image_url_m=None,
                        image_url_l=None)
    
    
    test_data = BookCreate(
                    isbn = "9780307245304",
                    book_title = "Percy Jackson and the Lightning Thief",
                    author = "Rick Riordan")
    
    result = service.create_book(test_data)
    assert result == expected_result


def test_prevent_duplicate_book():
    duplicate_data = BookCreate(
        isbn = "9780307245304",
        book_title = "Percy Jackson and the Lightning Thief",
        author = "Rick Riordan"
    )
    with pytest.raises(ValueError, match = "Book already exists in the database."):
        service.create_book(duplicate_data)
    
def test_get_all_books_returns_list():
    result = service.get_all_books()
    assert isinstance(result, list)
    assert any(book.isbn == "9780307245304" for book in result)

def test_update_book_success():
    update_data = BookUpdate(
        isbn = "9780307245304",
        book_title = "Updated Book",
        author = "Updated Author"
    )

    updated_book = service.update_book("9780307245304", update_data)
    assert updated_book.book_title == "Updated Book"
    assert updated_book.author == "Updated Author"

def test_delete_book_success():
    result = service.delete_book("9780307245304")
    assert result is True
