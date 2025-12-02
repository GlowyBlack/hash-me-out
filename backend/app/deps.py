import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.repositories.csv_repository import CSVRepository
from app.services.user_service import CSVUserService
from app.services.review_service import ReviewService

#  Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bcrypt_context = pwd_context 

# JWT setup
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "change-me")
ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
ACCESS_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

def create_access_token(
    *,
    username: str,  # still passed in, but we do not need to store it
    user_id: int,
    is_admin: bool,
    minutes: int = ACCESS_MINUTES,
) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=minutes)

    payload = {
        "sub": str(user_id),           # use id as subject
        "username": username,
        "is_admin": is_admin,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    # optional: keep "id" for backwards compatibility if you want
    # payload["id"] = user_id

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_user_service() -> CSVUserService:
    return CSVUserService(CSVRepository())

def get_review_service() -> ReviewService:
    return ReviewService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    svc: CSVUserService = Depends(get_user_service),
):
    try:
        payload = decode_token(token)

        # New tokens store user id in "sub".
        # If you keep "id" in the payload, fall back to it for old tokens.
        raw_id = payload.get("sub") or payload.get("id")
        if raw_id is None:
            raise ValueError("missing_id")

        user_id = int(raw_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        )

    user = svc.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_not_found",
        )
    return user
