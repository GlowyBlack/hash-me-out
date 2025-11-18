from pathlib import Path
from app.models.review import Review
from app.utils.data_manager import CSVRepository
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate


class ReviewService:
    def __init__(self):
        self.repo = CSVRepository()
        self.path = str(Path(__file__).resolve().parents[1] / "data" / "Reviews.csv")
        self.fields = ["ReviewID", "UserID", "ISBN", "Comment", "Time"]

    def _read_rows(self):
        return self.repo.read_all(self.path)

    def _write_rows(self, rows):
        self.repo.write_all(self.path, self.fields, rows)

    def _generate_next_id(self) -> int:
        rows = self._read_rows()
        if not rows:
            return 1
        ids = [int(r["ReviewID"]) for r in rows if r["ReviewID"].isdigit()]
        return max(ids, default=0) + 1

    def _already_reviewed(self, user_id: int, isbn: str) -> bool:
        rows = self._read_rows()
        return any(r["UserID"] == str(user_id) and r["ISBN"] == isbn for r in rows)

    def create_review(self, user_id: int, data: ReviewCreate) -> ReviewRead:
        """
        1 review per user per book.
        """
        if self._already_reviewed(user_id, data.isbn):
            raise ValueError("This user has already reviewed this book.")

        next_id = self._generate_next_id()

        review = Review(
            review_id=next_id,
            user_id=user_id,
            isbn=data.isbn,
            comment=data.comment,
        )

        self.repo.append_row(self.path, self.fields, review.to_csv_dict())
        return ReviewRead(**review.to_api_dict())

    def get_all_reviews(self, isbn: str) -> list[ReviewRead]:
        rows = self._read_rows()
        filtered = [r for r in rows if r["ISBN"] == isbn]
        return [ReviewRead(**Review.from_dict(r).to_api_dict()) for r in filtered]

    def edit_review(self, review_id: int, data: ReviewUpdate) -> ReviewRead:
        rows = self._read_rows()
        found_row = None

        for r in rows:
            if r["ReviewID"] == str(review_id):
                r["Comment"] = data.comment
                found_row = r
                break

        if not found_row:
            raise ValueError("Review not found")

        self._write_rows(rows)
        updated_review = Review.from_dict(found_row)
        return ReviewRead(**updated_review.to_api_dict())

    def delete_review(self, review_id: int) -> bool:
        rows = self._read_rows()
        filtered = [r for r in rows if r["ReviewID"] != str(review_id)]

        if len(filtered) == len(rows):
            return False

        self._write_rows(filtered)
        return True
