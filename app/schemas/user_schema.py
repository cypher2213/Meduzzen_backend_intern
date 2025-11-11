from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSchema(BaseModel):
    id: UUID
    name: Optional[str]
    age: Optional[int] = Field(gt=0, le=120)
    email: EmailStr

    model_config = {"from_attributes": True}


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
    model_config = ConfigDict(extra="forbid")


class UsersListSchema(BaseModel):
    users: List[UserSchema]


class UserDetailsSchema(BaseModel):
    user_info: UserSchema


class LoginResponseSchema(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str


class RefreshResponseSchema(BaseModel):
    access_token: str
    token_type: str
