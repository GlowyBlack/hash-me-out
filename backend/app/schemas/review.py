from pydantic import BaseModel, Field
from datetime import datetime

class ReviewCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    isbn: str = Field(..., min_length=10, max_length=13)
    comment: str = Field(..., min_length=8)
    author: str = Field(..., min_length=1)

class ReviewRead(BaseModel):
    review_id: int
    user_id: int = Field(..., gt=0)
    isbn: str
    comment: str
    time: datetime
