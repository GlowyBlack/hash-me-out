import csv
import os
from typing import Optional, Dict, List

from app.utils.data_manager import CSVRepository

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

USER_CSV = os.path.join(DATA_DIR, "Users.csv")
FIELDNAMES = ["id", "username", "email", "password_hash"]


class CSVUserService:
    def __init__(self, repo: CSVRepository, path: str = USER_CSV):
        self.repo = repo
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()

    def _norm(self, s: str) -> str:
        return s.strip().lower()

    def get_by_username(self, username: str) -> Optional[Dict]:
        username_norm = self._norm(username)
        for row in self.repo.read_all(self.path):
            if self._norm(row["username"]) == username_norm:
                row["id"] = int(row["id"])
                return row
        return None

    def create_user(self, *, username: str, email: str, password_hash: str) -> Dict:
        rows = self.repo.read_all(self.path)

        username_norm = self._norm(username)
        email_norm = self._norm(email)

        if any(self._norm(r["username"]) == username_norm for r in rows):
            raise ValueError("username_taken")
        if any(self._norm(r["email"]) == email_norm for r in rows):
            raise ValueError("email_taken")

        new_id = 1 if not rows else max(int(r["id"]) for r in rows) + 1
        rec = {
            "id": str(new_id),
            "username": username_norm,
            "email": email_norm,
            "password_hash": password_hash,
        }
        rows.append(rec)
        self.repo.write_all(self.path, FIELDNAMES, rows)

        rec["id"] = new_id
        return rec
