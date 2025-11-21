from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from app.schemas.book import BookItem
from app.utils.validators import validate_list_name

class ReadingListCreate(BaseModel):
    name: str = Field(..., description="Name of the Reading List")
    
    @field_validator("name")
    @classmethod
    def valid_name(cls, v: str) -> str:
        return validate_list_name(v)

class ReadingListRename(BaseModel):
    new_name: str = Field(..., description="New name of the Reading List")
    
    @field_validator("new_name")
    @classmethod
    def valid_name(cls, v: str) -> str:
        return validate_list_name(v)    
    
class ReadingListSummary(BaseModel):
    list_id: int
    name: str
    total_books: int = Field(..., description="Number of books in the list")
    is_public: bool

class ReadingListDetail(BaseModel):
    list_id: int
    user_id: int
    name: str
    books: List[BookItem] = Field(default_factory=list, description="Books inside the list")
    is_public: bool