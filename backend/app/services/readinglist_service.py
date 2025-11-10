from pathlib import Path
from app.models.request import Request
from app.schemas.readinglist import ReadingListCreate 

from app.utils.data_manager import CSVRepository 

class ReadingListService:
    def __init__(self):
        self.repo = CSVRepository()
        self.path = Path(__file__).resolve().parents[1] / "data" / "ReadingLists.csv"
        self.fields = ["ListID", "UserID", "Name", "ISBNs"]
        
    def __generate_next_id(self) -> int:
        """
        Generate the next ReviewID number.
        """
        rows = self.repo.read_all(self.path)
        if not rows:
            return 1
        ids = [int(r["ListID"]) for r in rows if r["ListID"].isdigit()]
        return max(ids, default=0) + 1

    def __already_added(self, list_id: int, isbn: str) -> bool:
        rows = self.repo.read_all(self.path)
        
        found = False
        for row in rows:
            if row["ListID"] == str(list_id):
                books = row["ISBNs"].split("|") if row["ISBNs"] else []
                if isbn in books:
                    found = True
                break
        
        
        return found
        
        
        