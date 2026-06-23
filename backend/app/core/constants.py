"""System-wide constants."""

# Interview defaults
DEFAULT_QUESTIONS_PER_INTERVIEW = 5
MIN_QUESTIONS = 3
MAX_QUESTIONS = 10

# Difficulty adjustment thresholds
DIFFICULTY_INCREASE_THRESHOLD = 85  # score >= this → increase difficulty
DIFFICULTY_DECREASE_THRESHOLD = 60  # score < this → decrease difficulty
MAX_DIFFICULTY_ADJUSTMENTS = 3

# Scoring weights
SCORE_WEIGHTS = {
    "technical_accuracy": 0.35,
    "completeness": 0.25,
    "communication_quality": 0.20,
    "problem_solving_approach": 0.15,
    "confidence_level": 0.05,
}

# RAG settings
RAG_TOP_K = 5
RAG_SIMILARITY_THRESHOLD = 0.7
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

# Cache TTLs (seconds)
CACHE_TTL_RAG = 3600 * 24  # 24 hours
CACHE_TTL_USER_PROFILE = 300  # 5 minutes
CACHE_TTL_QUESTION = 3600  # 1 hour

# File upload limits
MAX_RESUME_SIZE_MB = 10
ALLOWED_RESUME_TYPES = ["application/pdf", "application/msword",
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Skill gap severity thresholds
GAP_SEVERITY_HIGH = 0.7
GAP_SEVERITY_MEDIUM = 0.4
