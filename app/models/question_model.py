from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.uuid_mixin import UUIDMixin

if TYPE_CHECKING:
    from app.models.quiz_model import QuizModel


class QuestionModel(Base, UUIDMixin):
    __tablename__ = "questions"
    title: Mapped[str] = mapped_column(String, nullable=False)
    options: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    correct_answers: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    quiz_id: Mapped[str] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
    )

    quiz: Mapped["QuizModel"] = relationship(back_populates="questions")
