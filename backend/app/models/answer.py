"""Answer SQLAlchemy model."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Answer(BaseModel):
    __tablename__ = "answers"

    interview_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_language: Mapped[Optional[str]] = mapped_column(String(50))
    answer_code: Mapped[Optional[str]] = mapped_column(Text)

    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    character_count: Mapped[Optional[int]] = mapped_column(Integer)
    word_count: Mapped[Optional[int]] = mapped_column(Integer)

    is_followup_answer: Mapped[bool] = mapped_column(Boolean, default=False)
    followup_question_index: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    interview_question: Mapped["InterviewQuestion"] = relationship(  # type: ignore[name-defined]
        "InterviewQuestion", back_populates="answers"
    )
    evaluations: Mapped[List["Evaluation"]] = relationship(  # type: ignore[name-defined]
        "Evaluation", back_populates="answer", cascade="all, delete-orphan"
    )
