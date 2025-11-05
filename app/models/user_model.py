from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixin_for_models import TimestampUUIDMixin


class UserModel(Base, TimestampUUIDMixin):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
