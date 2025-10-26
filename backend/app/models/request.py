from datetime import datetime

class Request:
    """Domain model for a book request"""
    def __init__(self, request_id: int, user_id: int, book_title: str, author: str, isbn: str, time: datetime = None):
        self.request_id = request_id
        self.user_id = user_id
        self.book_title = book_title
        self.author = author
        self.isbn = isbn
        self.time = time or datetime.now().strftime("%Y-%m-%d")

    def to_api_dict(self) -> dict:
        """
        Convert this Request object into a dictionary formatted for API responses.
        Returns: dict containing all the Request information in API-friendly key names.
        """
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "book_title": self.book_title,
            "author": self.author,
            "isbn": self.isbn,
            "time": self.time.strftime("%Y-%m-%d"),
        }
        
    def to_csv_dict(self) -> dict:
        """
        Convert this Request object into a dictionary formatted for CSV storage.
        Created because api uses different keys than keys stored in csv file
        Returns: dict containing all Request information ready to be written to the CSV file.
        """
        return {
            "RequestID": self.request_id,
            "UserID": self.user_id,
            "Book Title": self.book_title,
            "Author": self.author,
            "ISBN": self.isbn,
            "Time": self.time.strftime("%Y-%m-%d"),
        }

    @classmethod
    def from_dict(cls, row: dict):
        return cls(
            request_id=int(row["RequestID"]),
            user_id=int(row["UserID"]),
            book_title=row["Book Title"],
            author=row["Author"],
            isbn=row["ISBN"],
            time=datetime.strptime(row["Time"], "%Y-%m-%d")
        )

    def matches_user(self, user_id: int) -> bool:
        return self.user_id == user_id

    def matches_isbn(self, isbn: str) -> bool:
        return self.isbn == isbn
