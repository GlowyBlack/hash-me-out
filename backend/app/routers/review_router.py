from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.review_service import ReviewService
from app.deps import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])
service = ReviewService()

# TODO: Make all of the methods work only for their respective role


@router.post(
    "/",
    summary="Create a review for a book",
    description="Creates a review for the given ISBN by the current user.",
    response_model=ReviewRead,
    response_description="The newly created review.",
)
def create_review(review: ReviewCreate, isbn: str,
                   curr = Depends(get_current_user)):
    user_id = curr["id"]
    try:
        return service.create_review(user_id = user_id, data = review, isbn = isbn)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{isbn}",
    summary="List all reviews for a book",
    description="Returns all reviews for the given ISBN.",
    response_model=list[ReviewRead],
    response_description="A list of reviews for the book.",
)
def get_all_reviews(isbn: str,):
    return service.get_all_reviews(isbn = isbn)


@router.put(
    "/{review_id}",
    summary="Edit a review",
    description="Updates an existing review by its ID.",
    response_model=ReviewRead,
    response_description="The updated review.",
)
def edit_review(review_id: int, review: ReviewUpdate,
                   curr = Depends(get_current_user)):
    
    try:
        return service.edit_review(review_id = review_id, data = review)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = str(e))


@router.delete(
    "/{review_id}",
    summary="Delete a review",
    description="Deletes a review by its ID.",
    response_description="Confirmation message on success.",
)
def delete_review(review_id: int,
                   curr = Depends(get_current_user)):
    if not service.delete_review(review_id = review_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Review not found")
    return {"message": "Review deleted successfully"}
