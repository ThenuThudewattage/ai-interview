"""User management API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.middleware.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserProfileRepository, UserPreferencesRepository
from app.services.skill_service import SkillService

router = APIRouter(prefix="/users", tags=["Users"])


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    preferred_difficulty: Optional[str] = None
    timezone: Optional[str] = None


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's profile."""
    skill_svc = SkillService(db)
    skills = await skill_svc.get_user_skills(current_user.id)
    avg_score = sum(float(s.proficiency_score) for s in skills) / len(skills) if skills else 0

    top_skills = sorted(skills, key=lambda s: s.proficiency_score, reverse=True)[:3]

    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "bio": current_user.bio,
        "preferences": {
            "preferred_difficulty": current_user.preferred_difficulty,
            "preferred_interview_duration_minutes": current_user.preferred_interview_duration_minutes,
            "timezone": current_user.timezone,
            "language": current_user.language,
        },
        "skills_summary": {
            "total_skills": len(skills),
            "average_proficiency": round(avg_score, 1),
            "top_skills": [s.skill_area.name for s in top_skills if s.skill_area],
        },
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat(),
    }


@router.put("/profile")
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile."""
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)

    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    await repo.update(current_user, **update_data)

    updated_fields = list(update_data.keys())
    return {
        "user_id": str(current_user.id),
        "updated_fields": updated_fields,
        "updated_at": current_user.updated_at.isoformat(),
    }


@router.get("/skills")
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's skill proficiency levels."""
    skill_svc = SkillService(db)
    skills = await skill_svc.get_user_skills(current_user.id)

    return {
        "user_id": str(current_user.id),
        "skills": [
            {
                "skill_id": str(s.id),
                "skill_name": s.skill_area.name if s.skill_area else "unknown",
                "category": s.skill_area.category if s.skill_area else None,
                "proficiency_score": float(s.proficiency_score),
                "confidence_score": float(s.confidence_score),
                "assessment_count": s.assessment_count,
                "last_assessment_date": s.last_assessment_date.isoformat() if s.last_assessment_date else None,
            }
            for s in skills
        ],
    }


@router.get("/skill-gaps")
async def get_skill_gaps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's identified skill gaps."""
    skill_svc = SkillService(db)
    gaps = await skill_svc.get_user_gaps(current_user.id)

    return {
        "total_gaps": len(gaps),
        "skill_gaps": [
            {
                "gap_id": str(g.id),
                "skill": g.skill_area.name if g.skill_area else "unknown",
                "gap_severity": float(g.gap_severity) if g.gap_severity else 0,
                "is_resolved": g.is_resolved,
                "identified_at": g.identified_at.isoformat() if g.identified_at else None,
            }
            for g in gaps
        ],
    }
