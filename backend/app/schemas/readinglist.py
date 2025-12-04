from pydantic import BaseModel, Field, field_validator
from typing import List
from app.schemas.book import BookItem

class ReadingListCreate(BaseModel):
    name: str = Field(..., description="Name of the Reading List")

    @field_validator("name")
    @classmethod
    def valid_name(cls, v: str) -> str:
        # Strip spaces and validate
        v = v.strip()
        if not v:
            # This becomes a 422 Unprocessable Entity in FastAPI
            raise ValueError("Reading list name cannot be empty or whitespace.")
        return v


class ReadingListRename(BaseModel):
    new_name: str = Field(..., description="New name of the Reading List")

    @field_validator("new_name")
    @classmethod
    def valid_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Reading list name cannot be empty or whitespace.")
        return v


class ReadingListSummary(BaseModel):
    list_id: int
    name: str
    total_books: int = Field(..., description="Number of books in the list")
    is_public: bool


class ReadingListDetail(BaseModel):
    list_id: int
    user_id: int
    name: str
    books: List[BookItem] = Field(
        default_factory=list,
        description="Books inside the list",
    )
    is_public: bool
