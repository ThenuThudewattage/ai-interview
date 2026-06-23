"""Learning Agent — analyzes performance and generates personalized learning paths."""
import logging
from typing import Any, Dict, List, Optional

from app.external.llm.base_client import LLMMessage
from app.external.llm.gemini_client import get_llm_client

logger = logging.getLogger(__name__)

LEARNING_SYSTEM_PROMPT = """You are an expert in software engineering education and personalized learning design.

Your role is to analyze interview performance data and create actionable, specific learning recommendations.

Given an evaluation result and the user's current skill levels, you will:
1. Identify specific knowledge/skill gaps (be SPECIFIC, not vague)
2. Suggest concrete learning resources (real books, courses, platforms)
3. Create a structured learning roadmap

Return a JSON object:
{
    "gaps_identified": [
        {
            "skill": "<specific skill name>",
            "severity": <0.0-1.0>,
            "description": "<what specifically they're missing>",
            "example_from_answer": "<concrete example from their answer>"
        }
    ],
    "learning_plan": {
        "title": "<descriptive plan title>",
        "description": "<2-3 sentence description>",
        "estimated_total_hours": <int>,
        "milestones": [
            {
                "name": "<milestone name>",
                "description": "<what they'll learn>",
                "sequence": <int>,
                "target_score": <0-100>,
                "estimated_days": <int>,
                "resources": [
                    {
                        "title": "<resource title>",
                        "type": "<article|video|course|book|practice_set>",
                        "url": "<URL if known>",
                        "estimated_time_minutes": <int>,
                        "proficiency_level": "<beginner|intermediate|advanced>"
                    }
                ]
            }
        ]
    },
    "next_interview_focus": ["<skill 1>", "<skill 2>"],
    "encouragement": "<1-2 sentence motivational message>"
}"""


class LearningAgent:
    """Agent responsible for analyzing performance and creating learning plans."""

    def __init__(self):
        self.llm = get_llm_client()

    async def analyze_and_recommend(
        self,
        evaluation: Dict[str, Any],
        user_skills: Dict[str, float],
        interview_type: str,
        question_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze evaluation and generate learning recommendations."""

        messages = [
            LLMMessage(role="system", content=LEARNING_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=f"""
Interview Type: {interview_type}
Question Asked: {question_content or "N/A"}

Evaluation Results:
- Technical Accuracy: {evaluation.get("technical_accuracy", 0)}/100
- Completeness: {evaluation.get("completeness", 0)}/100
- Communication Quality: {evaluation.get("communication_quality", 0)}/100
- Problem-Solving Approach: {evaluation.get("problem_solving_approach", 0)}/100
- Overall Score: {evaluation.get("overall_score", 0)}/100

Identified Improvements Needed: {evaluation.get("improvements", [])}
Gaps from Evaluator: {evaluation.get("gaps_identified", [])}

User's Current Skill Levels (0-100):
{chr(10).join(f"- {skill}: {score:.1f}" for skill, score in user_skills.items())}

Please analyze and create a targeted learning plan.
""",
            ),
        ]

        try:
            result = await self.llm.generate_structured(messages, {
                "gaps_identified": [],
                "learning_plan": {},
                "next_interview_focus": [],
                "encouragement": "",
            })
            return result
        except Exception as e:
            logger.error(f"LearningAgent error: {e}")
            return {
                "gaps_identified": [],
                "learning_plan": {"title": "Continue Practice", "milestones": []},
                "next_interview_focus": [interview_type],
                "encouragement": "Keep practicing — consistent effort leads to improvement!",
            }

    async def generate_full_plan(
        self,
        user_skills: Dict[str, float],
        skill_gaps: List[Dict],
        target_proficiency: float,
        available_hours_per_week: int,
        interview_type: str,
    ) -> Dict[str, Any]:
        """Generate a comprehensive learning plan from skill gaps."""

        gaps_text = "\n".join(
            f"- {g.get('skill', 'Unknown')}: severity {g.get('gap_severity', 0):.2f}"
            for g in skill_gaps[:10]
        )

        messages = [
            LLMMessage(role="system", content=LEARNING_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=f"""
Create a comprehensive learning plan for:
- Target Interview Type: {interview_type}
- Target Proficiency Goal: {target_proficiency}/100
- Available Study Time: {available_hours_per_week} hours/week

Current Skill Gaps (most critical):
{gaps_text}

Current Skills:
{chr(10).join(f"- {skill}: {score:.1f}/100" for skill, score in list(user_skills.items())[:10])}

Create a structured 4-6 week learning plan with specific milestones and resources.
""",
            ),
        ]

        try:
            return await self.llm.generate_structured(messages, {
                "gaps_identified": [],
                "learning_plan": {"title": "", "milestones": []},
                "next_interview_focus": [],
                "encouragement": "",
            })
        except Exception as e:
            logger.error(f"LearningAgent.generate_full_plan error: {e}")
            return {
                "learning_plan": {
                    "title": f"Master {interview_type.replace('_', ' ').title()}",
                    "description": "Comprehensive study plan",
                    "estimated_total_hours": available_hours_per_week * 4,
                    "milestones": [],
                }
            }
