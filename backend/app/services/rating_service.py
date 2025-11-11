# app/services/rating_service.py
from pathlib import Path
from statistics import mean
from app.models.rating import Rating
from app.utils.data_manager import CSVRepository
from app.schemas.rating import RatingCreate, RatingRead, AvgRatingRead


class RatingService:
    def __init__(self):
        self.repo = CSVRepository()
        self.ratings_path = str(Path(__file__).resolve().parents[1] / "data" / "Ratings.csv")
        self.fields = ["UserID", "ISBN", "Book-Rating"]

    def _read_rows(self):
        return self.repo.read_all(self.ratings_path)

    def _write_rows(self, rows):
        self.repo.write_all(self.ratings_path, self.fields, rows)
        
    '''
    This method creates or updates a rating for a given user and book.
    Args:
        user_id (int): The ID of the user creating the rating.
        rating_data (RatingCreate): The data for the rating, including ISBN and rating value.
    Returns:    
        RatingRead: The created or updated rating.
    '''

    def create_rating(self, user_id: int, rating_data: RatingCreate) -> RatingRead:
        """Upsert: update if (user_id, isbn) exists; else create."""
        rows = self._read_rows()
        uid = str(user_id)
        isbn = rating_data.isbn

        updated = False
        for r in rows:
            if r["UserID"] == uid and r["ISBN"] == isbn:
                r["Book-Rating"] = str(rating_data.rating)
                updated = True
                break

        if updated:
            self._write_rows(rows)
        else:
            rating = Rating(user_id=user_id, isbn=isbn, rating=rating_data.rating)
            self.repo.append_row(self.ratings_path, self.fields, rating.to_csv_dict())

        return RatingRead(user_id=user_id, isbn=isbn, rating=rating_data.rating)
    
    '''
    This method retrieves a user's rating for a specific book.
    Args:
        user_id (int): The ID of the user.
        isbn (str): The ISBN of the book.
    Returns:  
        RatingRead | None: The user's rating for the book, or None if not found.   
        
    '''
    def get_user_rating(self, user_id: int, isbn: str) -> RatingRead | None:
        for row in self._read_rows():
            if row["UserID"] == str(user_id) and row["ISBN"] == isbn:
                return RatingRead(user_id=int(row["UserID"]), isbn=row["ISBN"], rating=int(row["Book-Rating"]))
        return None
    
    '''
    This method retrieves all ratings in the system.
    Returns:    
        list[RatingRead]: A list of all ratings.
    '''
    def get_all_ratings(self) -> list[RatingRead]:
        return [
            RatingRead(user_id=int(r["UserID"]), isbn=r["ISBN"], rating=int(r["Book-Rating"]))
            for r in self._read_rows()
        ]

    '''
    This method deletes a user's rating for a specific book.
    Args:
        user_id (int): The ID of the user.
        isbn (str): The ISBN of the book.
    Returns:
        bool: True if the rating was deleted, False if not found.
    '''
    def delete_rating(self, user_id: int, isbn: str) -> bool:
        rows = self._read_rows()
        filtered = [r for r in rows if not (r["UserID"] == str(user_id) and r["ISBN"] == isbn)]
        if len(filtered) == len(rows):
            return False
        self._write_rows(filtered)
        return True
    
    '''
    This method retrieves all ratings for a specific book.  
    Args:
        isbn (str): The ISBN of the book.
    Returns:
        list[RatingRead]: A list of ratings for the specified book.
    '''
    def get_ratings_by_isbn(self, isbn: str) -> list[RatingRead]:
        return [
            RatingRead(user_id=int(r["UserID"]), isbn=r["ISBN"], rating=int(r["Book-Rating"]))
            for r in self._read_rows() if r["ISBN"] == isbn
        ]

    '''
    This method calculates the average rating for a specific book.
    Args:
        isbn (str): The ISBN of the book.
    Returns:
        AvgRatingRead: The average rating and count of ratings for the book.
    '''
    def get_avg_rating(self, isbn: str) -> AvgRatingRead:
        book_ratings = self.get_ratings_by_isbn(isbn)
        if not book_ratings:
            return AvgRatingRead(isbn=isbn, avg_rating=0.0, count=0)
        avg = mean(r.rating for r in book_ratings)
        return AvgRatingRead(isbn=isbn, avg_rating=round(avg, 2), count=len(book_ratings))
