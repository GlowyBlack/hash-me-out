from fastapi import APIRouter, HTTPException
from app.schemas.rating import RatingCreate, RatingRead, AvgRatingRead
from app.services.rating_service import RatingService

router = APIRouter(prefix="/ratings", tags=["Ratings"])
service = RatingService()


@router.post("/", response_model=RatingRead)
def add_rating(payload: RatingCreate, user_id: int):
    # keeps your method name; behavior is upsert
    return service.add_rating(user_id, payload)


@router.get("/", response_model=list[RatingRead])
def get_all_ratings():
    return service.get_all_ratings()


@router.get("/books/{isbn}", response_model=list[RatingRead])
def get_ratings_by_isbn(isbn: str):
    return service.get_ratings_by_isbn(isbn)


@router.get("/books/{isbn}/average", response_model=AvgRatingRead)
def get_avg_rating(isbn: str):
    return service.get_avg_rating(isbn)


@router.get("/users/{user_id}/books/{isbn}", response_model=RatingRead | None)
def get_user_rating(user_id: int, isbn: str):
    return service.get_user_rating(user_id, isbn)


@router.delete("/", status_code=204)
def delete_rating(user_id: int, isbn: str):
    ok = service.delete_rating(user_id, isbn)
    if not ok:
        raise HTTPException(status_code=404, detail="Rating not found")
