from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.utils.validators import validate_isbn

class BookCreate(BaseModel):
    isbn: str  =Field(..., description="ISBN must be 10 or 13 digits")
    book_title: str = Field(..., min_length=1, description="Title of the book")
    author: str = Field(..., min_length=1, description="Author of the book")
    year_of_publication: Optional[str] = Field(None, description="Year the book was published")
    publisher: Optional[str] = Field(None, description="Publisher of the book")
    image_url_s: Optional[str] = Field(None, description="Small image URL of Book Cover")
    image_url_m: Optional[str] = Field(None, description="Medium image URL of Book Cover")
    image_url_l: Optional[str] = Field(None, description="Large image URL of Book Cover")
    
    @field_validator("isbn")
    @classmethod
    def valid_isbn(cls, v: str) -> str:
        return validate_isbn(v)

class BookRead(BaseModel):
    isbn: str  
    book_title: str 
    author: str 
    year_of_publication: Optional[str] 
    publisher: Optional[str] 
    image_url_s: Optional[str] 
    image_url_m: Optional[str] 
    image_url_l: Optional[str] 

class BookUpdate(BaseModel):
    isbn: str  
    book_title: str 
    author: str 
    year_of_publication: Optional[str] 
    publisher: Optional[str] 
    image_url_s: Optional[str] 
    image_url_m: Optional[str] 
    image_url_l: Optional[str] 

class BookItem(BaseModel):
    book_title: str
    author: str
    isbn: str