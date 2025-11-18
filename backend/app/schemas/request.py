from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app.utils.validators import validate_isbn

class RequestCreate(BaseModel):
    book_title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: str 

    @field_validator("isbn")
    @classmethod
    def valid_isbn(cls, v: str) -> str:
        return validate_isbn(v)
    
class RequestRead(BaseModel):
    request_id: int
    user_id: int = Field(..., gt=0)
    book_title: str
    author: str
    isbn: str
