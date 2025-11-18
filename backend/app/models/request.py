from datetime import datetime

class Request:
    def __init__(self, request_id: int, user_id: int, book_title: str, author: str, isbn: str, time: datetime = None):
        self.request_id = request_id
        self.user_id = user_id
        self.book_title = book_title
        self.author = author
        self.isbn = isbn
        self.time = time or datetime.now().strftime("%Y-%m-%d")

    def to_api_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "book_title": self.book_title,
            "author": self.author,
            "isbn": self.isbn,
        }
        
    def to_csv_dict(self) -> dict:
        return {
            "RequestID": self.request_id,
            "UserID": self.user_id,
            "Book Title": self.book_title,
            "Author": self.author,
            "ISBN": self.isbn,
        }

    @classmethod
    def from_dict(cls, row: dict):
        return cls(
            request_id=int(row["RequestID"]),
            user_id=int(row["UserID"]),
            book_title=row["Book Title"],
            author=row["Author"],
            isbn=row["ISBN"],
        )

    def matches_user(self, user_id: int) -> bool:
        return self.user_id == user_id

    def matches_isbn(self, isbn: str) -> bool:
        return self.isbn == isbn
