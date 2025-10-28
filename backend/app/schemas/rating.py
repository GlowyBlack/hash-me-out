from pydantic import BaseModel, Field

class RatingCreate(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=13)
    rating: int = Field(..., ge=0, le=10)

class RatingRead(BaseModel):
    user_id: int = Field(..., gt=0) # field is required, id must be greater than 0
    isbn: str
    rating: int

class AvgRatingRead(BaseModel):
    isbn: str
    avg_rating: float
    count: int # Num of ratings for this book.
