"""Core enumerations for the platform."""
from enum import Enum


class InterviewType(str, Enum):
    SYSTEM_DESIGN = "system_design"
    ALGORITHMS = "algorithms"
    BEHAVIORAL = "behavioral"
    CODING = "coding"
    ML = "ml"
    GENERAL = "general"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class InterviewStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class LearningPlanStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ARCHIVED = "archived"


class MilestoneStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ResourceType(str, Enum):
    ARTICLE = "article"
    VIDEO = "video"
    COURSE = "course"
    BOOK = "book"
    PRACTICE_SET = "practice_set"


class QuestionType(str, Enum):
    SYSTEM_DESIGN = "system_design"
    ALGORITHM = "algorithm"
    BEHAVIORAL = "behavioral"
    CODING = "coding"
    ML = "ml"
    GENERAL = "general"


class AgentName(str, Enum):
    INTERVIEW = "interview_agent"
    FEEDBACK = "feedback_agent"
    LEARNING = "learning_agent"
