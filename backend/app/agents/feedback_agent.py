"""Feedback Agent — evaluates candidate answers with multi-dimensional scoring."""
import json
import logging
from typing import Any, Dict, Optional

from app.external.llm.base_client import LLMMessage
from app.external.llm.gemini_client import get_llm_client

logger = logging.getLogger(__name__)

FEEDBACK_SYSTEM_PROMPT = """You are an expert technical interviewer and evaluator with deep expertise in software engineering, system design, algorithms, and behavioral assessment.

Your role is to provide FAIR, CONSTRUCTIVE, and DETAILED evaluation of a candidate's interview answer.

Evaluate on these 5 dimensions (each 0-100):
1. **Technical Accuracy** (35% weight): Is the answer correct? Does it demonstrate understanding?
2. **Completeness** (25% weight): Does it cover the key aspects? Are important points addressed?
3. **Communication Quality** (20% weight): Is it clear, structured, and easy to follow?
4. **Problem-Solving Approach** (15% weight): Did they show systematic thinking? Did they clarify, consider trade-offs?
5. **Confidence Level** (5% weight): Did they seem confident and decisive?

Calculate overall_score = weighted average of all 5 dimensions.

Return a JSON object:
{
    "technical_accuracy": <0-100>,
    "completeness": <0-100>,
    "communication_quality": <0-100>,
    "problem_solving_approach": <0-100>,
    "confidence_level": <0-100>,
    "overall_score": <0-100 weighted average>,
    "strengths": ["<specific strength 1>", "<specific strength 2>"],
    "improvements": ["<specific improvement 1>", "<specific improvement 2>"],
    "gaps_identified": [
        {"skill": "<skill name>", "severity": <0.0-1.0>, "description": "<what was missing>"}
    ],
    "feedback_summary": "<2-3 sentence constructive summary>",
    "evaluator_confidence": <0.0-1.0>
}"""


class FeedbackAgent:
    """Agent responsible for evaluating candidate answers."""

    def __init__(self):
        self.llm = get_llm_client()

    async def evaluate_answer(
        self,
        question: Dict,
        answer: str,
        interview_type: str,
        expected_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate a candidate's answer using LLM."""

        expected_section = ""
        if expected_context:
            expected_section = f"\nExpected Answer Context (key points to cover):\n{expected_context}\n"

        messages = [
            LLMMessage(role="system", content=FEEDBACK_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=f"""
Interview Type: {interview_type}
Question: {question.get("content", "")}
Difficulty: {question.get("difficulty", "medium")}
Skill Areas: {", ".join(question.get("skill_areas", []))}
{expected_section}
Candidate's Answer:
---
{answer}
---

Please evaluate this answer thoroughly and return the JSON evaluation.
""",
            ),
        ]

        try:
            result = await self.llm.generate_structured(messages, {
                "technical_accuracy": 0,
                "completeness": 0,
                "communication_quality": 0,
                "problem_solving_approach": 0,
                "confidence_level": 0,
                "overall_score": 0,
                "strengths": [],
                "improvements": [],
                "gaps_identified": [],
                "feedback_summary": "",
                "evaluator_confidence": 0.8,
            })

            # Validate and normalize scores
            for field in ["technical_accuracy", "completeness", "communication_quality",
                          "problem_solving_approach", "confidence_level", "overall_score"]:
                if field in result:
                    result[field] = max(0, min(100, float(result[field])))

            # Recalculate overall_score with weights to ensure accuracy
            weights = {
                "technical_accuracy": 0.35,
                "completeness": 0.25,
                "communication_quality": 0.20,
                "problem_solving_approach": 0.15,
                "confidence_level": 0.05,
            }
            weighted_score = sum(
                result.get(k, 50) * w for k, w in weights.items()
            )
            result["overall_score"] = round(weighted_score, 2)

            return result

        except Exception as e:
            logger.error(f"FeedbackAgent error: {e}")
            # Return a default evaluation on error
            return {
                "technical_accuracy": 50,
                "completeness": 50,
                "communication_quality": 50,
                "problem_solving_approach": 50,
                "confidence_level": 50,
                "overall_score": 50,
                "strengths": [],
                "improvements": ["Evaluation failed - please retry"],
                "gaps_identified": [],
                "feedback_summary": f"Evaluation error: {str(e)}",
                "evaluator_confidence": 0.0,
            }
