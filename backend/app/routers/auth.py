from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.services.user_service import CSVUserService
from app.deps import get_user_service, pwd_context, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

@router.post("/register", response_model=UserOut)
def register(payload: UserCreateRequest, svc: CSVUserService = Depends(get_user_service)):
    try:
        user = svc.create_user(
            username=payload.username,
            email=payload.email,
            password_hash=pwd_context.hash(payload.password),
        )
        return UserOut(id=user["id"], username=user["username"], email=user["email"])
    except ValueError as e:
        msg = str(e)
        if msg in {"username_taken", "email_taken"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        raise

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), svc: CSVUserService = Depends(get_user_service)):
    user = svc.get_by_username(form.username)
    if not user or not pwd_context.verify(form.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")

    token = create_access_token(username=user["username"], user_id=user["id"], minutes=60)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(curr=Depends(get_current_user)):
    return UserOut(id=curr["id"], username=curr["username"], email=curr["email"])
