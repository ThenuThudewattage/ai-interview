"""WebSocket endpoint for real-time interview streaming."""
import asyncio
import json
import logging
import uuid
from typing import Dict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.feedback_agent import FeedbackAgent
from app.agents.interview_agent import InterviewAgent
from app.agents.learning_agent import LearningAgent
from app.agents.workflows.states import InterviewState
from app.db.session import get_db
from app.services.interview_service import InterviewService
from app.services.skill_service import SkillService

router = APIRouter(prefix="/interviews", tags=["WebSocket"])
logger = logging.getLogger(__name__)

# Active WebSocket sessions: {session_id: WebSocket}
active_sessions: Dict[str, WebSocket] = {}

# Agent instances
interview_agent = InterviewAgent()
feedback_agent = FeedbackAgent()
learning_agent = LearningAgent()


@router.websocket("/{interview_id}/stream")
async def interview_stream(interview_id: str, websocket: WebSocket):
    """WebSocket endpoint for real-time interview interaction."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = websocket

    logger.info(f"WebSocket connected for interview {interview_id}, session {session_id}")

    try:
        # Send connection confirmed
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "interview_id": interview_id,
            "message": "WebSocket connection established. Ready for interview.",
        })

        # State for this session
        state = {
            "interview_id": interview_id,
            "session_id": session_id,
            "questions_asked": 0,
            "current_score": 70.0,
            "technical_score": 70.0,
            "communication_score": 70.0,
            "scores_history": [],
            "used_question_ids": [],
            "difficulty_adjustments": 0,
            "difficulty_level": "medium",
            "interview_type": "system_design",
            "total_questions_planned": 5,
            "user_skills": {},
            "user_context": {},
        }

        # Main message loop
        async for message in _receive_messages(websocket):
            msg_type = message.get("type", "")

            if msg_type == "init":
                # Client sends interview config
                state["interview_type"] = message.get("interview_type", "system_design")
                state["difficulty_level"] = message.get("difficulty_level", "medium")
                state["total_questions_planned"] = message.get("total_questions", 5)
                state["user_skills"] = message.get("user_skills", {})
                state["user_context"] = message.get("user_context", {})

                # Send first question
                await _send_next_question(websocket, state)

            elif msg_type == "answer":
                answer_text = message.get("answer_text", "")
                state["current_answer"] = answer_text
                state["questions_asked"] = state.get("questions_asked", 0) + 1

                # Acknowledge receipt
                await websocket.send_json({
                    "type": "answer_received",
                    "message": "Processing your answer...",
                })

                # Evaluate answer
                await _evaluate_and_respond(websocket, state)

                # Check if interview complete
                if state["questions_asked"] >= state["total_questions_planned"]:
                    await _send_completion(websocket, state)
                    break
                else:
                    # Send next question
                    await _send_next_question(websocket, state)

            elif msg_type == "request_hint":
                current_q = state.get("current_question", {})
                hints = current_q.get("followup_hints", ["Consider scalability", "Think about trade-offs"])
                await websocket.send_json({
                    "type": "hint",
                    "hints": hints,
                })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        active_sessions.pop(session_id, None)


async def _receive_messages(websocket: WebSocket):
    """Async generator for WebSocket messages."""
    while True:
        try:
            data = await websocket.receive_text()
            yield json.loads(data)
        except WebSocketDisconnect:
            break
        except json.JSONDecodeError:
            logger.warning("Invalid JSON received via WebSocket")
            continue


async def _send_next_question(websocket: WebSocket, state: dict):
    """Generate and send the next question."""
    from app.agents.workflows.nodes import _get_fallback_question

    questions_asked = state.get("questions_asked", 0)
    interview_type = state.get("interview_type", "system_design")
    difficulty = state.get("difficulty_level", "medium")

    # Use fallback questions for now (DB questions via HTTP endpoint)
    question_content = _get_fallback_question(interview_type, difficulty, questions_asked)
    question = {
        "id": str(uuid.uuid4()),
        "content": question_content,
        "difficulty": difficulty,
        "skill_areas": [interview_type],
        "estimated_time_minutes": 15 if interview_type == "behavioral" else 45,
        "followup_hints": ["Consider scalability", "Discuss trade-offs", "Think about edge cases"],
    }

    state["current_question"] = question

    await websocket.send_json({
        "type": "question",
        "event_type": "question_presented",
        "question_number": questions_asked + 1,
        "total_questions": state["total_questions_planned"],
        "question": {
            "question_id": question["id"],
            "content": question["content"],
            "difficulty": question["difficulty"],
            "skill_areas": question["skill_areas"],
            "estimated_time_minutes": question["estimated_time_minutes"],
            "followup_hints": question["followup_hints"],
        },
    })


async def _evaluate_and_respond(websocket: WebSocket, state: dict):
    """Evaluate the current answer and send results."""
    question = state.get("current_question", {})
    answer = state.get("current_answer", "")

    try:
        evaluation = await feedback_agent.evaluate_answer(
            question=question,
            answer=answer,
            interview_type=state.get("interview_type", "system_design"),
        )

        overall = float(evaluation.get("overall_score", 50))

        # Update running scores
        q_count = state["questions_asked"]
        state["current_score"] = (state["current_score"] * (q_count - 1) + overall) / q_count
        state["scores_history"].append(overall)

        # Adjust difficulty
        state["difficulty_level"] = interview_agent.adjust_difficulty(
            state["difficulty_level"], overall, state["difficulty_adjustments"]
        )

        # Send evaluation
        await websocket.send_json({
            "type": "evaluation",
            "event_type": "evaluation_complete",
            "question_number": state["questions_asked"],
            "evaluation": {
                "technical_accuracy": evaluation.get("technical_accuracy", 0),
                "completeness": evaluation.get("completeness", 0),
                "communication_quality": evaluation.get("communication_quality", 0),
                "problem_solving_approach": evaluation.get("problem_solving_approach", 0),
                "overall": overall,
                "feedback_summary": evaluation.get("feedback_summary", ""),
                "strengths": evaluation.get("strengths", []),
                "improvements": evaluation.get("improvements", []),
            },
        })

        # Send metrics update
        await websocket.send_json({
            "type": "metrics_update",
            "metrics": {
                "overall_score": round(state["current_score"], 2),
                "questions_answered": state["questions_asked"],
                "total_questions": state["total_questions_planned"],
                "progress_percent": round(state["questions_asked"] / state["total_questions_planned"] * 100),
            },
        })

    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        await websocket.send_json({
            "type": "evaluation_error",
            "message": "Evaluation temporarily unavailable. Proceeding to next question.",
        })


async def _send_completion(websocket: WebSocket, state: dict):
    """Send interview completion event."""
    scores = state.get("scores_history", [])
    final_score = state.get("current_score", 0)

    trend = "stable"
    if len(scores) >= 2:
        if scores[-1] > scores[0]:
            trend = "improving"
        elif scores[-1] < scores[0]:
            trend = "declining"

    await websocket.send_json({
        "type": "interview_complete",
        "final_report": {
            "overall_score": round(final_score, 2),
            "questions_answered": state["questions_asked"],
            "score_trend": trend,
            "score_history": [round(s, 1) for s in scores],
            "message": "Interview complete! Your learning plan will be generated.",
        },
    })
