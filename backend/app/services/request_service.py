from datetime import datetime
from pathlib import Path
from app.models.request import Request
from app.schemas.request import RequestCreate, RequestRead 
from app.utils.data_manager import CSVRepository 

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "Requests.csv"

class RequestService:
    def __init__(self):
        self.repo = CSVRepository()
        self.path = DATA_PATH
        self.fields = ["RequestID", "UserID", "Book Title", "Author", "ISBN", "Time"]


    def _generate_next_id(self) -> int:
        """
        Generate the next RequestID number.
        - Reads all rows from the CSV file.
        - Finds the highest RequestID currently in use.
        - Returns that number + 1.
        If the file is empty, it starts from 1.
        """
        rows = self.repo.read_all(self.path)
        if not rows:
            return 1
        ids = [int(r["RequestID"]) for r in rows if r["RequestID"].isdigit()]
        return max(ids, default=0) + 1

    def _already_requested(self, user_id: int, isbn: str) -> bool:
        """
        Checks if this user has already requested the same book 
        Steps:
        1. Reading every row from the CSV file.
        2. Then compares each row's UserID and ISBN to the ones passed in.
        3. If a match is found, returns True.
        4. Otherwise, returns False.
        """
        rows = self.repo.read_all(self.path)
        return any(r["UserID"] == str(user_id) and r["ISBN"] == isbn for r in rows)

    def get_all_requests(self) -> list[RequestRead]:
        """
        Retrieve all requests from the requests.csv file.
        Steps:
        1. Read every row from the CSV file.
        2. Convert each row (which is a dictionary of strings) into a Request object.
        3. Convert each Request object back into an API-friendly dictionary using .to_api_dict().
        4. Wrap each dictionary in a the RequestRead schema so FastAPI can send it safely as JSON.

        Returns:
            A list of RequestRead objects representing all book requests.
        """
        rows = self.repo.read_all(self.path)
        return [RequestRead(**Request.from_dict(r).to_api_dict()) for r in rows]

    def __update_total_requested(self, isbn: str):
        path = "app/data/Total_Requested.csv"
        fieldnames = ["ISBN", "Total Requested"]
        rows = self.repo.read_all(path)
        found = False

        for r in rows:
            if r["ISBN"] == isbn:
                r["Total Requested"] = str(int(r["Total Requested"]) + 1)
                found = True
                break

        if not found:
            rows.append({"ISBN": isbn, "Total Requested": "1"})

        self.repo.write_all(path, fieldnames, rows)
        
    def create_request(self, data: RequestCreate) -> RequestRead:
        """
        Create a new book request and save it to the requests.csv file.
        Steps:
        1. Check if the user already requested this ISBN using _already_requested().
           - If yes, raise an error so they can't request it twice.
        2. Generate a new unique RequestID.
        3. Create a Request object using the provided data.
        4. Append this request to the CSV file.
        5. Update the Total_Requested.csv file to increment this book's total requests.
        6. Return a RequestRead object so the API can send it back as a response.
        """
        if self._already_requested(data.user_id, data.isbn):
            raise ValueError("This user has already requested this book.")

        new_id = self._generate_next_id()
        request = Request(
            request_id=new_id,
            user_id=data.user_id,
            book_title=data.book_title,
            author=data.author,
            isbn=data.isbn,
        )

        self.repo.append_row(self.path, self.fields, request.to_csv_dict())
        self.__update_total_requested(data.isbn)

        return RequestRead(**request.to_api_dict())

    def delete_request(self, request_id: int) -> bool:
        """
        Delete a specific request and reindex the remaining IDs.

        Steps:
        1. Read all requests from the file.
        2. Filter out (remove) the row that matches the given RequestID.
        3. If nothing was removed, return False (meaning the ID didn't exist).
        4. Reassign new sequential RequestIDs (1, 2, 3, ...).
        5. Overwrite the file with the updated data.
        6. Return True if deletion was successful.
        """
        rows = self.repo.read_all(self.path)
        original_count = len(rows)
        
        # Remove the row matching the given ID
        updated_rows = [r for r in rows if int(r["RequestID"]) != request_id]

        if len(updated_rows) == original_count:
            return False

        # ✅ Reassign new sequential IDs
        for i, row in enumerate(updated_rows, start=1):
            row["RequestID"] = str(i)

        self.repo.write_all(self.path, self.fields, updated_rows)
        return True
