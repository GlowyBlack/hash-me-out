from datetime import datetime

class User:
    def __init__(self, user_id: int, username: str, email: str,
                hashed_password: str, time: str | None = None,
                is_admin: bool = False, is_suspended: bool = False,
                suspended_until: str | None = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.time = time or datetime.now().isoformat()
        self.is_admin = is_admin
        self.is_suspended = is_suspended
        self.suspended_until = suspended_until
        

    def to_api_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "time": self.time,
            "is_admin": self.is_admin,
            "is_suspended": self.is_suspended,
        }


    def to_csv_dict(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.hashed_password,
            "is_admin": "true" if self.is_admin else "false",
            "is_suspended": "true" if self.is_suspended else "false",
            "suspended_until": self.suspended_until or "",
        }


    @classmethod
    def from_dict(cls, row):
        return cls(
            user_id=int(row["id"]),
            username=row["username"],
            email=row["email"],
            hashed_password=row["password_hash"],
            time=row.get("time"),
            is_admin=row["is_admin"].lower() == "true",
            is_suspended=row["is_suspended"].lower() == "true",
            suspended_until=row.get("suspended_until", ""),
        )