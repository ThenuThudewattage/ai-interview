"""Interview and Question repositories."""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview import Interview, Question, InterviewQuestion
from app.repositories.base_repository import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: AsyncSession):
        super().__init__(Question, session)

    async def search_by_type_and_difficulty(
        self,
        question_type: str,
        difficulty: str,
        exclude_ids: Optional[List[uuid.UUID]] = None,
        limit: int = 5,
    ) -> List[Question]:
        stmt = (
            select(Question)
            .where(
                Question.question_type == question_type,
                Question.difficulty_level == difficulty,
                Question.is_latest == True,
            )
        )
        if exclude_ids:
            stmt = stmt.where(Question.id.not_in(exclude_ids))
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_skill_area(
        self, skill_area: str, difficulty: str, limit: int = 5
    ) -> List[Question]:
        from sqlalchemy import cast
        from sqlalchemy.dialects.postgresql import ARRAY
        from sqlalchemy import String
        stmt = (
            select(Question)
            .where(
                Question.skill_areas.contains([skill_area]),
                Question.difficulty_level == difficulty,
                Question.is_latest == True,
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_for_seed(self) -> List[Question]:
        result = await self.session.execute(select(Question).where(Question.is_latest == True))
        return list(result.scalars().all())


class InterviewRepository(BaseRepository[Interview]):
    def __init__(self, session: AsyncSession):
        super().__init__(Interview, session)

    async def get_user_interviews(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> List[Interview]:
        result = await self.session.execute(
            select(Interview)
            .where(Interview.user_id == user_id)
            .order_by(Interview.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_recent_completed(
        self, user_id: uuid.UUID, interview_type: str, limit: int = 5
    ) -> List[Interview]:
        result = await self.session.execute(
            select(Interview)
            .where(
                Interview.user_id == user_id,
                Interview.interview_type == interview_type,
                Interview.status == "completed",
            )
            .order_by(Interview.completed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_questions(self, interview_id: uuid.UUID) -> Optional[Interview]:
        result = await self.session.execute(
            select(Interview)
            .options(
                selectinload(Interview.interview_questions).selectinload(
                    InterviewQuestion.question
                )
            )
            .where(Interview.id == interview_id)
        )
        return result.scalar_one_or_none()

    async def count_user_interviews(self, user_id: uuid.UUID) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(Interview).where(Interview.user_id == user_id)
        )
        return result.scalar_one()


class InterviewQuestionRepository(BaseRepository[InterviewQuestion]):
    def __init__(self, session: AsyncSession):
        super().__init__(InterviewQuestion, session)

    async def get_interview_questions(self, interview_id: uuid.UUID) -> List[InterviewQuestion]:
        result = await self.session.execute(
            select(InterviewQuestion)
            .where(InterviewQuestion.interview_id == interview_id)
            .order_by(InterviewQuestion.question_index)
        )
        return list(result.scalars().all())
