from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.timestamp_mixin import TimestampMixin
from app.models.uuid_mixin import UUIDMixin


class UserModel(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
