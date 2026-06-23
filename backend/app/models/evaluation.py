"""Evaluation SQLAlchemy model."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Evaluation(BaseModel):
    __tablename__ = "evaluations"

    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("answers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    evaluator_model: Mapped[str] = mapped_column(String(255), nullable=False)
    evaluation_version: Mapped[int] = mapped_column(Integer, default=1)

    # Scores (0-100)
    technical_accuracy: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    completeness: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    communication_quality: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    problem_solving_approach: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    confidence_level: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    overall_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    # Rubric
    rubric_version: Mapped[Optional[str]] = mapped_column(String(50))
    rubric_type: Mapped[Optional[str]] = mapped_column(String(50))

    # Feedback
    strengths: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    improvements: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    key_gaps_identified: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    feedback_summary: Mapped[Optional[str]] = mapped_column(Text)
    detailed_feedback: Mapped[Optional[str]] = mapped_column(Text)

    # LLM metadata
    evaluator_confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    llm_prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    llm_completion_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    llm_total_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    llm_cost_usd: Mapped[Optional[float]] = mapped_column(Numeric(10, 6))

    evaluated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    answer: Mapped["Answer"] = relationship("Answer", back_populates="evaluations")  # type: ignore[name-defined]
