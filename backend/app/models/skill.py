"""Skill-related SQLAlchemy models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class SkillArea(BaseModel):
    __tablename__ = "skill_areas"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    parent_skill_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill_areas.id"), nullable=True
    )

    # Relationships
    user_skills: Mapped[list["UserSkill"]] = relationship("UserSkill", back_populates="skill_area")
    skill_gaps: Mapped[list["SkillGap"]] = relationship("SkillGap", back_populates="skill_area")


class UserSkill(BaseModel):
    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_area_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill_areas.id", ondelete="CASCADE"), nullable=False
    )

    proficiency_score: Mapped[float] = mapped_column(Numeric(5, 2), default=50.0)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), default=50.0)

    assessment_count: Mapped[int] = mapped_column(Integer, default=0)
    last_assessment_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    score_trend: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    velocity: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_skills")  # type: ignore[name-defined]
    skill_area: Mapped["SkillArea"] = relationship("SkillArea", back_populates="user_skills")
    assessment_history: Mapped[list["SkillAssessmentHistory"]] = relationship(
        "SkillAssessmentHistory", back_populates="user_skill", cascade="all, delete-orphan"
    )


class SkillAssessmentHistory(BaseModel):
    __tablename__ = "skill_assessment_history"

    user_skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    proficiency_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    assessment_source: Mapped[Optional[str]] = mapped_column(String(100))
    related_interview_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=True
    )

    user_skill: Mapped["UserSkill"] = relationship("UserSkill", back_populates="assessment_history")


class SkillGap(BaseModel):
    __tablename__ = "skill_gaps"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill_areas.id", ondelete="CASCADE"), nullable=False
    )

    gap_severity: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    related_interview_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=True
    )
    identified_by_agent: Mapped[Optional[str]] = mapped_column(String(100))

    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    identified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="skill_gaps")  # type: ignore[name-defined]
    skill_area: Mapped["SkillArea"] = relationship("SkillArea", back_populates="skill_gaps")
