import csv
import os
from typing import Optional, Dict, List

from app.utils.data_manager import CSVRepository

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

        if isinstance(raw_flag, bool):
            r["is_admin"] = raw_flag
        else:
            r["is_admin"] = (raw_flag == "True")

        return r

    def get_by_username(self, username: str) -> Optional[Dict]:
        username_norm = self._norm(username)

        for row in self.repo.read_all(self.path):
            if self._norm(row["username"]) == username_norm:
                return self._convert_row(row)

        return None

    def create_user(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
        is_admin: bool = False,
    ) -> Dict:
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
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "is_admin": "True" if is_admin else "False",
        }

        rows.append(rec)
        self.repo.write_all(self.path, FIELDNAMES, rows)

        rec["id"] = new_id
        rec["is_admin"] = is_admin
        return self._convert_row(rec)

    def get_all_users(self) -> List[Dict]:
        rows = self.repo.read_all(self.path)
        return [self._convert_row(r) for r in rows]

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
        is_admin: bool | None = None,
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

        new_username_norm = self._norm(username) if username is not None else None
        new_email_norm = self._norm(email) if email is not None else None

        if new_username_norm is not None:
            for r in rows:
                if int(r["id"]) != user_id and self._norm(r["username"]) == new_username_norm:
                    raise ValueError("username_taken")

        if new_email_norm is not None:
            for r in rows:
                if int(r["id"]) != user_id and self._norm(r["email"]) == new_email_norm:
                    raise ValueError("email_taken")

        if username is not None:
            rec["username"] = username
        if email is not None:
            rec["email"] = email
        if password_hash is not None:
            rec["password_hash"] = password_hash
        if is_admin is not None:
            rec["is_admin"] = "True" if is_admin else "False"

        self.repo.write_all(self.path, FIELDNAMES, rows)

        return self._convert_row(rec)

    def set_admin(self, user_id: int, is_admin: bool) -> Dict:
        return self.update_user(user_id, is_admin=is_admin)
