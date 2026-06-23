"""Interview API endpoints."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.middleware.auth import get_current_user
from app.api.schemas.interview import (
    CompleteInterviewRequest,
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    InterviewListResponse,
    InterviewSummary,
    InterviewMetrics,
    InterviewDetailResponse,
    QuestionResponse,
)
from app.core.exceptions import AppException
from app.db.session import get_db
from app.models.user import User
from app.services.interview_service import InterviewService
from app.services.skill_service import SkillService

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("/start", response_model=StartInterviewResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    request: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new interview session."""
    try:
        svc = InterviewService(db)
        interview = await svc.create_interview(
            user_id=current_user.id,
            interview_type=request.interview_type,
            difficulty_level=request.difficulty_level,
            target_company=request.target_company,
            target_role=request.target_role,
            duration_minutes=request.duration_minutes,
            total_questions=request.total_questions,
        )

        # Get first question
        first_question_dict = await svc.get_next_question(
            interview_id=interview.id,
            interview_type=request.interview_type,
            difficulty=request.difficulty_level,
            used_question_ids=[],
        )

        first_q = None
        if first_question_dict:
            # Record the question
            iq = await svc.record_question(
                interview_id=interview.id,
                question_id=uuid.UUID(first_question_dict["id"]) if first_question_dict.get("id") else uuid.uuid4(),
                question_index=0,
            )
            first_q = QuestionResponse(
                question_id=first_question_dict.get("id", str(iq.id)),
                content=first_question_dict["content"],
                difficulty=first_question_dict.get("difficulty", request.difficulty_level),
                skill_areas=first_question_dict.get("skill_areas", []),
                estimated_time_minutes=first_question_dict.get("estimated_time_minutes", 45),
                followup_hints=first_question_dict.get("followup_hints", []),
            )

        return StartInterviewResponse(
            interview_id=str(interview.id),
            session_id=str(uuid.uuid4()),
            status="in_progress",
            interview_type=request.interview_type,
            difficulty_level=request.difficulty_level,
            started_at=interview.started_at.isoformat() if interview.started_at else datetime.now(timezone.utc).isoformat(),
            first_question=first_q,
            websocket_url=f"ws://localhost:8000/api/v1/interviews/{interview.id}/stream",
        )

    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=InterviewListResponse)
async def list_interviews(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's interviews."""
    svc = InterviewService(db)
    interviews, total = await svc.get_user_interviews(current_user.id, limit, offset)

    return InterviewListResponse(
        total=total,
        limit=limit,
        offset=offset,
        interviews=[
            InterviewSummary(
                interview_id=str(i.id),
                interview_type=i.interview_type,
                difficulty_level=i.difficulty_level,
                status=i.status,
                overall_score=float(i.overall_score) if i.overall_score else None,
                started_at=i.started_at.isoformat() if i.started_at else None,
                completed_at=i.completed_at.isoformat() if i.completed_at else None,
            )
            for i in interviews
        ],
    )


@router.get("/{interview_id}", response_model=InterviewDetailResponse)
async def get_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview details."""
    svc = InterviewService(db)
    interview = await svc.get_interview(interview_id)

    if str(interview.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    return InterviewDetailResponse(
        interview_id=str(interview.id),
        user_id=str(interview.user_id),
        interview_type=interview.interview_type,
        status=interview.status,
        difficulty_level=interview.difficulty_level,
        started_at=interview.started_at.isoformat() if interview.started_at else None,
        completed_at=interview.completed_at.isoformat() if interview.completed_at else None,
        current_question_index=interview.current_question_index,
        total_questions_planned=interview.total_questions_planned,
        metrics=InterviewMetrics(
            overall_score=float(interview.overall_score) if interview.overall_score else None,
            technical_score=float(interview.technical_score) if interview.technical_score else None,
            communication_score=float(interview.communication_score) if interview.communication_score else None,
        ),
    )


@router.post("/{interview_id}/answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    interview_id: uuid.UUID,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit answer to current interview question. Real-time evaluation via WebSocket."""
    svc = InterviewService(db)
    interview = await svc.get_interview(interview_id)

    if str(interview.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    if interview.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview is not in progress")

    # Get the current interview question
    from app.repositories.interview_repository import InterviewQuestionRepository
    iq_repo = InterviewQuestionRepository(db)
    questions = await iq_repo.get_interview_questions(interview_id)

    if not questions:
        raise HTTPException(status_code=400, detail="No questions found for this interview")

    current_iq = questions[interview.current_question_index] if interview.current_question_index < len(questions) else questions[-1]

    answer = await svc.submit_answer(
        interview_question_id=current_iq.id,
        answer_text=request.answer_text,
        time_spent_seconds=request.time_spent_seconds,
    )

    return SubmitAnswerResponse(
        answer_id=str(answer.id),
        received_at=answer.submitted_at.isoformat() if answer.submitted_at else datetime.now(timezone.utc).isoformat(),
        evaluation_status="processing",
        message="Answer received. Evaluation in progress via WebSocket.",
    )


@router.post("/{interview_id}/complete")
async def complete_interview(
    interview_id: uuid.UUID,
    request: CompleteInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete an interview session."""
    svc = InterviewService(db)
    interview = await svc.get_interview(interview_id)

    if str(interview.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    evaluations = await svc.get_interview_evaluations(interview_id)
    scores = [e["evaluation"].overall_score for e in evaluations if e.get("evaluation") and e["evaluation"].overall_score]
    overall = sum(float(s) for s in scores) / len(scores) if scores else 0
    tech = sum(float(e["evaluation"].technical_accuracy or 0) for e in evaluations if e.get("evaluation")) / len(evaluations) if evaluations else 0
    comm = sum(float(e["evaluation"].communication_quality or 0) for e in evaluations if e.get("evaluation")) / len(evaluations) if evaluations else 0

    await svc.complete_interview(interview_id, overall, tech, comm)

    return {
        "interview_id": str(interview_id),
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "final_scores": {
            "overall_score": round(overall, 2),
            "technical_score": round(tech, 2),
            "communication_score": round(comm, 2),
        },
    }
