"""Interview Pydantic schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class StartInterviewRequest(BaseModel):
    interview_type: str  # system_design, algorithms, behavioral, coding, ml
    difficulty_level: str = "medium"
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    duration_minutes: int = 60
    total_questions: int = 5


class QuestionResponse(BaseModel):
    question_id: str
    content: str
    difficulty: str
    skill_areas: List[str]
    estimated_time_minutes: int
    followup_hints: List[str]


class StartInterviewResponse(BaseModel):
    interview_id: str
    session_id: str
    status: str
    interview_type: str
    difficulty_level: str
    started_at: str
    first_question: Optional[QuestionResponse]
    websocket_url: str


class SubmitAnswerRequest(BaseModel):
    answer_text: str
    time_spent_seconds: int = 0


class SubmitAnswerResponse(BaseModel):
    answer_id: str
    received_at: str
    evaluation_status: str
    message: str


class InterviewMetrics(BaseModel):
    overall_score: Optional[float]
    technical_score: Optional[float]
    communication_score: Optional[float]


class InterviewDetailResponse(BaseModel):
    interview_id: str
    user_id: str
    interview_type: str
    status: str
    difficulty_level: str
    started_at: Optional[str]
    completed_at: Optional[str]
    current_question_index: int
    total_questions_planned: int
    metrics: InterviewMetrics


class InterviewSummary(BaseModel):
    interview_id: str
    interview_type: str
    difficulty_level: str
    status: str
    overall_score: Optional[float]
    started_at: Optional[str]
    completed_at: Optional[str]


class InterviewListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    interviews: List[InterviewSummary]


class CompleteInterviewRequest(BaseModel):
    reason: str = "finished_all_questions"
    feedback: Optional[str] = None


class EvaluationScores(BaseModel):
    technical_accuracy: Optional[float]
    completeness: Optional[float]
    communication_quality: Optional[float]
    problem_solving_approach: Optional[float]
    confidence_level: Optional[float]
    overall_score: Optional[float]


class EvaluationFeedback(BaseModel):
    strengths: List[str]
    improvements: List[str]
    gaps_identified: List[str]
    feedback_summary: Optional[str]


class EvaluationResponse(BaseModel):
    evaluation_id: str
    answer_id: str
    scores: EvaluationScores
    feedback: EvaluationFeedback
    evaluator_confidence: Optional[float]
    evaluated_at: Optional[str]
