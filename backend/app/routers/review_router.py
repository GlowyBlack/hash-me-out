from fastapi import APIRouter, HTTPException, status
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])
service = ReviewService()


@router.post("/")
def create_review(review: ReviewCreate, user_id: int):
    try:
        return service.create_review(user_id = user_id, data = review)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{isbn}")
def get_all_reviews(isbn: str):
    return service.get_all_reviews(isbn = isbn)


@router.put("/{review_id}")
def edit_review(review_id: int, review: ReviewUpdate):
    try:
        return service.edit_review(review_id = review_id, data = review)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = str(e))


@router.delete("/{review_id}")
def delete_review(review_id: int):
    if not service.delete_review(review_id = review_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Review not found")
    return {"message": "Review deleted successfully"}
