from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app.utils.validators import validate_isbn

class RequestCreate(BaseModel):
    title: str = Field(..., min_length=1)   
    author: str = Field(..., min_length=1)
    isbn: str
    notes: Optional[str] = None

class RequestRead(BaseModel):
    request_id: int
    user_id: int = Field(..., gt=0)
    book_title: str
    author: str
    isbn: str
