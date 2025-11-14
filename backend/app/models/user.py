from datetime import datetime

class User:
    #todo: add roles into user schema
    def __init__(self, user_id: int, username: str, email: str,
                 hashed_password: str, time: str | None = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.time = time or datetime.now().isoformat()

    def to_api_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "time": self.time,
        }

    def to_csv_dict(self) -> dict:
        return {
            "UserID": self.user_id,
            "Username": self.username,
            "Email": self.email,
            "HashedPassword": self.hashed_password,
            "Time": self.time,
        }

    @classmethod
    def from_dict(cls, row: dict):
        return cls(
            user_id=int(row["UserID"]),
            username=row["Username"],
            email=row["Email"],
            hashed_password=row["HashedPassword"],
            time=row.get("Time"),
        )
