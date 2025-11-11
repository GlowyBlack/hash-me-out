import os
import csv
from typing import Optional, Dict, List


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True) 

USER_CSV = os.path.join(DATA_DIR, "Users.csv")
FIELDNAMES = ["id", "username", "email", "password_hash"]

print("USERS CSV PATH:", USER_CSV)

class CSVUserService:
    def __init__(self, path: str = USER_CSV):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader()

    def _read_all(self) -> List[Dict[str, str]]:
        with open(self.path, "r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _write_all(self, rows: List[Dict[str, str]]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, self.path)

    def get_by_username(self, username: str) -> Optional[Dict]:
        for row in self._read_all():
            if row["username"] == username:
                row["id"] = int(row["id"])
                return row
        return None

    def create_user(self, *, username: str, email: str, password_hash: str) -> Dict:
        rows = self._read_all()
        if any(r["username"] == username for r in rows):
            raise ValueError("username_taken")
        new_id = 1 if not rows else max(int(r["id"]) for r in rows) + 1
        rec = {
            "id": str(new_id),
            "username": username,
            "email": email,
            "password_hash": password_hash
        }
        rows.append(rec)
        self._write_all(rows)
        rec["id"] = new_id
        return rec
