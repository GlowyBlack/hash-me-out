from pathlib import Path
from app.models.review import Review
from app.utils.data_manager import CSVRepository
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate


class ReviewService:
    """
    Service for creating, retrieving, editing, and deleting book reviews.

    All CSV access is centralized through helper methods to reduce duplication
    and follow SRP (Single Responsibility Principle).
    """

    def __init__(self):
        self.repo = CSVRepository()
        self.path = Path(__file__).resolve().parents[1] / "data" / "Reviews.csv"
        self.fields = ["ReviewID", "UserID", "ISBN", "Comment", "Time"]

    # ------------------------------------------------------------------
    # CSV helpers
    # ------------------------------------------------------------------

    def __read_rows(self):
        return self.repo.read_all(self.path)

    def __write_rows(self, rows):
        self.repo.write_all(self.path, self.fields, rows)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def __generate_next_id(self) -> int:
        rows = self.__read_rows()
        ids = [int(r["ReviewID"]) for r in rows if r["ReviewID"].isdigit()]
        return max(ids, default=0) + 1

    def __find_row_by_id(self, review_id: int):
        rid = str(review_id)
        for r in self.__read_rows():
            if r["ReviewID"] == rid:
                return r
        return None

    def __already_reviewed(self, user_id: int, isbn: str) -> bool:
        uid = str(user_id)
        return any(
            r["UserID"] == uid and r["ISBN"] == isbn
            for r in self.__read_rows()
        )

    def __resequence_ids(self, rows):
        for i, row in enumerate(rows, start=1):
            row["ReviewID"] = str(i)

    # ------------------------------------------------------------------
    #  API
    # ------------------------------------------------------------------

    def create_review(self, user_id: int, data: ReviewCreate) -> ReviewRead:
        """
        Create a review unless one already exists for this user/book pair.
        """
        if self.__already_reviewed(user_id, data.isbn):
            raise ValueError("This user has already reviewed this book.")

        new_id = self.__generate_next_id()
        review = Review(
            review_id=new_id,
            user_id=user_id,
            isbn=data.isbn,
            comment=data.comment,
        )

        self.repo.append_row(self.path, self.fields, review.to_csv_dict())
        return ReviewRead(**review.to_api_dict())

    def get_all_reviews(self, isbn: str) -> list[ReviewRead]:
        rows = self.__read_rows()
        return [
            ReviewRead(**Review.from_dict(r).to_api_dict())
            for r in rows if r["ISBN"] == isbn
        ]

    def edit_review(self, review_id: int, data: ReviewUpdate) -> ReviewRead:
        rows = self.__read_rows()
        row = None

        for r in rows:
            if r["ReviewID"] == str(review_id):
                r["Comment"] = data.comment
                row = r
                break

        if row is None:
            raise ValueError("Review not found")

        self.__write_rows(rows)
        updated = Review.from_dict(row)
        return ReviewRead(**updated.to_api_dict())

    def delete_review(self, review_id: int) -> bool:
        rows = self.__read_rows()
        filtered = [r for r in rows if r["ReviewID"] != str(review_id)]

        if len(filtered) == len(rows):
            return False

        self.__resequence_ids(filtered)
        self.__write_rows(filtered)
        return True
