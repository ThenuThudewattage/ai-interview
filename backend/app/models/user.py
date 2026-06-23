"""User-related SQLAlchemy models."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    profile_picture_url: Mapped[Optional[str]] = mapped_column(Text)
    bio: Mapped[Optional[str]] = mapped_column(Text)

    # Preferences
    preferred_difficulty: Mapped[str] = mapped_column(String(50), default="medium")
    preferred_interview_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    language: Mapped[str] = mapped_column(String(50), default="en")

    # Account status
    account_status: Mapped[str] = mapped_column(String(50), default="active")
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        "UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    interviews: Mapped[List["Interview"]] = relationship(  # type: ignore[name-defined]
        "Interview", back_populates="user", cascade="all, delete-orphan"
    )
    user_skills: Mapped[List["UserSkill"]] = relationship(  # type: ignore[name-defined]
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    learning_plans: Mapped[List["LearningPlan"]] = relationship(  # type: ignore[name-defined]
        "LearningPlan", back_populates="user", cascade="all, delete-orphan"
    )
    skill_gaps: Mapped[List["SkillGap"]] = relationship(  # type: ignore[name-defined]
        "SkillGap", back_populates="user", cascade="all, delete-orphan"
    )


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    resume_url: Mapped[Optional[str]] = mapped_column(Text)
    resume_text: Mapped[Optional[str]] = mapped_column(Text)

    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer)
    current_job_title: Mapped[Optional[str]] = mapped_column(String(255))
    current_company: Mapped[Optional[str]] = mapped_column(String(255))

    target_position: Mapped[Optional[str]] = mapped_column(String(255))
    target_companies: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    top_skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    programming_languages: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserPreferences(BaseModel):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    preferred_skill_areas: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    preferred_question_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    preferred_companies: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    learning_pace: Mapped[str] = mapped_column(String(50), default="medium")

    email_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    interview_reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="preferences")
