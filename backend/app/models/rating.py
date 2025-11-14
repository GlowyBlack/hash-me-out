from datetime import datetime

class Rating:
    def __init__(self, user_id: int, isbn: str, rating: int):
        self.user_id = user_id
        self.isbn = isbn
        self.rating = rating

    def to_api_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "isbn": self.isbn,
            "rating": self.rating,
            }

    def to_csv_dict(self) -> dict:
        return {
            "UserID": self.user_id,
            "ISBN": self.isbn,
            "Book-Rating": self.rating,
        }

    @classmethod
    def from_dict(cls, row: dict):
        return cls(
            user_id=int(row["UserID"]),
            isbn=row["ISBN"],
            rating=int(row["Book-Rating"]),
        )
