from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services.book_service import BookService
from app.logger import logger
from app.deps import get_current_user

router = APIRouter(prefix = "/books", tags = ["Books"])
service = BookService()

@router.get("/search", response_model = list[BookRead])
def search_books(
    query: str,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
):
    return service.search_books(
        query = query,
        author = author,
        genre = genre,
        year_min = year_min,
        year_max = year_max,
    )

@router.get("/live-search", response_model = list[BookRead])
def live_search_books(
    query: str,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    limit: int = 10,
):
    start = datetime.now()

    logger.info(f"API CALL      | /live-search/{query} ")
    result = service.live_search(
        query = query,
        author = author,
        genre = genre,
        year_min = year_min,
        year_max = year_max,
        limit = limit,
    )
    elapsed = (datetime.now() - start).total_seconds() * 1000

    logger.info(f"API DONE      | /live-search/{query} | length of returned book = {len(result)} | took = {elapsed:.2}ms")

    return result

@router.post(
    "/",
    summary = "Create a new book (Admin only)",
    description = "Creates a new book entry in the system. Requires admin privileges.",
    response_description = "The newly created book entry."
)
def create_book(book: BookCreate,
                curr = Depends(get_current_user)):
    """Create a new book entry in the system."""
    if not curr.get("is_admin"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Admin privileges required")
    try:
        return service.create_book(book)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))

@router.get(
    "/",
    summary = "Retrieve all books",
    description = "Returns a list of all books available in the system."
)
def get_all_books():
    """Retrieve a list of books."""
    return service.get_all_books()

@router.get(
    "/{isbn}",
    summary = "Retrieve a book by ISBN",
    description = "Returns details about a specific book using its ISBN."
)
def get_book(isbn: str):
    """Retrieve a specific book by ISBN."""
    book = service.get_book(isbn)
    if not book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    return book

@router.put(
    "/{isbn}",
    summary = "Update a book's details (Admin only)",
    description = "Updates an existing book's information. Requires admin privileges.",
    response_description = "The updated book entry."
)
def update_book(isbn: str, book: BookUpdate,
                curr = Depends(get_current_user)):
    """Update an existing book's details."""
    if not curr.get("is_admin"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Admin privileges required")
    try:
        updated_book = service.update_book(isbn, book)
        if not updated_book:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
        return updated_book
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))
    
@router.delete(
    "/{isbn}",
    summary = "Delete a book (Admin only)",
    description = "Deletes a book from the system using its ISBN. Requires admin privileges.",
    response_description = "A success message upon deletion."
)
def delete_book(isbn: str, 
                curr = Depends(get_current_user)):
    """Delete a book from the system by its ISBN."""
    if not curr.get("is_admin"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Admin privileges required")
    if not service.delete_book(isbn):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    return {"message": "Book deleted successfully"}