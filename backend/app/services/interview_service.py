"""Interview service — orchestrates the interview workflow."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, InterviewException
from app.models.answer import Answer
from app.models.evaluation import Evaluation
from app.models.interview import Interview, InterviewQuestion
from app.repositories.answer_repository import AnswerRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.interview_repository import InterviewRepository, InterviewQuestionRepository, QuestionRepository


class InterviewService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.interview_repo = InterviewRepository(session)
        self.question_repo = QuestionRepository(session)
        self.iq_repo = InterviewQuestionRepository(session)
        self.answer_repo = AnswerRepository(session)
        self.eval_repo = EvaluationRepository(session)

    async def create_interview(
        self,
        user_id: uuid.UUID,
        interview_type: str,
        difficulty_level: str,
        target_company: Optional[str] = None,
        target_role: Optional[str] = None,
        duration_minutes: int = 60,
        total_questions: int = 5,
    ) -> Interview:
        interview = await self.interview_repo.create(
            user_id=user_id,
            interview_type=interview_type,
            difficulty_level=difficulty_level,
            target_company=target_company,
            target_role=target_role,
            duration_minutes=duration_minutes,
            total_questions_planned=total_questions,
            status="in_progress",
            started_at=datetime.now(timezone.utc),
        )
        return interview

    async def get_interview(self, interview_id: uuid.UUID) -> Interview:
        interview = await self.interview_repo.get_by_id(interview_id)
        if not interview:
            raise NotFoundException("Interview", str(interview_id))
        return interview

    async def get_user_interviews(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[List[Interview], int]:
        interviews = await self.interview_repo.get_user_interviews(user_id, limit, offset)
        total = await self.interview_repo.count_user_interviews(user_id)
        return interviews, total

    async def get_next_question(
        self,
        interview_id: uuid.UUID,
        interview_type: str,
        difficulty: str,
        used_question_ids: List[uuid.UUID],
    ) -> Optional[Dict]:
        """Get next question from the question bank."""
        # Map interview type to question type
        type_map = {
            "system_design": "system_design",
            "algorithms": "algorithm",
            "behavioral": "behavioral",
            "coding": "coding",
            "ml": "ml",
        }
        q_type = type_map.get(interview_type, "general")

        questions = await self.question_repo.search_by_type_and_difficulty(
            question_type=q_type,
            difficulty=difficulty,
            exclude_ids=used_question_ids,
            limit=10,
        )

        if not questions:
            # Try any difficulty
            questions = await self.question_repo.search_by_type_and_difficulty(
                question_type=q_type,
                difficulty=difficulty,
                limit=10,
            )

        if not questions:
            return None

        # Return first available question (agents can be more sophisticated)
        q = questions[0]
        return {
            "id": str(q.id),
            "title": q.title,
            "content": q.content,
            "difficulty": q.difficulty_level,
            "skill_areas": q.skill_areas,
            "estimated_time_minutes": q.estimated_time_minutes,
            "followup_hints": q.followup_hints or [],
            "expected_answer_summary": q.expected_answer_summary,
        }

    async def record_question(
        self,
        interview_id: uuid.UUID,
        question_id: uuid.UUID,
        question_index: int,
    ) -> InterviewQuestion:
        return await self.iq_repo.create(
            interview_id=interview_id,
            question_id=question_id,
            question_index=question_index,
            asked_at=datetime.now(timezone.utc),
        )

    async def submit_answer(
        self,
        interview_question_id: uuid.UUID,
        answer_text: str,
        time_spent_seconds: int = 0,
    ) -> Answer:
        word_count = len(answer_text.split())
        answer = await self.answer_repo.create(
            interview_question_id=interview_question_id,
            answer_text=answer_text,
            word_count=word_count,
            character_count=len(answer_text),
            submitted_at=datetime.now(timezone.utc),
        )
        return answer

    async def save_evaluation(
        self,
        answer_id: uuid.UUID,
        scores: Dict[str, Any],
        feedback: Dict[str, Any],
        model: str,
        tokens: Dict[str, int],
        cost_usd: float,
    ) -> Evaluation:
        evaluation = await self.eval_repo.create(
            answer_id=answer_id,
            evaluator_model=model,
            technical_accuracy=scores.get("technical_accuracy"),
            completeness=scores.get("completeness"),
            communication_quality=scores.get("communication_quality"),
            problem_solving_approach=scores.get("problem_solving_approach"),
            confidence_level=scores.get("confidence_level"),
            overall_score=scores.get("overall_score"),
            strengths=feedback.get("strengths", []),
            improvements=feedback.get("improvements", []),
            key_gaps_identified=feedback.get("gaps_identified", []),
            feedback_summary=feedback.get("feedback_summary", ""),
            detailed_feedback=feedback.get("detailed_feedback", ""),
            llm_prompt_tokens=tokens.get("prompt"),
            llm_completion_tokens=tokens.get("completion"),
            llm_total_tokens=tokens.get("total"),
            llm_cost_usd=cost_usd,
            evaluated_at=datetime.now(timezone.utc),
        )
        return evaluation

    async def complete_interview(
        self,
        interview_id: uuid.UUID,
        overall_score: float,
        technical_score: float,
        communication_score: float,
    ) -> Interview:
        interview = await self.get_interview(interview_id)
        return await self.interview_repo.update(
            interview,
            status="completed",
            completed_at=datetime.now(timezone.utc),
            overall_score=overall_score,
            technical_score=technical_score,
            communication_score=communication_score,
        )

    async def get_interview_evaluations(self, interview_id: uuid.UUID) -> List[Dict]:
        """Get all evaluations for an interview with context."""
        interview = await self.interview_repo.get_with_questions(interview_id)
        if not interview:
            raise NotFoundException("Interview", str(interview_id))

        results = []
        for iq in interview.interview_questions:
            for answer in iq.answers:
                answer_with_evals = await self.answer_repo.get_with_evaluations(answer.id)
                if answer_with_evals and answer_with_evals.evaluations:
                    latest_eval = answer_with_evals.evaluations[0]
                    results.append({
                        "question_index": iq.question_index,
                        "question_id": str(iq.question_id),
                        "answer_id": str(answer.id),
                        "evaluation": latest_eval,
                    })
        return results
