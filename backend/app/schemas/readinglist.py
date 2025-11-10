from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from app.schemas.book import BookItem

class ReadingListCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the Reading List")

class ReadingListRename(BaseModel):
    new_name: str = Field(..., min_length=1, description="New name of the Reading List")

class ReadingListSummary(BaseModel):
    name: str
    total_books: int = Field(..., description="Number of books in the list")

class ReadingListDetail(BaseModel):
    name: str = Field(..., min_length=1)
    books: List[BookItem] = Field(default_factory=list, description="Books inside the list")