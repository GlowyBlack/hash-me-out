
from pathlib import Path
from app.utils.data_manager import CSVRepository

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "Reviews.csv"

class ReviewService:
    def __init__(self):
        self.repo = CSVRepository()
        self.path = DATA_PATH
        self.fields = ["ReviewID", "UserID", "ISBN", "Comment", "Time"]
        
    
    def __generate_next_id(self) -> int:
        """
        Generate the next ReviewID number.
        - Reads all rows from the CSV file.
        - Finds the highest ReviewID currently in use.
        - Returns that number + 1.
        If the file is empty, it starts from 1.
        """
        rows = self.repo.read_all(self.path)
        if not rows:
            return 1
        ids = [int(r["ReviewtID"]) for r in rows if r["ReviewID"].isdigit()]
        return max(ids, default=0) + 1

    def _already_requested(self, user_id: int, isbn: str) -> bool:
        """
        Checks if this user has already review the same book 
        Steps:
        1. Reading every row from the CSV file.
        2. Then compares each row's UserID and ISBN to the ones passed in.
        3. If a match is found, returns True.
        4. Otherwise, returns False.
        """
        rows = self.repo.read_all(self.path)
        return any(r["UserID"] == str(user_id) and r["ISBN"] == isbn for r in rows)

        
