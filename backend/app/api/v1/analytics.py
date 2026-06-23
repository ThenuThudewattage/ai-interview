"""Analytics API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.middleware.auth import get_current_user
from app.db.session import get_db
from app.models.interview import Interview
from app.models.user import User
from app.services.skill_service import SkillService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user dashboard analytics."""
    # Get interview stats
    result = await db.execute(
        select(
            func.count(Interview.id).label("total"),
            func.count(Interview.id).filter(Interview.status == "completed").label("completed"),
            func.avg(Interview.overall_score).filter(Interview.status == "completed").label("avg_score"),
        ).where(Interview.user_id == current_user.id)
    )
    stats = result.one()

    # Get skills
    skill_svc = SkillService(db)
    skills = await skill_svc.get_user_skills(current_user.id)
    gaps = await skill_svc.get_user_gaps(current_user.id)

    # Recent interviews
    from app.repositories.interview_repository import InterviewRepository
    repo = InterviewRepository(db)
    recent = await repo.get_user_interviews(current_user.id, limit=5)

    return {
        "user_id": str(current_user.id),
        "interview_stats": {
            "total_interviews": stats.total or 0,
            "completed_interviews": stats.completed or 0,
            "completion_rate": round((stats.completed or 0) / max(stats.total or 1, 1) * 100, 1),
            "average_score": round(float(stats.avg_score or 0), 2),
        },
        "skill_overview": {
            "total_skills_tracked": len(skills),
            "skills_above_70": len([s for s in skills if float(s.proficiency_score) >= 70]),
            "skills_needing_work": len([s for s in skills if float(s.proficiency_score) < 50]),
            "active_skill_gaps": len(gaps),
        },
        "skill_breakdown": [
            {
                "skill": s.skill_area.name if s.skill_area else "unknown",
                "category": s.skill_area.category if s.skill_area else None,
                "proficiency": float(s.proficiency_score),
                "confidence": float(s.confidence_score),
            }
            for s in skills[:10]
        ],
        "recent_interviews": [
            {
                "interview_id": str(i.id),
                "interview_type": i.interview_type,
                "difficulty_level": i.difficulty_level,
                "status": i.status,
                "overall_score": float(i.overall_score) if i.overall_score else None,
                "started_at": i.started_at.isoformat() if i.started_at else None,
            }
            for i in recent
        ],
    }
