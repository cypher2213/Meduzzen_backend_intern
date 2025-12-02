from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.company_user_role_model import RoleEnum


class CompanySchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    is_public: Optional[bool] = True

    model_config = {"from_attributes": True}


class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: Optional[bool] = True


class CompanyCreateResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_public: bool


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = True


class CompanyListSchema(BaseModel):
    List[CompanySchema]


class InviteSentSchema(BaseModel):
    company_id: UUID
    invited_user_id: UUID


class RequestSentSchema(BaseModel):
    company_id: UUID


class UserWithRoleSchema(BaseModel):
    id: UUID
    email: str
    name: str
    age: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    role: RoleEnum


class UsersWithRolesResponse(BaseModel):
    users: List[UserWithRoleSchema]


class Questions(BaseModel):
    title: str
    options: List[str]
    correct_answers: List[int]


class QuizCreate(BaseModel):
    title: str
    description: str
    questions: List[Questions]


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answers: Optional[List[int]] = None


class QuestionList(BaseModel):
    id: UUID
    title: str
    options: List[str]

    model_config = {"from_attributes": True}


class QuizzesList(BaseModel):
    id: UUID
    title: str
    description: str
    questions: List[QuestionList]

    model_config = {"from_attributes": True}


class QuestionCreateSchema(BaseModel):
    quiz_id: UUID
    title: str
    options: List[str]
    correct_answers: List[int]
