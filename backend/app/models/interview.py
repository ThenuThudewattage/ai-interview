"""Interview and Question SQLAlchemy models."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Question(BaseModel):
    __tablename__ = "questions"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    skill_areas: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)

    difficulty_level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    estimated_time_minutes: Mapped[int] = mapped_column(Integer, default=45)

    expected_answer_summary: Mapped[Optional[str]] = mapped_column(Text)
    expected_answer_detailed: Mapped[Optional[str]] = mapped_column(Text)
    key_points: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    followup_hints: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    common_mistakes: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    source: Mapped[Optional[str]] = mapped_column(String(255))
    company_filters: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    frequency_count: Mapped[int] = mapped_column(Integer, default=1)

    version: Mapped[int] = mapped_column(Integer, default=1)
    is_latest: Mapped[bool] = mapped_column(default=True, index=True)

    # Relationships
    interview_questions: Mapped[List["InterviewQuestion"]] = relationship(
        "InterviewQuestion", back_populates="question"
    )


class Interview(BaseModel):
    __tablename__ = "interviews"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="in_progress", index=True)

    interview_type: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(50), default="medium")
    target_company: Mapped[Optional[str]] = mapped_column(String(255))
    target_role: Mapped[Optional[str]] = mapped_column(String(255))

    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    current_question_index: Mapped[int] = mapped_column(Integer, default=0)
    total_questions_planned: Mapped[int] = mapped_column(Integer, default=5)

    overall_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    technical_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    communication_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="interviews")  # type: ignore[name-defined]
    interview_questions: Mapped[List["InterviewQuestion"]] = relationship(
        "InterviewQuestion", back_populates="interview", cascade="all, delete-orphan"
    )


class InterviewQuestion(BaseModel):
    __tablename__ = "interview_questions"
    __table_args__ = (UniqueConstraint("interview_id", "question_index"),)

    interview_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    question_index: Mapped[int] = mapped_column(Integer, nullable=False)
    asked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_difficulty_adjusted: Mapped[Optional[str]] = mapped_column(String(50))
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    interview: Mapped["Interview"] = relationship("Interview", back_populates="interview_questions")
    question: Mapped["Question"] = relationship("Question", back_populates="interview_questions")
    answers: Mapped[List["Answer"]] = relationship(  # type: ignore[name-defined]
        "Answer", back_populates="interview_question", cascade="all, delete-orphan"
    )
