from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSchema(BaseModel):
    id: int
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
    model_config = ConfigDict(extra="forbid")


class UsersListSchema(BaseModel):
    users: List[UserSchema]


class UserDetailsSchema(BaseModel):
    user_info: UserSchema
