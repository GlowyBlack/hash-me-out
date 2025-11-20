import csv
import os
from typing import Optional, Dict, List

USER_CSV = os.path.join(os.path.dirname(__file__), "users.csv")
FIELDNAMES = ["id", "username", "email", "password_hash"]


class CSVUserService:
    def __init__(self, path: str = USER_CSV):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()

    def _read_all(self) -> List[Dict[str, str]]:
        with open(self.path, "r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _write_all(self, rows: List[Dict[str, str]]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(tmp, self.path)

    def _norm(self, s: str) -> str:
        return s.strip().lower()

    def get_by_username(self, username: str) -> Optional[Dict]:
        username = self._norm(username)
        for row in self._read_all():
            if self._norm(row["username"]) == username:
                row["id"] = int(row["id"])
                return row
        return None

    def create_user(self, *, username: str, email: str, password_hash: str) -> Dict:
        rows = self._read_all()

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
        self._write_all(rows)

        rec["id"] = new_id
        return rec

    def update_user(
        self,
        user_id: int,
        *,
        username: str | None = None,
        email: str | None = None,
        password_hash: str | None = None,
    ) -> Dict:
        rows = self._read_all()

        # find target row
        target_idx = None
        for i, r in enumerate(rows):
            if int(r["id"]) == user_id:
                target_idx = i
                break

        if target_idx is None:
            raise ValueError("user_not_found")

        rec = rows[target_idx]

        # normalized new values (if provided)
        new_username = self._norm(username) if username is not None else None
        new_email = self._norm(email) if email is not None else None

        # uniqueness checks (ignoring this same user)
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

        # write back
        self._write_all(rows)

        return {
            "id": int(rec["id"]),
            "username": rec["username"],
            "email": rec["email"],
            "password_hash": rec["password_hash"],
        }
