from pydantic import BaseModel, Field

class RatingCreate(BaseModel):
    rating: int = Field(..., ge=0, le=10)

class RatingRead(BaseModel):
    user_id: int = Field(..., gt=0)
    isbn: str
    rating: int

class AvgRatingRead(BaseModel):
    isbn: str
    avg_rating: float
    count: int 