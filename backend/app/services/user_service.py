import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

from app.repositories.csv_repository import CSVRepository

USER_CSV = Path(__file__).resolve().parents[1] / "data" / "Users.csv"

FIELDNAMES = [
    "id",
    "username",
    "email",
    "password_hash",
    "is_admin",
    "is_suspended",
    "suspended_until",
    "suspension_reason",
    "warnings",
]


class CSVUserService:
    def __init__(self, repo: CSVRepository, path: str = USER_CSV):
        self.repo = repo
        self.path = path

    def _norm(self, s: str) -> str:
        return s.strip().lower()

    def _get_next_id(self) -> int:
        rows = self.repo.read_all(self.path)
        if not rows:
            return 1
        return max(int(r["id"]) for r in rows) + 1

    def _write_all(self, users: list[dict]) -> None:
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(users)

    def _check_suspension_expired(self, user: dict) -> dict:
        suspended_until = user.get("suspended_until", "")
        if not suspended_until:
            return user

        suspended_until_dt = datetime.fromisoformat(suspended_until)
        if datetime.now() >= suspended_until_dt:
            user["is_suspended"] = False
            user["suspended_until"] = ""
            user["suspension_reason"] = ""

            rows = self.repo.read_all(self.path)
            for r in rows:
                if int(r["id"]) == user["id"]:
                    r["is_suspended"] = "false"
                    r["suspended_until"] = ""
                    r["suspension_reason"] = ""
                    break

            self._write_all(rows)

        return user

    def _is_admin(self, user_id: int) -> bool:
        rows = self.repo.read_all(self.path)

        for r in rows:
            if int(r["id"]) == int(user_id):
                return str(r.get("is_admin", "False")).strip().lower() in {
                    "true",
                    "1",
                    "yes",
                }

        return False

    def get_by_username(self, username: str) -> Optional[Dict]:
        username_norm = self._norm(username)

        for row in self.repo.read_all(self.path):
            if self._norm(row["username"]) == username_norm:
                row["id"] = int(row["id"])
                row["is_admin"] = row["is_admin"].lower() == "true"
                row["is_suspended"] = row["is_suspended"].lower() == "true"
                row["warnings"] = int(row.get("warnings", "0") or 0)
                row["suspension_reason"] = row.get("suspension_reason") or None

                row = self._check_suspension_expired(row)
                return row

        return None

    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Return a single user by numeric id, or None if not found."""
        for row in self.repo.read_all(self.path):
            if int(row["id"]) == int(user_id):
                row["id"] = int(row["id"])
                row["is_admin"] = str(row.get("is_admin", "false")).lower() in {
                    "true",
                    "1",
                    "yes",
                }
                row["is_suspended"] = str(row.get("is_suspended", "false")).lower() in {
                    "true",
                    "1",
                    "yes",
                }
                row["warnings"] = int(row.get("warnings", "0") or 0)
                row["suspension_reason"] = row.get("suspension_reason") or None

                row = self._check_suspension_expired(row)
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
                raise ValueError("Username is taken")
            if self._norm(u["email"]) == email_norm:
                raise ValueError("Email is taken")

        new_id = self._get_next_id()

        user = {
            "id": new_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "is_admin": "true" if is_admin else "false",
            "is_suspended": "false",
            "suspended_until": "",
            "suspension_reason": "",
            "warnings": "0",
        }

        users.append(user)
        self._write_all(users)

        return {
            "id": int(user["id"]),
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "is_admin": is_admin,
            "is_suspended": False,
            "suspended_until": "",
            "suspension_reason": None,
            "warnings": 0,
        }

    def update_user(
        self,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        is_admin: bool | None = None,
    ) -> Dict:
        users = self.repo.read_all(self.path)
        updated_user = None

        for u in users:
            if int(u["id"]) == int(user_id):
                if username is not None:
                    username_clean = username.strip()
                    if username_clean:
                        new_norm = self._norm(username_clean)
                        for other in users:
                            if (
                                int(other["id"]) != int(user_id)
                                and self._norm(other["username"]) == new_norm
                            ):
                                raise ValueError("Username is taken")
                        u["username"] = username_clean

                if email is not None:
                    email_clean = email.strip()
                    if email_clean:
                        new_norm = self._norm(email_clean)
                        for other in users:
                            if (
                                int(other["id"]) != int(user_id)
                                and self._norm(other["email"]) == new_norm
                            ):
                                raise ValueError("Email is taken")
                        u["email"] = email_clean

                if is_admin is not None:
                    u["is_admin"] = "true" if is_admin else "false"

                updated_user = u
                break

        if updated_user is None:
            raise ValueError("User not found")

        self._write_all(users)

        updated_user["id"] = int(updated_user["id"])
        updated_user["is_admin"] = (
            str(updated_user.get("is_admin", "false")).lower() in {"true", "1", "yes"}
        )
        updated_user["is_suspended"] = (
            str(updated_user.get("is_suspended", "false")).lower() in {
                "true",
                "1",
                "yes",
            }
        )
        updated_user["warnings"] = int(updated_user.get("warnings", "0") or 0)
        updated_user["suspension_reason"] = (
            updated_user.get("suspension_reason") or None
        )

        return updated_user

    def suspend_user(
        self,
        admin_id: int,
        target_id: int,
        duration_minutes: int,
        reason: str | None = None,
    ) -> Dict:
        if not self._is_admin(admin_id):
            raise PermissionError("Admin privileges required")

        rows = self.repo.read_all(self.path)
        target = None

        suspended_until_dt = datetime.now() + timedelta(minutes=duration_minutes)
        suspended_until_str = suspended_until_dt.isoformat()

        for u in rows:
            if int(u["id"]) == int(target_id):
                u["is_suspended"] = "true"
                u["suspended_until"] = suspended_until_str
                u["suspension_reason"] = reason or ""
                target = u
                break

        if target is None:
            raise ValueError("User not found")

        self._write_all(rows)
        return target

    def unsuspend_user(self, admin_id: int, target_id: int) -> Dict:
        if not self._is_admin(admin_id):
            raise PermissionError("Admin privileges required")

        users = self.repo.read_all(self.path)
        unsuspended_user = None

        for u in users:
            if int(u["id"]) == int(target_id):
                u["is_suspended"] = "false"
                u["suspended_until"] = ""
                u["suspension_reason"] = ""
                unsuspended_user = u
                break

        if unsuspended_user is None:
            raise ValueError("user_not_found")

        self._write_all(users)
        return unsuspended_user

    def increment_warning(self, user_id: int) -> dict:
        users = self.repo.read_all(self.path)
        target = None

        for u in users:
            if int(u["id"]) == int(user_id):
                current = int(u.get("warnings", "0") or 0)
                current += 1
                u["warnings"] = str(current)
                target = u
                break

        if target is None:
            raise ValueError("User not found")

        self._write_all(users)
        return target

    def reset_warnings(self, user_id: int) -> dict:
        users = self.repo.read_all(self.path)
        target = None

        for u in users:
            if int(u["id"]) == int(user_id):
                u["warnings"] = "0"
                target = u
                break

        if target is None:
            raise ValueError("User not found")

        self._write_all(users)
        return target

    def auto_suspend_for_profanity(self, target_id: int, duration_minutes: int) -> dict:
        users = self.repo.read_all(self.path)
        target = None

        suspended_until_dt = datetime.now() + timedelta(minutes=duration_minutes)
        suspended_until_str = suspended_until_dt.isoformat()

        for u in users:
            if int(u["id"]) == int(target_id):
                u["is_suspended"] = "true"
                u["suspended_until"] = suspended_until_str
                u["suspension_reason"] = "Automatic suspension due to profanity"
                u["warnings"] = "0"
                target = u
                break

        if target is None:
            raise ValueError("User not found")

        self._write_all(users)
        return target
