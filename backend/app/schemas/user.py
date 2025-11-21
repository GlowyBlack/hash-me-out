from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    #role: str = Field(default="user", pattern="^(user|admin)$")

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    #role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str | None = None
    id: int | None = None
    #role: str | None = None
    exp: int | None = None
