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

    def get_all_users(self) -> List[Dict]:
        rows = self.repo.read_all(self.path)
        for r in rows:
            r["id"] = int(r["id"])
        return rows

    def delete_user(self, user_id: int) -> bool:
        rows = self.repo.read_all(self.path)
        filtered = [r for r in rows if int(r["id"]) != user_id]

        if len(filtered) == len(rows):
            return False

        self.repo.write_all(self.path, FIELDNAMES, filtered)
        return True

    def update_user(
        self,
        user_id: int,
        *,
        username: str | None = None,
        email: str | None = None,
        password_hash: str | None = None,
    ) -> Dict:
        rows = self.repo.read_all(self.path)



        target_idx = None
        for i, r in enumerate(rows):
            if int(r["id"]) == user_id:
                target_idx = i
                break

        if target_idx is None:
            raise ValueError("user_not_found")

        rec = rows[target_idx]

        # normalize new values
        new_username = self._norm(username) if username is not None else None
        new_email = self._norm(email) if email is not None else None

        # uniqueness checks (excluding this user)
        if new_username is not None:
            for r in rows:
                if int(r["id"]) != user_id and self._norm(r["username"]) == new_username:
                    raise ValueError("username_taken")

        if new_email is not None:
            for r in rows:
                if int(r["id"]) != user_id and self._norm(r["email"]) == new_email:
                    raise ValueError("email_taken")

        # apply updates
        if new_username is not None:
            rec["username"] = new_username
        if new_email is not None:
            rec["email"] = new_email
        if password_hash is not None:
            rec["password_hash"] = password_hash

        # write back to disk
        self.repo.write_all(self.path, FIELDNAMES, rows)

        # return updated record with id as int
        return {
            "id": int(rec["id"]),
            "username": rec["username"],
            "email": rec["email"],
            "password_hash": rec["password_hash"],
        }
