import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.repositories.csv_repository import CSVRepository
from app.services.user_service import CSVUserService

#  Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bcrypt_context = pwd_context 

# JWT setup
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "change-me")
ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
ACCESS_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

def create_access_token(*, username: str, user_id: int, minutes: int = ACCESS_MINUTES) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=minutes)
    payload = {"sub": username, "id": user_id, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Repo + service singletons
_repo = CSVRepository()
_user_service = CSVUserService(_repo)

def get_user_service() -> CSVUserService:
    return _user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme),svc: CSVUserService = Depends(get_user_service),):
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        user_id = payload.get("id")
        if not username or user_id is None:
            raise ValueError("missing_claims")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")

    user = svc.get_by_username(username)
    if not user or int(user["id"]) != int(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found")
    return user
