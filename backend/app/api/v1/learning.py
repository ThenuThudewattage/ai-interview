"""Learning plan API endpoints."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.middleware.auth import get_current_user
from app.api.schemas.learning import (
    GenerateLearningPlanRequest,
    LearningPlanResponse,
    MilestoneResponse,
    ResourceResponse,
    ResourceCompletionRequest,
)
from app.db.session import get_db
from app.models.user import User
from app.repositories.learning_plan_repository import LearningPlanRepository, LearningResourceRepository
from app.services.skill_service import SkillService
from app.agents.learning_agent import LearningAgent

router = APIRouter(prefix="/learning-plans", tags=["Learning"])


@router.post("/generate", status_code=201)
async def generate_learning_plan(
    request: GenerateLearningPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a personalized learning plan."""
    skill_svc = SkillService(db)
    user_skills = await skill_svc.get_user_skills_dict(current_user.id)
    skill_gaps = await skill_svc.get_user_gaps(current_user.id)

    gaps_data = [
        {
            "skill": g.skill_area.name if g.skill_area else "unknown",
            "gap_severity": float(g.gap_severity) if g.gap_severity else 0.5,
        }
        for g in skill_gaps
    ]

    # Use Learning Agent to generate plan
    agent = LearningAgent()
    plan_data = await agent.generate_full_plan(
        user_skills=user_skills,
        skill_gaps=gaps_data,
        target_proficiency=request.target_proficiency,
        available_hours_per_week=request.available_hours_per_week,
        interview_type=request.interview_type or "system_design",
    )

    plan_info = plan_data.get("learning_plan", {})

    # Save to DB
    from app.models.learning_plan import LearningPlan, LearningMilestone, LearningResource

    plan = LearningPlan(
        user_id=current_user.id,
        title=plan_info.get("title", "Personalized Learning Plan"),
        description=plan_info.get("description", ""),
        target_proficiency_score=request.target_proficiency,
        estimated_hours_total=plan_info.get("estimated_total_hours"),
        focus_skill_areas=[g.get("skill") for g in gaps_data[:5]],
    )
    db.add(plan)
    await db.flush()

    milestones_data = []
    for i, m in enumerate(plan_info.get("milestones", [])[:6]):
        milestone = LearningMilestone(
            learning_plan_id=plan.id,
            name=m.get("name", f"Milestone {i + 1}"),
            description=m.get("description", ""),
            sequence_number=i + 1,
            target_score=m.get("target_score"),
        )
        db.add(milestone)
        await db.flush()

        resources = []
        for r in m.get("resources", [])[:5]:
            resource = LearningResource(
                learning_milestone_id=milestone.id,
                title=r.get("title", "Resource"),
                description=r.get("description", ""),
                resource_type=r.get("type", "article"),
                url=r.get("url"),
                estimated_time_minutes=r.get("estimated_time_minutes"),
                proficiency_level=r.get("proficiency_level", "intermediate"),
                assigned_at=datetime.now(timezone.utc),
            )
            db.add(resource)
            resources.append(resource)

        milestones_data.append({
            "milestone": milestone,
            "resources": resources,
        })

    await db.flush()

    return {
        "learning_plan_id": str(plan.id),
        "user_id": str(current_user.id),
        "title": plan.title,
        "description": plan.description,
        "status": plan.status,
        "target_proficiency_score": float(plan.target_proficiency_score),
        "estimated_hours_total": plan.estimated_hours_total,
        "milestones": [
            {
                "milestone_id": str(m["milestone"].id),
                "name": m["milestone"].name,
                "sequence_number": m["milestone"].sequence_number,
                "status": m["milestone"].status,
                "resources": [
                    {
                        "resource_id": str(r.id),
                        "title": r.title,
                        "resource_type": r.resource_type,
                        "url": r.url,
                        "estimated_time_minutes": r.estimated_time_minutes,
                    }
                    for r in m["resources"]
                ],
            }
            for m in milestones_data
        ],
        "created_at": plan.created_at.isoformat(),
    }


@router.get("/{plan_id}")
async def get_learning_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get learning plan with progress."""
    repo = LearningPlanRepository(db)
    plan = await repo.get_with_milestones(plan_id)

    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    if str(plan.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "learning_plan_id": str(plan.id),
        "status": plan.status,
        "title": plan.title,
        "description": plan.description,
        "milestones": [
            {
                "milestone_id": str(m.id),
                "name": m.name,
                "status": m.status,
                "sequence_number": m.sequence_number,
                "resources": [
                    {
                        "resource_id": str(r.id),
                        "title": r.title,
                        "resource_type": r.resource_type,
                        "url": r.url,
                        "estimated_time_minutes": r.estimated_time_minutes,
                        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                    }
                    for r in m.resources
                ],
            }
            for m in plan.milestones
        ],
    }


@router.get("")
async def list_learning_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's learning plans."""
    repo = LearningPlanRepository(db)
    plans = await repo.get_user_plans(current_user.id)

    return {
        "total": len(plans),
        "plans": [
            {
                "learning_plan_id": str(p.id),
                "title": p.title,
                "status": p.status,
                "target_proficiency_score": float(p.target_proficiency_score),
                "created_at": p.created_at.isoformat(),
            }
            for p in plans
        ],
    }
