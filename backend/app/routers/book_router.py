from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.book import BookCreate, BookUpdate
from app.services.book_service import BookService
from app.deps import get_current_user

router = APIRouter(prefix = "/books", tags = ["Books"])
service = BookService()

@router.post(
    "/",
    summary="Create a new book (Admin only)",
    description="Creates a new book entry in the system. Requires admin privileges.",
    response_description="The newly created book entry."
)
def create_book(book: BookCreate,
                curr = Depends(get_current_user)):
    """Create a new book entry in the system."""
    if not curr.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    try:
        return service.create_book(book)
    except ValueError as e:
        raise HTTPException(status_code = 400, detail = str(e))
    
@router.get(
    "/",
    summary="Retrieve all books",
    description="Returns a list of all books available in the system."
)
def get_all_books():
    """Retrieve a list of books."""
    return service.get_all_books()

@router.get(
    "/{isbn}",
    summary="Retrieve a book by ISBN",
    description="Returns details about a specific book using its ISBN."
)
def get_book(isbn: str):
    """Retrieve a specific book by ISBN."""
    book = service.get_book(isbn)
    if not book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    return book

@router.put(
    "/{isbn}",
    summary="Update a book's details (Admin only)",
    description="Updates an existing book's information. Requires admin privileges.",
    response_description="The updated book entry."
)
def update_book(isbn: str, book: BookUpdate,
                curr = Depends(get_current_user)):
    """Update an existing book's details."""
    if not curr.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    try:
        updated_book = service.update_book(isbn, book)
        if not updated_book:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
        return updated_book
    except ValueError as e:
        raise HTTPException(status_code = 400, detail = str(e))
    
@router.delete(
    "/{isbn}",
    summary="Delete a book (Admin only)",
    description="Deletes a book from the system using its ISBN. Requires admin privileges.",
    response_description="A success message upon deletion."
)
def delete_book(isbn: str, 
                curr = Depends(get_current_user)):
    """Delete a book from the system by its ISBN."""
    if not curr.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    if not service.delete_book(isbn):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    return {"message": "Book deleted successfully"}