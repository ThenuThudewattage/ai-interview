"""Skill repositories."""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.skill import SkillArea, UserSkill, SkillGap, SkillAssessmentHistory
from app.repositories.base_repository import BaseRepository


class SkillAreaRepository(BaseRepository[SkillArea]):
    def __init__(self, session: AsyncSession):
        super().__init__(SkillArea, session)

    async def get_by_name(self, name: str) -> Optional[SkillArea]:
        result = await self.session.execute(
            select(SkillArea).where(SkillArea.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_skills(self) -> List[SkillArea]:
        result = await self.session.execute(select(SkillArea).order_by(SkillArea.name))
        return list(result.scalars().all())


class UserSkillRepository(BaseRepository[UserSkill]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserSkill, session)

    async def get_user_skills(self, user_id: uuid.UUID) -> List[UserSkill]:
        result = await self.session.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill_area))
            .where(UserSkill.user_id == user_id)
            .order_by(UserSkill.proficiency_score.desc())
        )
        return list(result.scalars().all())

    async def get_user_skill(
        self, user_id: uuid.UUID, skill_area_id: uuid.UUID
    ) -> Optional[UserSkill]:
        result = await self.session.execute(
            select(UserSkill).where(
                UserSkill.user_id == user_id,
                UserSkill.skill_area_id == skill_area_id,
            )
        )
        return result.scalar_one_or_none()


class SkillGapRepository(BaseRepository[SkillGap]):
    def __init__(self, session: AsyncSession):
        super().__init__(SkillGap, session)

    async def get_user_gaps(
        self, user_id: uuid.UUID, resolved: bool = False
    ) -> List[SkillGap]:
        result = await self.session.execute(
            select(SkillGap)
            .options(selectinload(SkillGap.skill_area))
            .where(
                SkillGap.user_id == user_id,
                SkillGap.is_resolved == resolved,
            )
            .order_by(SkillGap.gap_severity.desc())
        )
        return list(result.scalars().all())
