"""LangGraph workflow nodes — each node is an async function that updates InterviewState."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from app.agents.feedback_agent import FeedbackAgent
from app.agents.interview_agent import InterviewAgent
from app.agents.learning_agent import LearningAgent
from app.agents.workflows.states import InterviewState

logger = logging.getLogger(__name__)

# Agent singletons (initialized once per process)
_interview_agent: InterviewAgent = None
_feedback_agent: FeedbackAgent = None
_learning_agent: LearningAgent = None


def get_agents():
    global _interview_agent, _feedback_agent, _learning_agent
    if not _interview_agent:
        _interview_agent = InterviewAgent()
        _feedback_agent = FeedbackAgent()
        _learning_agent = LearningAgent()
    return _interview_agent, _feedback_agent, _learning_agent


async def initialize_node(state: InterviewState) -> Dict:
    """Node 1: Initialize interview session with user context."""
    logger.info(f"[INIT] Interview {state.get('interview_id')} starting")

    return {
        "questions_asked": 0,
        "current_score": 70.0,
        "technical_score": 70.0,
        "communication_score": 70.0,
        "scores_history": [],
        "used_question_ids": [],
        "difficulty_adjustments": 0,
        "should_increase_difficulty": False,
        "should_decrease_difficulty": False,
        "interview_complete": False,
        "messages": [],
        "events": [{"type": "interview_initialized", "timestamp": datetime.now(timezone.utc).isoformat()}],
        "errors": [],
        "total_llm_cost_usd": 0.0,
        "next_action": "generate_question",
    }


async def generate_question_node(state: InterviewState, session=None) -> Dict:
    """Node 2: Generate/select next interview question."""
    interview_agent, _, _ = get_agents()

    questions_asked = state.get("questions_asked", 0)
    difficulty = state.get("difficulty_level", "medium")
    interview_type = state.get("interview_type", "system_design")
    user_skills = state.get("user_skills", {})
    current_score = state.get("current_score", 70.0)
    used_ids = state.get("used_question_ids", [])

    # Determine skill focus
    skill_area = interview_agent.determine_next_skill_focus(
        user_skills, interview_type, questions_asked
    )

    # Get candidate questions from DB if session available
    candidate_questions = []
    if session:
        try:
            from app.services.interview_service import InterviewService
            svc = InterviewService(session)
            question_dict = await svc.get_next_question(
                interview_id=uuid.UUID(state["interview_id"]),
                interview_type=interview_type,
                difficulty=difficulty,
                used_question_ids=[uuid.UUID(qid) for qid in used_ids if qid],
            )
            if question_dict:
                candidate_questions = [question_dict]
        except Exception as e:
            logger.error(f"Error fetching question from DB: {e}")
            state.get("errors", []).append(str(e))

    # Use AI agent to select best question
    if candidate_questions:
        selected = await interview_agent.select_question(
            candidate_questions=candidate_questions,
            user_context=state.get("user_context", {}),
            current_score=current_score,
            interview_type=interview_type,
            skill_area=skill_area,
            questions_asked=questions_asked,
        )
    else:
        # Fallback mock question for development
        selected = {
            "id": str(uuid.uuid4()),
            "title": f"Q{questions_asked + 1}: {interview_type.replace('_', ' ').title()} Question",
            "content": _get_fallback_question(interview_type, difficulty, questions_asked),
            "difficulty": difficulty,
            "skill_areas": [skill_area],
            "followup_hints": ["Consider scalability", "Discuss trade-offs", "Think about edge cases"],
        }

    # Record question in DB
    interview_question_id = None
    if session and selected.get("id"):
        try:
            from app.services.interview_service import InterviewService
            from app.repositories.interview_repository import InterviewQuestionRepository
            svc = InterviewService(session)
            try:
                q_uuid = uuid.UUID(selected["id"])
                iq = await svc.record_question(
                    interview_id=uuid.UUID(state["interview_id"]),
                    question_id=q_uuid,
                    question_index=questions_asked,
                )
                interview_question_id = str(iq.id)
            except Exception:
                pass  # Skip if question ID isn't in DB (mock)
        except Exception as e:
            logger.warning(f"Could not record question: {e}")

    new_used_ids = used_ids + [selected.get("id", "")]
    new_messages = state.get("messages", []) + [{
        "role": "assistant",
        "content": selected.get("content", ""),
        "type": "question",
        "question_id": selected.get("id"),
    }]

    logger.info(f"[QUESTION] Q{questions_asked + 1}: {selected.get('title', 'Untitled')}")

    return {
        "current_question": selected,
        "current_interview_question_id": interview_question_id,
        "messages": new_messages,
        "questions_asked": questions_asked + 1,
        "used_question_ids": new_used_ids,
        "next_action": "process_answer",
        "events": state.get("events", []) + [{
            "type": "question_generated",
            "question_id": selected.get("id"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }


async def process_answer_node(state: InterviewState, session=None) -> Dict:
    """Node 3: Process and store user's answer."""
    current_answer = state.get("current_answer", "")
    iq_id = state.get("current_interview_question_id")
    answer_id = None

    if session and iq_id and current_answer:
        try:
            from app.services.interview_service import InterviewService
            svc = InterviewService(session)
            answer = await svc.submit_answer(
                interview_question_id=uuid.UUID(iq_id),
                answer_text=current_answer,
            )
            answer_id = str(answer.id)
        except Exception as e:
            logger.error(f"Error storing answer: {e}")

    new_messages = state.get("messages", []) + [{
        "role": "user",
        "content": current_answer,
        "type": "answer",
    }]

    return {
        "messages": new_messages,
        "current_answer_id": answer_id,
        "next_action": "evaluate_answer",
    }


async def evaluate_answer_node(state: InterviewState, session=None) -> Dict:
    """Node 4: Evaluate the answer using Feedback Agent."""
    _, feedback_agent, _ = get_agents()

    current_question = state.get("current_question", {})
    current_answer = state.get("current_answer", "")
    interview_type = state.get("interview_type", "system_design")

    evaluation = await feedback_agent.evaluate_answer(
        question=current_question,
        answer=current_answer,
        interview_type=interview_type,
        expected_context=current_question.get("expected_answer_summary"),
    )

    # Update running scores
    overall = float(evaluation.get("overall_score", 50))
    technical = float(evaluation.get("technical_accuracy", 50))
    communication = float(evaluation.get("communication_quality", 50))
    questions_asked = state.get("questions_asked", 1)

    # Weighted moving average
    prev_overall = state.get("current_score", 70)
    new_overall = (prev_overall * (questions_asked - 1) + overall) / questions_asked

    prev_tech = state.get("technical_score", 70)
    new_tech = (prev_tech * (questions_asked - 1) + technical) / questions_asked

    prev_comm = state.get("communication_score", 70)
    new_comm = (prev_comm * (questions_asked - 1) + communication) / questions_asked

    # Save evaluation to DB
    if session and state.get("current_answer_id"):
        try:
            from app.services.interview_service import InterviewService
            svc = InterviewService(session)
            await svc.save_evaluation(
                answer_id=uuid.UUID(state["current_answer_id"]),
                scores={
                    "technical_accuracy": technical,
                    "completeness": evaluation.get("completeness", 50),
                    "communication_quality": communication,
                    "problem_solving_approach": evaluation.get("problem_solving_approach", 50),
                    "confidence_level": evaluation.get("confidence_level", 50),
                    "overall_score": overall,
                },
                feedback={
                    "strengths": evaluation.get("strengths", []),
                    "improvements": evaluation.get("improvements", []),
                    "gaps_identified": [g.get("skill") for g in evaluation.get("gaps_identified", [])],
                    "feedback_summary": evaluation.get("feedback_summary", ""),
                },
                model="gemini-2.0-flash",
                tokens={"prompt": 0, "completion": 0, "total": 0},
                cost_usd=0.0,
            )
        except Exception as e:
            logger.error(f"Error saving evaluation: {e}")

    logger.info(f"[EVAL] Score: {overall:.1f}/100 (tech: {technical:.1f}, comm: {communication:.1f})")

    return {
        "current_evaluation": evaluation,
        "current_score": new_overall,
        "technical_score": new_tech,
        "communication_score": new_comm,
        "scores_history": state.get("scores_history", []) + [overall],
        "next_action": "analyze_and_adjust",
        "events": state.get("events", []) + [{
            "type": "evaluation_complete",
            "score": overall,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }


async def analyze_and_adjust_node(state: InterviewState) -> Dict:
    """Node 5: Analyze evaluation and adjust difficulty."""
    interview_agent, _, _ = get_agents()

    current_score = state.get("current_score", 70)
    current_difficulty = state.get("difficulty_level", "medium")
    adjustments = state.get("difficulty_adjustments", 0)
    questions_asked = state.get("questions_asked", 1)
    total_planned = state.get("total_questions_planned", 5)

    # Determine difficulty adjustment
    new_difficulty = interview_agent.adjust_difficulty(current_difficulty, current_score, adjustments)
    increased = new_difficulty != current_difficulty and _difficulty_rank(new_difficulty) > _difficulty_rank(current_difficulty)
    decreased = new_difficulty != current_difficulty and _difficulty_rank(new_difficulty) < _difficulty_rank(current_difficulty)

    new_adjustments = adjustments + (1 if increased else -1 if decreased else 0)

    # Should we conclude?
    should_conclude = questions_asked >= total_planned
    next_action = "conclude" if should_conclude else "generate_question"

    events = state.get("events", [])
    if increased or decreased:
        events = events + [{
            "type": "difficulty_adjusted",
            "from": current_difficulty,
            "to": new_difficulty,
            "score": current_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]

    return {
        "difficulty_level": new_difficulty,
        "should_increase_difficulty": increased,
        "should_decrease_difficulty": decreased,
        "difficulty_adjustments": new_adjustments,
        "next_action": next_action,
        "events": events,
    }


async def learning_analysis_node(state: InterviewState, session=None) -> Dict:
    """Node 6: Learning Agent analyzes and records skill gaps."""
    _, _, learning_agent = get_agents()

    evaluation = state.get("current_evaluation", {})
    user_skills = state.get("user_skills", {})
    interview_type = state.get("interview_type", "system_design")
    current_question = state.get("current_question", {})

    # Only run if evaluation has meaningful data
    if not evaluation or evaluation.get("overall_score", 0) == 0:
        return {}

    try:
        analysis = await learning_agent.analyze_and_recommend(
            evaluation=evaluation,
            user_skills=user_skills,
            interview_type=interview_type,
            question_content=current_question.get("content"),
        )

        # Record gaps in DB
        if session and analysis.get("gaps_identified"):
            try:
                from app.services.skill_service import SkillService
                skill_svc = SkillService(session)
                for gap in analysis.get("gaps_identified", []):
                    await skill_svc.record_skill_gap(
                        user_id=uuid.UUID(state["user_id"]),
                        skill_name=gap.get("skill", "unknown"),
                        severity=float(gap.get("severity", 0.5)),
                        interview_id=uuid.UUID(state["interview_id"]),
                        identified_by="learning_agent",
                    )
            except Exception as e:
                logger.error(f"Error recording skill gaps: {e}")

    except Exception as e:
        logger.error(f"LearningAnalysis error: {e}")
        analysis = {}

    return {
        "events": state.get("events", []) + [{
            "type": "learning_analysis_complete",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }


async def conclude_node(state: InterviewState, session=None) -> Dict:
    """Node 7: Generate final report and complete interview."""
    final_score = state.get("current_score", 0)
    technical = state.get("technical_score", 0)
    communication = state.get("communication_score", 0)
    questions = state.get("questions_asked", 0)
    scores_history = state.get("scores_history", [])

    # Score trend
    trend = "stable"
    if len(scores_history) >= 2:
        if scores_history[-1] > scores_history[0]:
            trend = "improving"
        elif scores_history[-1] < scores_history[0]:
            trend = "declining"

    final_report = {
        "overall_score": round(final_score, 2),
        "technical_score": round(technical, 2),
        "communication_score": round(communication, 2),
        "questions_answered": questions,
        "score_trend": trend,
        "difficulty_adjustments": state.get("difficulty_adjustments", 0),
        "total_cost_usd": state.get("total_llm_cost_usd", 0),
    }

    # Update interview in DB
    if session:
        try:
            from app.services.interview_service import InterviewService
            svc = InterviewService(session)
            await svc.complete_interview(
                interview_id=uuid.UUID(state["interview_id"]),
                overall_score=final_score,
                technical_score=technical,
                communication_score=communication,
            )
        except Exception as e:
            logger.error(f"Error completing interview: {e}")

    logger.info(f"[CONCLUDE] Interview {state.get('interview_id')} complete. Score: {final_score:.1f}")

    return {
        "interview_complete": True,
        "final_report": final_report,
        "next_action": "exit",
        "events": state.get("events", []) + [{
            "type": "interview_completed",
            "final_score": final_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }


# ── Router ─────────────────────────────────────────────────────

def orchestrator_router(state: InterviewState) -> str:
    """Route to the next node based on state.next_action."""
    action = state.get("next_action", "generate_question")
    routing = {
        "generate_question": "generate_question",
        "process_answer": "process_answer",
        "evaluate_answer": "evaluate_answer",
        "analyze_and_adjust": "analyze_and_adjust",
        "conclude": "conclude_interview",
        "exit": "__end__",
    }
    return routing.get(action, "generate_question")


def after_adjust_router(state: InterviewState) -> str:
    """Route after analyze_and_adjust: learning_analysis always runs, then check if done."""
    if state.get("next_action") == "conclude":
        return "conclude_interview"
    return "generate_question"


# ── Helpers ────────────────────────────────────────────────────

def _difficulty_rank(difficulty: str) -> int:
    return {"easy": 0, "medium": 1, "hard": 2, "expert": 3}.get(difficulty, 1)


def _get_fallback_question(interview_type: str, difficulty: str, index: int) -> str:
    """Fallback questions when DB has no data yet."""
    questions = {
        "system_design": [
            "Design a URL shortener service like bit.ly. Walk me through the architecture, considering scalability to handle 1 billion URLs.",
            "Design a distributed message queue system like Kafka. How would you handle message ordering, durability, and high throughput?",
            "Design a real-time collaborative document editing system like Google Docs. Address concurrency and conflict resolution.",
            "Design a ride-sharing service like Uber. How would you handle matching, real-time location tracking, and surge pricing?",
            "Design a content delivery network (CDN). Explain caching strategies, geographic distribution, and cache invalidation.",
        ],
        "algorithms": [
            "Given a binary tree, find the maximum path sum. The path doesn't need to start or end at the root.",
            "Implement an LRU (Least Recently Used) cache with O(1) get and put operations.",
            "Given a list of intervals, merge all overlapping intervals. Discuss time and space complexity.",
            "Find the kth largest element in an unsorted array. Discuss multiple approaches and their trade-offs.",
            "Implement a trie data structure and use it to implement autocomplete functionality.",
        ],
        "behavioral": [
            "Tell me about a time you had to make a difficult technical decision with incomplete information. What was your process?",
            "Describe a project where you had to work with a difficult stakeholder. How did you handle it?",
            "Tell me about a time you failed on a project. What did you learn and how did you apply those lessons?",
            "Describe a time you had to mentor or help a struggling team member. What was your approach?",
            "Tell me about a time you had to push back on a requirement. How did you handle it?",
        ],
    }
    q_list = questions.get(interview_type, questions["system_design"])
    return q_list[index % len(q_list)]
