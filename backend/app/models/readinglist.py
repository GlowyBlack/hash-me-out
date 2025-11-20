from datetime import datetime
from typing import List, Dict
from app.schemas.book import BookItem
from app.utils.data_manager import CSVRepository

class ReadingList:
    def __init__(self, list_id: int, user_id: int, name: str, books: List[BookItem] = None, is_public: bool = False):
        self.list_id = list_id
        self.user_id = user_id
        self.name = name
        self.books = books or []
        self.is_public = is_public
        
    def to_csv_dict(self) -> dict:

        return {
            "ListID": self.list_id,
            "UserID": self.user_id,
            "Name": self.name,
            "ISBNs": "|".join(self.books) if self.books else "",
            "IsPublic": "true" if self.is_public else "false",
        }
        
        
    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "ReadingList":
        return cls(
            list_id = int(row["ListID"]),
            user_id = int(row["UserID"]),
            name = row["Name"],
            books = row.get("ISBNs", "").split("|") if row.get("ISBNs") else [],
            is_public=row.get("IsPublic", "false") == "true"
        )

    def to_api_dict(self) -> dict:
        book_info_list =self.__get_book_info()
        return {
            "list_id": self.list_id,
            "user_id": self.user_id,
            "name": self.name,
            "books": book_info_list,
            "is_public": self.is_public,
        }
                
    def __get_book_info(self):
        books_path = "app/data/Books.csv"
        repo = CSVRepository()
        all_books = repo.read_all(books_path)
        book_lookup = {row["ISBN"]: row for row in all_books}

        returned_books = []
        for isbn in self.books:
            book_data = book_lookup.get(isbn)
            if book_data:
                returned_books.append({
                    "isbn": isbn,
                    "book_title": book_data.get("Book-Title", "Unknown Title"),
                    "author": book_data.get("Book-Author", "Unknown Author")
                })
            else:
                returned_books.append({
                    "isbn": isbn,
                    "book_title": "Unknown Title",
                    "author": "Unknown Author"
                })
        return returned_books
             
    def rename(self, new_name: str):
        self.name = new_name
        
    def add_book(self, isbn: str):
        if isbn in self.books:
            return ValueError(f"Book {isbn} already in reading list.")
        self.books.append(isbn)
        
    def remove_book(self, isbn: str):
        self.books = [b for b in self.books if b != isbn]

    def total_books(self) -> int:
        return len(self.books)
    
