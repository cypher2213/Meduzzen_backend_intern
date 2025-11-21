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
