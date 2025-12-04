from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.utils.validators import validate_email


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def valid_email(cls, v: str) -> str:
        return validate_email(v)


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool

    is_suspended: bool | None = None
    suspended_until: Optional[str] = None
    suspension_reason: Optional[str] = None
    warnings: int | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
    id: Optional[int] = None
    is_admin: Optional[bool] = None
    exp: Optional[int] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
