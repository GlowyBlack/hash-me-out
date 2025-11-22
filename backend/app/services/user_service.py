import csv
import os
from typing import Optional, Dict
from app.repositories.csv_repository import CSVRepository

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

USER_CSV = os.path.join(DATA_DIR, "Users.csv")
FIELDNAMES = ["id", "username", "email", "password_hash", "is_admin"]

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
    
    def _convert_row(self, row: dict) -> dict:
        r = dict(row)
        r["id"] = int(r["id"])

        raw_flag = r.get("is_admin", "False")

    def _get_next_id(self) -> int:
        rows = self.repo.read_all(self.path)
        if not rows:
            return 1
        return max(int(r["id"]) for r in rows) + 1

    def get_by_username(self, username: str) -> Optional[Dict]:
        username_norm = self._norm(username)

        for row in self.repo.read_all(self.path):
            if self._norm(row["username"]) == username_norm:
                row["id"] = int(row["id"])
                if "is_admin" in row:
                    val = str(row["is_admin"]).strip().lower()
                    row["is_admin"] = val in {"true", "1", "yes"}
                return row
        return None

    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        is_admin: bool = False,
    ) -> Dict:
        users = self.repo.read_all(self.path)

        username_norm = self._norm(username)
        email_norm = self._norm(email)

        for u in users:
            if self._norm(u["username"]) == username_norm:
                raise ValueError("username_taken")
            if self._norm(u["email"]) == email_norm:
                raise ValueError("email_taken")

        new_id = self._get_next_id()

        user = {
            "id": new_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "is_admin": is_admin,
        }

        users.append(user)

        with open(self.path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(users)

        return user

    def update_user(
        self,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        is_admin: bool | None = None,
    ) -> Dict:
        users = self.repo.read_all(self.path)

        updated_user: Optional[Dict] = None
        user_id_int = int(user_id)

        for u in users:
            if int(u["id"]) == user_id_int:

                if username is not None:
                    new_username_norm = self._norm(username)
                    for other in users:
                        if int(other["id"]) != user_id_int and self._norm(other["username"]) == new_username_norm:
                            raise ValueError("username_taken")
                    u["username"] = username

                if email is not None:
                    new_email_norm = self._norm(email)
                    for other in users:
                        if int(other["id"]) != user_id_int and self._norm(other["email"]) == new_email_norm:
                            raise ValueError("email_taken")
                    u["email"] = email

                if is_admin is not None:
                    u["is_admin"] = is_admin

                updated_user = u
                break

        if updated_user is None:
            raise ValueError("user_not_found")

        with open(self.path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(users)

        updated_user["id"] = int(updated_user["id"])

        return updated_user
