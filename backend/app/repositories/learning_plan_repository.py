"""Learning plan repository."""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.learning_plan import LearningPlan, LearningMilestone, LearningResource
from app.repositories.base_repository import BaseRepository


class LearningPlanRepository(BaseRepository[LearningPlan]):
    def __init__(self, session: AsyncSession):
        super().__init__(LearningPlan, session)

    async def get_user_plans(
        self, user_id: uuid.UUID, status: Optional[str] = None
    ) -> List[LearningPlan]:
        stmt = (
            select(LearningPlan)
            .where(LearningPlan.user_id == user_id)
            .order_by(LearningPlan.created_at.desc())
        )
        if status:
            stmt = stmt.where(LearningPlan.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_milestones(self, plan_id: uuid.UUID) -> Optional[LearningPlan]:
        result = await self.session.execute(
            select(LearningPlan)
            .options(
                selectinload(LearningPlan.milestones).selectinload(
                    LearningMilestone.resources
                )
            )
            .where(LearningPlan.id == plan_id)
        )
        return result.scalar_one_or_none()


class LearningResourceRepository(BaseRepository[LearningResource]):
    def __init__(self, session: AsyncSession):
        super().__init__(LearningResource, session)

    async def get_milestone_resources(
        self, milestone_id: uuid.UUID
    ) -> List[LearningResource]:
        result = await self.session.execute(
            select(LearningResource)
            .where(LearningResource.learning_milestone_id == milestone_id)
            .order_by(LearningResource.assigned_at)
        )
        return list(result.scalars().all())
