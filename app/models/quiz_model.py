from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.question_model import QuestionModel
    from app.models.company_model import CompanyModel
    from app.models.results import QuizResults

from uuid import UUID

from sqlalchemy import ForeignKey

from app.models.uuid_mixin import UUIDMixin


class QuizModel(Base, UUIDMixin):
    __tablename__ = "quizzes"
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    total_participation: Mapped[int] = mapped_column(Integer, default=0)
    questions: Mapped[List["QuestionModel"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    company: Mapped["CompanyModel"] = relationship(back_populates="quizzes")
    quiz_results: Mapped[List["QuizResults"]] = relationship(
        "QuizResults", back_populates="quiz", cascade="all, delete-orphan"
    )
