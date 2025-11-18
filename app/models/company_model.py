from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.timestamp_mixin import TimestampMixin
from app.models.uuid_mixin import UUIDMixin

if TYPE_CHECKING:
    from app.models.company_user_role_model import CompanyUserRoleModel


class CompanyModel(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "companies"
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False)
    roles: Mapped[List["CompanyUserRoleModel"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
