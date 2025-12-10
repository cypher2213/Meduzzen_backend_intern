from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.results import QuizResults
    from app.models.question_model import QuestionModel

from app.models.base import Base
from app.models.timestamp_mixin import TimestampMixin
from app.models.uuid_mixin import UUIDMixin


class QuizAnswer(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "quiz_answers"

    quiz_result_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("results.id"), nullable=False
    )
    question_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False
    )
    selected_answers: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)

    quiz_result: Mapped["QuizResults"] = relationship(
        "QuizResults", back_populates="answers"
    )
    question: Mapped["QuestionModel"] = relationship(
        "QuestionModel", back_populates="quiz_answers"
    )
