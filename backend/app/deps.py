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
    username: str,
    user_id: int,
    is_admin: bool,
    minutes: int = ACCESS_MINUTES,
) -> str:
    """
    Create a JWT access token for the given user.

    The token payload includes the user's id as "sub", username, admin flag,
    issued-at time (iat), and expiration time (exp).
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=minutes)

    payload = {
        "sub": str(user_id),
        "username": username,
        "is_admin": is_admin,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """
    Decode a JWT and return its payload. Raise an HTTP 401 if invalid.
    """
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
    """
    Retrieve the current authenticated user from the JWT token.

    The username is extracted from the token and used to look up the user. This avoids
    issues where numeric IDs may not match string IDs in the CSV repository.
    """
    try:
        payload = decode_token(token)
        username = payload.get("username")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid_token",
            )
        user = svc.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_not_found",
            )
        return user
    except HTTPException:
        # Re-raise specific HTTP errors
        raise
    except Exception:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        )