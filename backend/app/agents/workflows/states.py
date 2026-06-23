"""LangGraph Interview Workflow State Definition."""
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class InterviewState(TypedDict, total=False):
    """Shared state across all agents in the interview workflow."""

    # ── Session Info ─────────────────────────────────────────────
    user_id: str
    interview_id: str
    session_id: str

    # ── Interview Config ──────────────────────────────────────────
    interview_type: str  # system_design, algorithms, behavioral, coding, ml
    difficulty_level: str  # easy, medium, hard, expert
    target_company: Optional[str]
    total_questions_planned: int

    # ── User Context ──────────────────────────────────────────────
    user_context: Dict[str, Any]   # User profile info
    user_skills: Dict[str, float]  # {skill_name: proficiency_score}
    interview_history: List[Dict]  # Previous interview summaries

    # ── Current State ─────────────────────────────────────────────
    messages: Annotated[list, add_messages]
    current_question: Optional[Dict]           # Current question dict
    current_interview_question_id: Optional[str]  # FK to interview_questions
    current_answer_id: Optional[str]
    current_answer: Optional[str]
    current_evaluation: Optional[Dict]
    used_question_ids: List[str]               # IDs of already-asked questions

    # ── Metrics ───────────────────────────────────────────────────
    questions_asked: int
    current_score: float        # Running weighted average (0-100)
    technical_score: float
    communication_score: float
    scores_history: List[float]  # Score per question

    # ── Decision Making ───────────────────────────────────────────
    next_action: str  # generate_question | process_answer | evaluate | conclude | exit
    should_increase_difficulty: bool
    should_decrease_difficulty: bool
    difficulty_adjustments: int

    # ── Completion ────────────────────────────────────────────────
    interview_complete: bool
    final_report: Optional[Dict]

    # ── Observability ─────────────────────────────────────────────
    correlation_id: str
    events: List[Dict]
    errors: List[str]
    total_llm_cost_usd: float
