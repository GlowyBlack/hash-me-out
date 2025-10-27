from pydantic import BaseModel, Field
from datetime import datetime

class ReviewCreate(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=13)
    comment: str = Field(..., min_length=8)

class ReviewRead(BaseModel):
    review_id: int
    user_id: int 
    isbn: str
    comment: str
    time: datetime
    
class ReviewUpdate(BaseModel):
    comment: str = Field(..., min_length=8)
