from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    id: UUID
    name: str
    age: int = Field(gt=0, le=120)
    email: EmailStr

    class Config:
        orm_mode = True


class SignInSchema(BaseModel):
    email: EmailStr
    password: str


class SignUpSchema(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    age: int = Field(gt=0, le=120)


class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class UsersListSchema(BaseModel):
    users: List[UserSchema]


class UserDetailsSchema(BaseModel):
    user_info: UserSchema
