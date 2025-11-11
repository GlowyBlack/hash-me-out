import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "dev-only-change-me")
ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
ACCESS_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(*, username: str, user_id: int, minutes: int = ACCESS_MINUTES) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=minutes)
    payload = {
        "sub": username,
        "id": user_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
