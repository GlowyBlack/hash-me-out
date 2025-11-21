from pathlib import Path
from statistics import mean
from app.models.rating import Rating
from app.utils.data_manager import CSVRepository
from app.schemas.rating import RatingRead, AvgRatingRead


class RatingService:
    def __init__(self):
        self.repo = CSVRepository()
        self.ratings_path = str(Path(__file__).resolve().parents[1] / "data" / "Ratings.csv")
        self.fields = ["UserID", "ISBN", "Book-Rating"]

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def __read(self):
        return self.repo.read_all(self.ratings_path)

    def __write(self, rows):
        self.repo.write_all(self.ratings_path, self.fields, rows)

    def __match(self, row, user_id, isbn):
        return row["UserID"] == str(user_id) and row["ISBN"] == isbn

    def __to_read_model(self, row):
        return RatingRead(
            user_id = int(row["UserID"]),
            isbn = row["ISBN"],
            rating = int(row["Book-Rating"]),
        )

    # -----------------------------------------------------------------------
    # Public API 
    # -----------------------------------------------------------------------

    def create_rating(self, user_id: int, isbn: str, rating_value: int) -> RatingRead:
        """
        Create or update a rating for the specified user/book.
        """
        rows = self.__read()

        for row in rows:
            if self.__match(row, user_id, isbn):
                row["Book-Rating"] = str(rating_value)
                self.__write(rows)
                return self.__to_read_model(row)

        rating = Rating(user_id, isbn, rating_value)
        self.repo.append_row(self.ratings_path, self.fields, rating.to_csv_dict())
        return self.__to_read_model(rating.to_csv_dict())

    def get_user_rating(self, user_id: int, isbn: str) -> RatingRead | None:
        """
        Return a user's rating for a specific book, or None if not found.
        """
        for row in self.__read():
            if self.__match(row, user_id, isbn):
                return self.__to_read_model(row)
        return None

    def get_all_ratings(self) -> list[RatingRead]:
        return [self.__to_read_model(r) for r in self.__read()]

    def delete_rating(self, user_id: int, isbn: str) -> bool:
        rows = self.__read()
        filtered = [r for r in rows if not self.__match(r, user_id, isbn)]

        if len(filtered) == len(rows):
            return False

        self.__write(filtered)
        return True

    def get_ratings_by_isbn(self, isbn: str) -> list[RatingRead]:
        return [
            self.__to_read_model(r)
            for r in self.__read()
            if r["ISBN"] == isbn
        ]

    def get_avg_rating(self, isbn: str) -> AvgRatingRead:
        """
        Compute the average rating for a book.
        If no ratings exist, return 0.0 and count 0.
        """
        ratings = self.get_ratings_by_isbn(isbn)

        if not ratings:
            return AvgRatingRead(isbn = isbn, avg_rating = 0.0, count = 0)

        avg = mean(r.rating for r in ratings)
        return AvgRatingRead(isbn = isbn, avg_rating = round(avg, 2), count = len(ratings))
