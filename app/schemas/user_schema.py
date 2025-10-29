from typing import List

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    id: int
    name: str
    password: str = Field(min_length=6)
    age: int = Field(gt=0, le=120)
    email: EmailStr


class SignInSchema(BaseModel):
    email: EmailStr
    password: str


class SignUpSchema(UserSchema):
    pass


class UserUpdateSchema(BaseModel):
    name: str
    password: str = Field(min_length=6)
    email: EmailStr


class UsersListSchema(BaseModel):
    users: List[UserSchema]


class UserDetailsSchema(BaseModel):
    user_info: UserSchema
