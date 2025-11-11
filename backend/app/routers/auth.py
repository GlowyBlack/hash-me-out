from app.deps import pwd_context, create_access_token, decode_token
from app.services.user_service import CSVUserService
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from pydantic import BaseModel, EmailStr

from app.deps import pwd_context, create_access_token, decode_token
from app.services.user_service import CSVUserService


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


svc = CSVUserService()


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        data = decode_token(token)
        username: Optional[str] = data.get("sub")
        user = svc.get_by_username(username) if username else None
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token subject")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate):
    try:
        pw_hash = pwd_context.hash(data.password)
        user = svc.create_user(
            username=data.username,
            email=str(data.email),
            password_hash=pw_hash,
        )
        return UserOut(id=user["id"], username=user["username"], email=user["email"])
    except ValueError as e:
        if str(e) == "username_taken":
            raise HTTPException(status_code=400, detail="Username already exists")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"user_create_failed: {e}")

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = svc.get_by_username(form.username)
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(username=user["username"], user_id=user["id"])
    return Token(access_token=token)

@router.get("/me", response_model=UserOut)
def me(curr: Dict = Depends(get_current_user)):
    return UserOut(id=curr["id"], username=curr["username"], email=curr["email"])
