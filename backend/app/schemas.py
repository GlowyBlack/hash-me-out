from pydantic import BaseModel

class BookRequest(BaseModel):
    bookTitle: str
    author: str
    isbn: str
