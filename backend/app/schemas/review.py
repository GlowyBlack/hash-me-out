from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app.utils.validators import validate_comment

class ReviewCreate(BaseModel):
    comment: str = Field(..., min_length=8)
    
    @field_validator("comment")
    @classmethod
    def valid_isbn(cls, v: str) -> str:
        return validate_comment(v)
    
class ReviewRead(BaseModel):
    review_id: int
    user_id: int 
    isbn: str
    comment: str
    time: datetime
    
class ReviewUpdate(BaseModel):
    comment: str = Field(..., min_length=8, max_length=500)

    @field_validator("comment")
    @classmethod
    def valid_isbn(cls, v: str) -> str:
        return validate_comment(v)