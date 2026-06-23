"""Skill service."""
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import UserSkill, SkillGap
from app.repositories.skill_repository import SkillAreaRepository, UserSkillRepository, SkillGapRepository


class SkillService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.skill_area_repo = SkillAreaRepository(session)
        self.user_skill_repo = UserSkillRepository(session)
        self.skill_gap_repo = SkillGapRepository(session)

    async def get_user_skills(self, user_id: uuid.UUID) -> List[UserSkill]:
        return await self.user_skill_repo.get_user_skills(user_id)

    async def get_user_skills_dict(self, user_id: uuid.UUID) -> Dict[str, float]:
        """Return {skill_name: proficiency_score} dict."""
        skills = await self.user_skill_repo.get_user_skills(user_id)
        return {s.skill_area.name: float(s.proficiency_score) for s in skills}

    async def update_skill_from_interview(
        self,
        user_id: uuid.UUID,
        skill_name: str,
        interview_score: float,
    ) -> None:
        """Update skill proficiency based on interview performance."""
        skill_area = await self.skill_area_repo.get_by_name(skill_name)
        if not skill_area:
            return

        user_skill = await self.user_skill_repo.get_user_skill(user_id, skill_area.id)
        if user_skill:
            # Weighted moving average
            current = float(user_skill.proficiency_score)
            new_score = current * 0.7 + interview_score * 0.3
            await self.user_skill_repo.update(
                user_skill,
                proficiency_score=new_score,
                assessment_count=user_skill.assessment_count + 1,
                last_assessment_date=datetime.now(timezone.utc),
            )
        else:
            await self.user_skill_repo.create(
                user_id=user_id,
                skill_area_id=skill_area.id,
                proficiency_score=interview_score,
                assessment_count=1,
                last_assessment_date=datetime.now(timezone.utc),
            )

    async def record_skill_gap(
        self,
        user_id: uuid.UUID,
        skill_name: str,
        severity: float,
        interview_id: Optional[uuid.UUID] = None,
        identified_by: str = "feedback_agent",
    ) -> None:
        skill_area = await self.skill_area_repo.get_by_name(skill_name)
        if not skill_area:
            return

        await self.skill_gap_repo.create(
            user_id=user_id,
            skill_area_id=skill_area.id,
            gap_severity=severity,
            related_interview_id=interview_id,
            identified_by_agent=identified_by,
            identified_at=datetime.now(timezone.utc),
        )

    async def get_user_gaps(self, user_id: uuid.UUID) -> List[SkillGap]:
        return await self.skill_gap_repo.get_user_gaps(user_id, resolved=False)

    async def initialize_user_skills(self, user_id: uuid.UUID) -> None:
        """Initialize default skill scores for a new user."""
        skill_areas = await self.skill_area_repo.get_all_skills()
        for area in skill_areas:
            existing = await self.user_skill_repo.get_user_skill(user_id, area.id)
            if not existing:
                await self.user_skill_repo.create(
                    user_id=user_id,
                    skill_area_id=area.id,
                    proficiency_score=50.0,
                    confidence_score=50.0,
                )
