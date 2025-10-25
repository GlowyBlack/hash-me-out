from pydantic import BaseModel, Field
from datetime import datetime

class RequestCreate(BaseModel):
    book_title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: str = Field(..., min_length=10, max_length=13)

class RequestRead(BaseModel):
    request_id: int
    user_id: int = Field(..., gt=0)
    book_title: str
    author: str
    isbn: str
    time: datetime
