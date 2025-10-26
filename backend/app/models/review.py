from datetime import datetime

class Review:
    def __init__(self, review_id: int, user_id: int, isbn: str, comment: str, time: datetime = None):
        self.review_id = review_id
        self.user_id = user_id
        self.isbn = isbn
        self.comment = comment
        self.time = time or datetime.now()
        
    def to_api_dict(self) -> dict:
        """
        Convert this Review object into a dictionary formatted for API responses.
        Returns: dict containing all the Review information in API-friendly key names.
        """
        return {
            "review_id": self.review_id,
            "user_id": self.user_id,
            "isbn": self.isbn,
            "comment": self.comment,
            "time": self.time.strftime("%Y-%m-%d"),
        }
            
    def to_csv_dict(self) -> dict:
        """
        Convert this Review object into a dictionary formatted for CSV storage.
        Returns: dict containing all Review information ready to be written to the CSV file.
        """
        return {
            "ReviewID": self.review_id,
            "UserID": self.user_id,
            "ISBN": self.isbn,
            "Comment": self.comment,
            "Time": self.time.strftime("%Y-%m-%d"),
        }
        
    @classmethod
    def from_dict(cls, row: dict):
        """
        Factory method that allows us to create a class instance from a dictionary of data 
        reading from CSV/JSON sources
        """
        return cls(
            review_id=int(row["ReviewID"]),
            user_id=int(row["UserID"]),
            isbn=row["ISBN"],
            comment=row["Comment"],
            time=datetime.strptime(row["Time"], "%Y-%m-%d")
        )