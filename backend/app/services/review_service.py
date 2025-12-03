from pathlib import Path
from urllib.parse import quote_plus
from datetime import datetime
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

    # --------------------------------------------------------------------
    # Internal CSV helpers
    # --------------------------------------------------------------------

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

    # --------------------------------------------------------------------
    # Profanity + Penalty
    # --------------------------------------------------------------------

    def _contains_profanity(self, text: str) -> bool:
        """Detects if text contains profanity using PurgoMalum."""
        try:
            encoded = quote_plus(text)
            url = f"{self.PURGOMALUM_URL}?text={encoded}"
            resp = requests.get(url, timeout=3)

            if resp.status_code == 200:
                result = resp.text.strip().lower()
                return result == "true"
        except Exception:
            pass

        return False

    def _apply_profanity_penalty(self, user_id: int):
        """Adds warnings, and auto-suspends if the user reaches 3 warnings."""
        user_row = self.user_service.increment_warning(user_id)
        warnings_count = int(user_row.get("warnings", "0") or 0)

        if warnings_count >= 3:
            self.user_service.auto_suspend_for_profanity(
                target_id=user_id,
                duration_minutes=WEEK_IN_MINUTES,
            )
            raise ValueError("profanity_suspension")

        remaining = 3 - warnings_count
        raise ValueError(f"profanity_detected:{remaining}")

    # --------------------------------------------------------------------
    # CREATE REVIEW
    # --------------------------------------------------------------------

    def create_review(self, user_id: int, data: ReviewCreate, isbn: str) -> ReviewRead:
        if self._contains_profanity(data.comment):
            self._apply_profanity_penalty(user_id)

        if self.__already_reviewed(user_id, isbn):
            raise ValueError("already_reviewed")

        next_id = self.__generate_next_id()
        now = datetime.now()

        review = Review(
            review_id=next_id,
            user_id=user_id,
            isbn=isbn,
            comment=data.comment,
            time=now,
        )

        self.repo.append_row(self.path, self.fields, review.to_csv_dict())

        user = self.user_service.get_by_id(user_id)
        username = user["username"] if user else f"User #{user_id}"

        return ReviewRead(
            review_id=next_id,
            user_id=user_id,
            username=username,
            isbn=isbn,
            comment=data.comment,
            time=now,
        )

        # --------------------------------------------------------------------
    # GET ALL REVIEWS
    # --------------------------------------------------------------------

    def get_all_reviews(self, isbn: str) -> list[ReviewRead]:
        """
        Returns all reviews for a given ISBN, enriched with:
        - username (via CSVUserService)
        - rating (via Ratings.csv, if present)

        Keeps CSV schemas unchanged and avoids tight coupling
        by doing the join only in this service layer.
        """
        rows = self.__read_rows()

        # --- Load ratings for this book ----------------------------------
        rating_path = Path(__file__).resolve().parents[1] / "data" / "Ratings.csv"
        rating_rows = self.repo.read_all(rating_path)

        # (user_id, isbn) -> rating
        rating_lookup: dict[tuple[str, str], int] = {}
        for r in rating_rows:
            # Defensive checks in case of bad rows
            uid = r.get("UserID")
            r_isbn = r.get("ISBN")
            rating_val = r.get("Rating")

            if uid is None or r_isbn is None or rating_val is None:
                continue

            try:
                rating_int = int(rating_val)
            except ValueError:
                continue

            rating_lookup[(uid, r_isbn)] = rating_int

        # --- Cache usernames so we don't hit Users.csv for every row -----
        user_cache: dict[str, str] = {}

        enriched: list[ReviewRead] = []

        for r in rows:
            if r["ISBN"] != isbn:
                continue

            # Base review fields from model
            review = Review.from_dict(r)
            review_dict = review.to_api_dict()
            # review_dict now has: review_id, user_id, isbn, comment, time

            uid_str = r["UserID"]  # note: this is the string ID from CSV

            # Attach rating (if exists)
            key = (uid_str, isbn)
            review_dict["rating"] = rating_lookup.get(key)

            # Attach username
            if uid_str in user_cache:
                username = user_cache[uid_str]
            else:
                user = self.user_service.get_by_id(int(uid_str))
                if user:
                    username = user["username"]
                else:
                    username = f"User #{uid_str}"
                user_cache[uid_str] = username

            review_dict["username"] = username

            # Convert to ReviewRead so response_model validation passes
            enriched.append(ReviewRead(**review_dict))

        return enriched

    # --------------------------------------------------------------------
    # EDIT REVIEW
    # --------------------------------------------------------------------

    def edit_review(self, review_id: int, user_id: int, data: ReviewUpdate) -> ReviewRead:
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
        found_row["Time"] = datetime.now().isoformat()

        self.__write_rows(rows)

        updated_review = Review.from_dict(found_row)
        review_dict = updated_review.to_api_dict()

        user = self.user_service.get_by_id(user_id)
        review_dict["username"] = user["username"] if user else f"User #{user_id}"

        return ReviewRead(**review_dict)

    # --------------------------------------------------------------------
    # DELETE REVIEW
    # --------------------------------------------------------------------

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