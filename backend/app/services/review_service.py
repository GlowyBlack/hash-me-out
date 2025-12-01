from pathlib import Path
from urllib.parse import quote_plus
import requests
from app.models.review import Review
from app.repositories.csv_repository import CSVRepository
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.user_service import CSVUserService

WEEK_IN_MINUTES = 7 * 24 * 60

class ReviewService:
    PURGOMALUM_URL = "https://www.purgomalum.com/service/containsprofanity"
    
    def __init__(self):
        self.repo = CSVRepository()
        self.path = Path(__file__).resolve().parents[1] / "data" / "Reviews.csv"
        self.fields = ["ReviewID", "UserID", "ISBN", "Comment", "Time"]
        self.user_service = CSVUserService(CSVRepository())

    def __read_rows(self):
        return self.repo.read_all(self.path)

    def __write_rows(self, rows):
        self.repo.write_all(self.path, self.fields, rows)

    def __generate_next_id(self) -> int:
        rows = self.__read_rows()
        if not rows:
            return 1
        ids = [int(r["ReviewID"]) for r in rows if r["ReviewID"].isdigit()]
        return max(ids, default=0) + 1

    def __already_reviewed(self, user_id: int, isbn: str) -> bool:
        rows = self.__read_rows()
        return any(r["UserID"] == str(user_id) and r["ISBN"] == isbn for r in rows)

    # -----------------------------------------------------------------------
    # PurgoMalum Profanity Check
    # -----------------------------------------------------------------------

    def _contains_profanity(self, text: str) -> bool:
        """Uses PurgoMalum API to detect profanity."""
        try:
            encoded = quote_plus(text)
            url = f"{self.PURGOMALUM_URL}?text={encoded}"
            resp = requests.get(url, timeout=3)
           
            if resp.status_code == 200:
                result = resp.text.strip().lower()
                if result == "true": # The API can fail entirely; treat non-true as no profanity
                    return True
                if result == "false":
                    return False
        except Exception:
            pass

        return False
    
    def _apply_profanity_penalty(self, user_id: int):
        """
        Applies the profanity penalty:
          - increments warnings
          - auto-suspends on 3rd warning
        """
        user_row = self.user_service.increment_warning(user_id)
        warnings_count = int(user_row.get("warnings", "0") or 0)

        if warnings_count >= 3:

            self.user_service.auto_suspend_for_profanity(
                target_id = user_id,
                duration_minutes = WEEK_IN_MINUTES,
            )
            raise ValueError("profanity_suspension")

        remaining = 3 - warnings_count
        raise ValueError(f"profanity_detected:{remaining}")

    def create_review(self, user_id: int, data: ReviewCreate, isbn: str) -> ReviewRead:
        """
        1 review per user per book.
        Also checks profanity:
          - increments warnings on each profane attempt
          - auto-suspends user for a while on 3rd warning
        """
        if self._contains_profanity(data.comment):
            self._apply_profanity_penalty(user_id)
            
        if self.__already_reviewed(user_id, isbn):
            raise ValueError("already_reviewed")

        next_id = self.__generate_next_id()

        review = Review(
            review_id=next_id,
            user_id=user_id,
            isbn=isbn,
            comment=data.comment,
        )

        self.repo.append_row(self.path, self.fields, review.to_csv_dict())
        return ReviewRead(**review.to_api_dict())

    def get_all_reviews(self, isbn: str) -> list[ReviewRead]:
        rows = self.__read_rows()
        filtered = [r for r in rows if r["ISBN"] == isbn]
        return [ReviewRead(**Review.from_dict(r).to_api_dict()) for r in filtered]

    def edit_review(
        self,
        review_id: int,
        user_id: int,
        data: ReviewUpdate,
    ) -> ReviewRead:
        """
        Edit an existing review.
        Rules:
          - Only the owner (matching user_id) can edit.
          - New comment goes through profanity / warnings / auto-suspension.
        """
        rows = self.__read_rows()
        found_row = None

        for r in rows:
            if r["ReviewID"] == str(review_id):
                found_row = r
                break

        if not found_row:
            raise ValueError("review_not_found")

        if found_row["UserID"] != str(user_id):
            raise PermissionError("not_owner")

        if self._contains_profanity(data.comment):
            self._apply_profanity_penalty(user_id)
            
        found_row["Comment"] = data.comment
        self.__write_rows(rows)

        updated_review = Review.from_dict(found_row)
        return ReviewRead(**updated_review.to_api_dict())

    def delete_review(self, review_id: int) -> bool:
        rows = self.__read_rows()
        original_count = len(rows)
        filtered = [r for r in rows if r["ReviewID"] != str(review_id)]
        
        if len(filtered) == original_count:
            return False

        for i, row in enumerate(filtered, start=1):
            row["ReviewID"] = str(i)

        self.__write_rows(filtered)
        
        return True