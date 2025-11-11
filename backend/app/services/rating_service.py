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
            
    '''
    This method checks if a user has already rated a specific book.
    
    Args:
        user_id (int): The ID of the user.
        isbn (str): The ISBN of the book.
    Returns:
        bool: True if the user has already rated the book, False otherwise.
    
    ''' 
    def already_rated(self, user_id: int, isbn: str) -> bool:
        rows = self.repo.read_all(self.ratings_path) # read all rows (user id, isbn, rating) from the CSV file
        return any(r["UserID"] == str(user_id) and r["ISBN"] == isbn for r in rows) # user id and book already in row in file? rating must already exist, return false
    
    '''
    This method creates a new rating for a book by a user.
    
    Args:
        user_id (int): The ID of the user.
        rating_data (RatingCreate): The rating data containing ISBN and rating value.
    Returns:
        RatingRead: The created rating data.    
    '''  
    def create_rating(self, user_id: int, rating_data: RatingCreate) -> RatingRead:
        if self.already_rated(user_id, rating_data.isbn):
            raise ValueError("This user has already rated this book.")

        rating = Rating(user_id=user_id, isbn=rating_data.isbn, rating=rating_data.rating)

        self.repo.append_row(self.ratings_path, self.fields, rating.to_csv_dict())

        return RatingRead(user_id=rating.user_id, isbn=rating.isbn, rating=rating.rating)

        
    '''
    This method calculates the average rating for a book based on its ISBN.
    
    Args:
        isbn (str): The ISBN of the book.
    Returns:
        AvgRatingRead: The average rating data including ISBN, average rating, and count of ratings.
    '''   
    def get_avg_rating(self, isbn: str) -> AvgRatingRead:
        book_ratings = self.get_ratings_by_isbn(isbn)
        if not book_ratings:
            return AvgRatingRead(isbn=isbn, avg_rating=0.0, count=0) # no ratings? avg is 0
        avg = mean(r.rating for r in book_ratings) # the rating value for each rating in book_ratings
        return AvgRatingRead(isbn=isbn, avg_rating=round(avg, 2), count=len(book_ratings))
    
    '''
    This method retrieves a user's rating for a specific book.
    
    Args:
        user_id (int): The ID of the user.
        isbn (str): The ISBN of the book.
    Returns:
        RatingRead | None: The user's rating data if found, otherwise None.
    
    '''
    def get_user_rating(self, user_id: int, isbn: str) -> RatingRead | None:
        rows = self.repo.read_all(self.ratings_path)
        for row in rows:
            if row["UserID"] == str(user_id) and row["ISBN"] == isbn:
                rating = Rating.from_dict(row)
                return RatingRead(
                    user_id=rating.user_id,
                    isbn=rating.isbn,
                    rating=rating.rating,
                )
        return None
    
    '''
    This method retrieves all ratings from the data source.
    
    Returns:
        list[RatingRead]: A list of all rating data.
        
    '''
    def get_all_ratings(self) -> list[RatingRead]:
        rows = self.repo.read_all(self.ratings_path)
        ratings = []
        for row in rows:
            rating = Rating.from_dict(row)
            ratings.append(RatingRead(
                user_id=rating.user_id,
                isbn=rating.isbn,
                rating=rating.rating,
            ))
        return ratings
    
    '''
    This method deletes a user's rating for a specific book.
    
    Args:
        user_id (int): The ID of the user.
        isbn (str): The ISBN of the book.
    Returns:
        bool: True if the rating was deleted, False if not found.
    '''
    
    def delete_rating(self, user_id: int, isbn: str) -> bool:
        rows = self.repo.read_all(self.ratings_path)
        og_length = len(rows)
        filtered_rows = [r for r in rows if not (r["UserID"] == str(user_id) and r["ISBN"] == isbn)]
        if len(filtered_rows) == og_length:
            return False

        self.repo.write_all(self.ratings_path, self.fields, filtered_rows)
        return True
    
    '''
    This method retrieves all ratings for a specific book based on its ISBN.
    Args:
        isbn (str): The ISBN of the book.
    Returns:    
        list[RatingRead]: A list of rating data for the specified book.
    '''
    def get_ratings_by_isbn(self, isbn: str) -> list[RatingRead]:
        rows = self.repo.read_all(self.ratings_path)
        ratings = []
        for row in rows:
            if row["ISBN"] == isbn: # filter by isbn
                rating = Rating.from_dict(row) # create internal rating object from row dict (raw dictionary to rating model obj)
                ratings.append(RatingRead( # convert internal object to output schema for FastAPI
                    user_id=rating.user_id,
                    isbn=rating.isbn,
                    rating=rating.rating,
                ))
        return ratings