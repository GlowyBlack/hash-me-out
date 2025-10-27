from fastapi import APIRouter, HTTPException
from app.schemas.review import ReviewCreate
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])
service = ReviewService()

@router.post("/")
def create_request(review: ReviewCreate):
    """Submit a new book request."""
    try:
        return service.create_review(review)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{isbn}")
def get_all_requests(isbn: str):
    """List all book requests."""
    return service.get_all_reviews(isbn)
