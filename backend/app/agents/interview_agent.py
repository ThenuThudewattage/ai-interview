"""Interview Agent — conducts interviews, selects questions, adapts difficulty."""
import json
import logging
from typing import Any, Dict, List, Optional

from app.external.llm.gemini_client import get_llm_client
from app.external.llm.base_client import LLMMessage

logger = logging.getLogger(__name__)

INTERVIEW_SYSTEM_PROMPT = """You are an expert technical interview conductor with 15+ years of experience interviewing engineers at top tech companies (Google, Meta, Amazon, Microsoft).

Your role is to SELECT the most appropriate interview question for the candidate from a provided list of candidates.

Given:
- Candidate's profile and current performance
- A list of candidate questions
- The skill area to focus on
- Interview type and difficulty level

Select the BEST question that:
1. Matches the candidate's current skill level and performance
2. Covers the target skill area
3. Hasn't been covered in previous questions (variety)
4. Progressively builds on what we've learned about the candidate

Return a JSON object with:
{
    "selected_question_index": <int, 0-based index from the candidates list>,
    "reasoning": "<why this question is the best choice>",
    "adjusted_difficulty_hint": "<any adjustments to how to present the question>"
}"""


class InterviewAgent:
    """Agent responsible for selecting and presenting interview questions."""

    def __init__(self):
        self.llm = get_llm_client()

    async def select_question(
        self,
        candidate_questions: List[Dict],
        user_context: Dict,
        current_score: float,
        interview_type: str,
        skill_area: str,
        questions_asked: int,
    ) -> Dict[str, Any]:
        """Select the best question from candidates using AI."""

        if not candidate_questions:
            return {}

        # If only one candidate, return it directly
        if len(candidate_questions) == 1:
            return candidate_questions[0]

        messages = [
            LLMMessage(role="system", content=INTERVIEW_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=f"""
Candidate Profile:
- Experience: {user_context.get('years_of_experience', 'Unknown')} years
- Current Role: {user_context.get('current_job_title', 'Unknown')}
- Interview Type: {interview_type}
- Questions Asked So Far: {questions_asked}
- Current Performance Score: {current_score:.1f}/100
- Focus Skill Area: {skill_area}

Candidate Questions (pick the best):
{json.dumps([{"index": i, "title": q.get("title"), "difficulty": q.get("difficulty"), "skill_areas": q.get("skill_areas")} for i, q in enumerate(candidate_questions)], indent=2)}

Select the best question to ask next.
""",
            ),
        ]

        try:
            result = await self.llm.generate_structured(
                messages,
                {"selected_question_index": 0, "reasoning": "", "adjusted_difficulty_hint": ""},
            )
            idx = int(result.get("selected_question_index", 0))
            if 0 <= idx < len(candidate_questions):
                return candidate_questions[idx]
        except Exception as e:
            logger.error(f"InterviewAgent error: {e}")

        return candidate_questions[0]

    def determine_next_skill_focus(
        self,
        user_skills: Dict[str, float],
        interview_type: str,
        questions_asked: int,
    ) -> str:
        """Determine which skill area to focus on next."""
        skill_priority = {
            "system_design": ["system_design", "distributed_systems", "databases", "scalability", "caching"],
            "algorithms": ["algorithms", "data_structures", "complexity_analysis", "dynamic_programming", "graphs"],
            "behavioral": ["leadership", "communication", "problem_solving", "teamwork", "adaptability"],
            "coding": ["algorithms", "data_structures", "clean_code", "testing", "optimization"],
            "ml": ["machine_learning", "deep_learning", "statistics", "feature_engineering", "ml_systems"],
        }

        priority_skills = skill_priority.get(interview_type, ["general"])

        # Rotate through skills based on questions asked
        return priority_skills[questions_asked % len(priority_skills)]

    def adjust_difficulty(
        self,
        current_difficulty: str,
        current_score: float,
        adjustments_count: int,
    ) -> str:
        """Adjust difficulty based on performance."""
        from app.core.constants import DIFFICULTY_INCREASE_THRESHOLD, DIFFICULTY_DECREASE_THRESHOLD, MAX_DIFFICULTY_ADJUSTMENTS

        difficulty_order = ["easy", "medium", "hard", "expert"]
        current_idx = difficulty_order.index(current_difficulty) if current_difficulty in difficulty_order else 1

        if current_score >= DIFFICULTY_INCREASE_THRESHOLD and adjustments_count < MAX_DIFFICULTY_ADJUSTMENTS:
            new_idx = min(current_idx + 1, len(difficulty_order) - 1)
        elif current_score < DIFFICULTY_DECREASE_THRESHOLD and adjustments_count > -MAX_DIFFICULTY_ADJUSTMENTS:
            new_idx = max(current_idx - 1, 0)
        else:
            new_idx = current_idx

        return difficulty_order[new_idx]
