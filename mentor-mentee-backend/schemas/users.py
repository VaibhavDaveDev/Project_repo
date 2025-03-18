from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum as PyEnum

class RoleEnum(str, PyEnum):
    super_admin = "super_admin"
    admin = "admin"
    mentor = "mentor"
    mentee = "mentee"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.mentee
    profile_picture: Optional[str] = None
    bio: Optional[str] = None

class User(BaseModel):
    user_id: int
    username: str
    email: str
    role: RoleEnum
    is_active: bool
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    google_id: Optional[str] = None
    github_id: Optional[str] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
