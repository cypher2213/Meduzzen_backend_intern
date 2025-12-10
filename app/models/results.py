from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.timestamp_mixin import TimestampMixin
from app.models.uuid_mixin import UUIDMixin

if TYPE_CHECKING:
    from app.models.user_model import UserModel
    from app.models.quiz_model import QuizModel
    from app.models.quiz_answer_model import QuizAnswer

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class QuizResults(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "results"
    user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    quiz_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=True
    )
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[user_id])
    quiz: Mapped["QuizModel"] = relationship("QuizModel", foreign_keys=[quiz_id])
    answers: Mapped[list["QuizAnswer"]] = relationship(
        "QuizAnswer", back_populates="quiz_result", cascade="all, delete-orphan"
    )
