from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.uuid_mixin import UUIDMixin

if TYPE_CHECKING:
    from app.models.company_model import CompanyModel
    from app.models.user_model import UserModel


class CompanyUserRoleModel(Base, UUIDMixin):
    __tablename__ = "company_user_roles"
    user_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    company_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    role: Mapped[str] = mapped_column(String, default="member")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="roles")
    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel", back_populates="roles"
    )
