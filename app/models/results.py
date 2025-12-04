from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.models.base import Base
from app.models.timestamp_mixin import TimestampMixin
from app.models.uuid_mixin import UUIDMixin

if TYPE_CHECKING:
    from app.models.company_model import CompanyModel
    from app.models.user_model import UserModel
    from app.models.quiz_model import QuizModel
    from app.models.question_model import QuestionModel

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class QuizResults(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "results"
    user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    company_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )

    quiz_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=True
    )

    question_id: Mapped[UUID] = mapped_column(ForeignKey("questions.id"))

    is_done: Mapped[bool] = mapped_column(Boolean, default=False)

    selected_answers: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)

    user: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[user_id])
    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel", foreign_keys=[company_id]
    )
    quiz: Mapped["QuizModel"] = relationship("QuizModel", foreign_keys=[quiz_id])
    question: Mapped["QuestionModel"] = relationship(
        "QuestionModel", foreign_keys=[question_id], back_populates="quiz_results"
    )
