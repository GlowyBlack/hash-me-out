from fastapi import APIRouter, HTTPException
from app.schemas.book import BookCreate, BookUpdate
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])
service = BookService()

@router.post("/")
def create_book(book: BookCreate):
    try:
        return service.create_book(book)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/")
def get_all_books():
    """Retrieve a list of books."""
    return service.get_all_books()

@router.get("/{isbn}")
def get_book(isbn: str):
    """Retrieve a specific book by ISBN."""
    book = service.get_book(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{isbn}")
def update_book(isbn: str, book: BookUpdate):
    """Update an existing book's details."""
    try:
        updated_book = service.update_book(isbn, book)
        if not updated_book:
            raise HTTPException(status_code=404, detail="Book not found")
        return updated_book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/{isbn}", status_code=204)
def delete_book(isbn: str):
    if not service.delete_book(isbn):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}