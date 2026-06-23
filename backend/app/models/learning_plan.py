"""Learning plan SQLAlchemy models."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class LearningPlan(BaseModel):
    __tablename__ = "learning_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)

    target_proficiency_score: Mapped[float] = mapped_column(Numeric(5, 2), default=80.0)
    target_completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    estimated_hours_total: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_hours_spent: Mapped[int] = mapped_column(Integer, default=0)

    focus_skill_areas: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_plans")  # type: ignore[name-defined]
    milestones: Mapped[List["LearningMilestone"]] = relationship(
        "LearningMilestone", back_populates="learning_plan", cascade="all, delete-orphan",
        order_by="LearningMilestone.sequence_number"
    )


class LearningMilestone(BaseModel):
    __tablename__ = "learning_milestones"

    learning_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    sequence_number: Mapped[Optional[int]] = mapped_column(Integer)

    target_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    status: Mapped[str] = mapped_column(String(50), default="pending")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    learning_plan: Mapped["LearningPlan"] = relationship("LearningPlan", back_populates="milestones")
    resources: Mapped[List["LearningResource"]] = relationship(
        "LearningResource", back_populates="milestone", cascade="all, delete-orphan"
    )


class LearningResource(BaseModel):
    __tablename__ = "learning_resources"

    learning_milestone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_milestones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))
    url: Mapped[Optional[str]] = mapped_column(Text)

    source: Mapped[Optional[str]] = mapped_column(String(255))
    estimated_time_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    proficiency_level: Mapped[Optional[str]] = mapped_column(String(50))

    rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    relevance_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))

    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    milestone: Mapped["LearningMilestone"] = relationship(
        "LearningMilestone", back_populates="resources"
    )
