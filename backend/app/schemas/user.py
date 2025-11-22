from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool 

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str | None = None
    id: int | None = None
    is_admin: bool | None = None   
    exp: int | None = None
