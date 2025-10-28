
from pathlib import Path
from app.models.review import Review
from app.utils.data_manager import CSVRepository
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate


class ReviewService:
    def __init__(self):
        self.repo = CSVRepository()
        self.path = Path(__file__).resolve().parents[1] / "data" / "Reviews.csv"
        self.fields = ["ReviewID", "UserID", "ISBN", "Comment", "Time"]
        
    
    def __generate_next_id(self) -> int:
        """
        Generate the next ReviewID number.
        """
        rows = self.repo.read_all(self.path)
        if not rows:
            return 1
        ids = [int(r["ReviewtID"]) for r in rows if r["ReviewID"].isdigit()]
        return max(ids, default=0) + 1

    def _already_reviewed(self, user_id: int, isbn: str) -> bool:
        """
        Checks if this user has already review the same book 
        """
        rows = self.repo.read_all(self.path)
        return any(r["UserID"] == str(user_id) and r["ISBN"] == isbn for r in rows)

    
    def create_review(self, user_id: int, data: ReviewCreate) -> ReviewRead:
        next_id = self.__generate_next_id()
        if self._already_reviewed(user_id, data.isbn):
            raise ValueError("This user has already reviewed this book.")
        
        review = Review(
            review_id= next_id,
            user_id= user_id,
            isbn= data.isbn,
            comment= data.comment
        )
        
        self.repo.append_row(self.path, self.fields, review.to_csv_dict())
        return ReviewRead(**review.to_api_dict())
    
    def get_all_reviews(self, isbn: str) -> list[ReviewRead]:
        rows = self.repo.read_all(self.path) 
        filtered_reviews = [r for r in rows if r["ISBN"] == isbn]
        return [ReviewRead(**Review.from_dict(r).to_api_dict()) for r in filtered_reviews]


    def edit_review(self, data: ReviewUpdate) -> ReviewRead:
        rows = self.repo.read_all(self.path)
        
        pass