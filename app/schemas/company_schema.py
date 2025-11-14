from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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

    model_config = {"from_attributes": True}
