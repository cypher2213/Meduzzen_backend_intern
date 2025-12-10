from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.company_user_role_model import CompanyUserRoleModel
    from app.models.results import QuizResults

from app.models.base import Base
from app.models.timestamp_mixin import TimestampMixin
from app.models.uuid_mixin import UUIDMixin


class UserModel(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    roles: Mapped[List["CompanyUserRoleModel"]] = relationship(
        "CompanyUserRoleModel", back_populates="user", cascade="all, delete-orphan"
    )
    quiz_results: Mapped[List["QuizResults"]] = relationship(
        "QuizResults", back_populates="user", cascade="all, delete-orphan"
    )
