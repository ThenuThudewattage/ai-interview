"""Evaluation repository."""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import Evaluation
from app.repositories.base_repository import BaseRepository


class EvaluationRepository(BaseRepository[Evaluation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Evaluation, session)

    async def get_by_answer(self, answer_id: uuid.UUID) -> List[Evaluation]:
        result = await self.session.execute(
            select(Evaluation)
            .where(Evaluation.answer_id == answer_id)
            .order_by(Evaluation.evaluated_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest_for_answer(self, answer_id: uuid.UUID) -> Optional[Evaluation]:
        result = await self.session.execute(
            select(Evaluation)
            .where(Evaluation.answer_id == answer_id)
            .order_by(Evaluation.evaluated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
