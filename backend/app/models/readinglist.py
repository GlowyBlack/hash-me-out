from datetime import datetime
from typing import List, Dict
from app.schemas.book import BookItem
from app.utils.data_manager import CSVRepository

class ReadingList:
    def __init__(self, list_id: int, user_id: int, name: str, books: List[BookItem] = None):
        self.list_id = list_id
        self.user_id = user_id
        self.name = name
        self.books = books or []
        
    def to_csv_dict(self) -> dict:
        """
        Convert this Review object into a dictionary formatted for CSV storage.
        """
        return {
            "ListID": self.list_id,
            "UserID": self.user_id,
            "Name": self.name,
            "ISBNs": "|".join(self.books) if self.books else "",
        }
        
        
    @classmethod
    def from_dict(cls, row: dict):
        
        return cls(
            review_id=int(row["ReviewID"]),
            user_id=int(row["UserID"]),
            isbn=row["ISBN"],
            comment=row["Comment"],
            time=datetime.strptime(row["Time"], "%Y-%m-%d")
        )

    def to_api_dict(self) -> dict:
        book_info_list = ""
        return {
            "list_id": self.list_id,
            "user_id": self.user_id,
            "name": self.name,
            "books": book_info_list
        }
            
    
    def __get_book_info(self):
        books_path = "app/data/BX_Books.csv"
        repo = CSVRepository()
        all_books = repo.read_all(books_path)
     
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