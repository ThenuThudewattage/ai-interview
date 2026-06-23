"""Models package - import all to register with SQLAlchemy metadata."""
from app.models.base import BaseModel
from app.models.user import User, UserProfile, UserPreferences
from app.models.interview import Interview, Question, InterviewQuestion
from app.models.answer import Answer
from app.models.evaluation import Evaluation
from app.models.skill import SkillArea, UserSkill, SkillAssessmentHistory, SkillGap
from app.models.learning_plan import LearningPlan, LearningMilestone, LearningResource
from app.models.document import Document, DocumentChunk, RAGSearchCache

__all__ = [
    "BaseModel",
    "User", "UserProfile", "UserPreferences",
    "Interview", "Question", "InterviewQuestion",
    "Answer",
    "Evaluation",
    "SkillArea", "UserSkill", "SkillAssessmentHistory", "SkillGap",
    "LearningPlan", "LearningMilestone", "LearningResource",
    "Document", "DocumentChunk", "RAGSearchCache",
]
