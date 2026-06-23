"""Learning Pydantic schemas."""
from typing import List, Optional
from pydantic import BaseModel


class GenerateLearningPlanRequest(BaseModel):
    based_on_interview_id: Optional[str] = None
    target_proficiency: float = 80.0
    available_hours_per_week: int = 10
    learning_pace: str = "medium"
    interview_type: Optional[str] = None


class ResourceResponse(BaseModel):
    resource_id: Optional[str]
    title: str
    description: Optional[str]
    resource_type: Optional[str]
    url: Optional[str]
    estimated_time_minutes: Optional[int]
    proficiency_level: Optional[str]


class MilestoneResponse(BaseModel):
    milestone_id: str
    name: Optional[str]
    description: Optional[str]
    sequence_number: Optional[int]
    target_score: Optional[float]
    status: str
    resources: List[ResourceResponse]


class LearningPlanResponse(BaseModel):
    learning_plan_id: str
    user_id: str
    title: Optional[str]
    description: Optional[str]
    status: str
    target_proficiency_score: float
    target_completion_date: Optional[str]
    estimated_hours_total: Optional[int]
    milestones: List[MilestoneResponse]
    created_at: str


class SkillGapResponse(BaseModel):
    gap_id: str
    skill: str
    gap_severity: Optional[float]
    is_resolved: bool
    identified_at: Optional[str]


class SkillGapListResponse(BaseModel):
    total_gaps: int
    skill_gaps: List[SkillGapResponse]


class ResourceCompletionRequest(BaseModel):
    resource_id: str
    completion_percentage: int = 100
    notes: Optional[str] = None
