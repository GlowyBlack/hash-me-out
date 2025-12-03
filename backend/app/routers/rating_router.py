from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.rating import RatingCreate, RatingRead, AvgRatingRead
from app.services.rating_service import RatingService
from app.deps import get_current_user

router = APIRouter(prefix = "/ratings", tags = ["Ratings"])
service = RatingService()


@router.post("/books/{isbn}",
    summary = "Add or update a rating for a book",
    description=(
        "Creates or updates a rating for the given book by the current user. "
        "If the user has already rated this book, the rating is updated."
    ),
    response_model=RatingRead,
    response_description = "The created or updated rating.",
)
def add_rating(isbn: str, payload: RatingCreate, curr = Depends(get_current_user)):
    user_id = curr["id"]
    return service.create_rating(user_id = user_id, isbn = isbn, rating_value = payload.rating)

@router.get(
    "/",
    summary = "List all ratings",
    description = "Returns all ratings stored in the system.",
    response_model=list[RatingRead],
    response_description = "A list of all ratings.",
)
def get_all_ratings():
    return service.get_all_ratings()


@router.get(
    "/books/{isbn}",
    summary = "List ratings for a specific book",
    description = "Returns all ratings for the given ISBN.",
    response_model=list[RatingRead],
    response_description = "A list of ratings for the given ISBN.",
)
def get_ratings_by_isbn(isbn: str):
    return service.get_ratings_by_isbn(isbn)


@router.get(
    "/books/{isbn}/average",
    summary = "Get average rating for a book",
    description = "Returns the average rating and count of ratings for the given ISBN.",
    response_model = AvgRatingRead,
    response_description = "Average rating information for the given ISBN.",
)
def get_avg_rating(isbn: str):
    return service.get_avg_rating(isbn)


@router.get(
    "/users/{user_id}/books/{isbn}",
    summary = "Get a user's rating for a book",
    description = "Returns a specific user's rating for a given ISBN, if it exists.",
    response_model = RatingRead | None,
    response_description = "The rating if found, otherwise null.",
)
def get_user_rating(user_id: int, isbn: str):
    return service.get_user_rating(user_id, isbn)


@router.delete(
    "/",
    summary = "Delete current user's rating for a book",
    status_code = status.HTTP_204_NO_CONTENT,
    description = "Deletes the current user's rating for the given ISBN if it exists.",
    response_description = "No content on success.",
)
def delete_rating(isbn: str, curr = Depends(get_current_user)):
    user_id = curr["id"]
    ok = service.delete_rating(user_id = user_id, isbn = isbn)
    if not ok:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Rating not found")
