"""Answer repository."""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.answer import Answer
from app.repositories.base_repository import BaseRepository


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Answer, session)

    async def get_by_interview_question(
        self, interview_question_id: uuid.UUID
    ) -> List[Answer]:
        result = await self.session.execute(
            select(Answer)
            .where(Answer.interview_question_id == interview_question_id)
            .order_by(Answer.submitted_at)
        )
        return list(result.scalars().all())

    async def get_with_evaluations(self, answer_id: uuid.UUID) -> Optional[Answer]:
        result = await self.session.execute(
            select(Answer)
            .options(selectinload(Answer.evaluations))
            .where(Answer.id == answer_id)
        )
        return result.scalar_one_or_none()
