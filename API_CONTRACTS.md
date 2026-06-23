# API Contracts & Integration Specifications

## Overview

This document defines all API endpoints, request/response contracts, and integration points for the AI Interview Intelligence Platform.

---

## 1. Authentication & Authorization

### 1.1 Authentication Endpoints

#### POST /api/v1/auth/register

Register a new user account.

**Request**:
```json
{
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe",
    "username": "johndoe"
}
```

**Response** (201 Created):
```json
{
    "user_id": "user_123",
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "created_at": "2026-06-17T10:00:00Z",
    "verification_email_sent": true
}
```

**Errors**:
- `400 Bad Request`: Invalid email format, weak password
- `409 Conflict`: Email already exists

---

#### POST /api/v1/auth/login

Authenticate user and return JWT tokens.

**Request**:
```json
{
    "email": "john@example.com",
    "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
        "user_id": "user_123",
        "email": "john@example.com",
        "username": "johndoe"
    }
}
```

**Errors**:
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Missing required fields

---

#### POST /api/v1/auth/refresh

Refresh access token using refresh token.

**Request**:
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
}
```

---

## 2. User Management API

### 2.1 User Profile Endpoints

#### GET /api/v1/users/profile

Get current user's profile.

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
    "user_id": "user_123",
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "profile_picture_url": "https://...",
    "bio": "Software engineer interested in system design",
    "preferences": {
        "preferred_difficulty": "hard",
        "preferred_interview_duration_minutes": 60,
        "timezone": "America/New_York",
        "language": "en"
    },
    "skills_summary": {
        "total_skills": 12,
        "average_proficiency": 72,
        "top_skills": ["system_design", "algorithms", "distributed_systems"]
    },
    "interview_stats": {
        "total_interviews": 25,
        "completed_interviews": 24,
        "average_score": 76.5
    },
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-06-17T10:00:00Z"
}
```

---

#### PUT /api/v1/users/profile

Update user profile.

**Request**:
```json
{
    "full_name": "John Doe",
    "bio": "Senior Software Engineer",
    "preferences": {
        "preferred_difficulty": "expert",
        "timezone": "UTC"
    }
}
```

**Response** (200 OK):
```json
{
    "user_id": "user_123",
    "updated_fields": ["full_name", "bio", "preferences"],
    "updated_at": "2026-06-17T10:05:00Z"
}
```

---

#### POST /api/v1/users/profile/resume

Upload user's resume.

**Request**:
```
Content-Type: multipart/form-data
Authorization: Bearer <access_token>

[Binary PDF/DOCX file]
```

**Response** (200 OK):
```json
{
    "resume_id": "resume_123",
    "resume_url": "https://storage.example.com/resume_123.pdf",
    "parsed_data": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-1234",
        "experience": [
            {
                "company": "TechCorp",
                "position": "Senior Software Engineer",
                "duration": "3 years"
            }
        ],
        "skills": ["Python", "Java", "Kubernetes", "PostgreSQL"],
        "education": [
            {
                "school": "University of Example",
                "degree": "B.S. Computer Science"
            }
        ]
    },
    "extraction_confidence": 0.95,
    "upload_time": "2026-06-17T10:05:00Z"
}
```

**Errors**:
- `400 Bad Request`: Invalid file format
- `413 Payload Too Large`: File exceeds 10MB

---

#### POST /api/v1/users/job-description/analyze

Analyze job description to identify required skills.

**Request**:
```json
{
    "job_description": "We are looking for a Senior Software Engineer with experience in distributed systems, system design, and cloud infrastructure...",
    "company": "Google",
    "position": "Senior Software Engineer"
}
```

**Response** (200 OK):
```json
{
    "analysis_id": "jd_analysis_123",
    "company": "Google",
    "position": "Senior Software Engineer",
    "required_skills": [
        {
            "skill": "system_design",
            "proficiency_required": "expert",
            "importance": "high"
        },
        {
            "skill": "distributed_systems",
            "proficiency_required": "advanced",
            "importance": "high"
        },
        {
            "skill": "cloud_platforms",
            "proficiency_required": "intermediate",
            "importance": "medium"
        }
    ],
    "recommended_interview_topics": [
        "designing_microservices",
        "database_scaling",
        "kubernetes_deployment"
    ],
    "analysis_confidence": 0.92
}
```

---

## 3. Interview API

### 3.1 Interview Session Endpoints

#### POST /api/v1/interviews/start

Start a new interview session.

**Request**:
```json
{
    "interview_type": "system_design",
    "difficulty_level": "hard",
    "target_company": "Google",
    "target_role": "Senior Software Engineer",
    "duration_minutes": 60
}
```

**Response** (201 Created):
```json
{
    "interview_id": "int_456",
    "session_id": "sess_abc123",
    "user_id": "user_123",
    "status": "initializing",
    "interview_type": "system_design",
    "difficulty_level": "hard",
    "started_at": "2026-06-17T10:05:00Z",
    "estimated_completion_time": "2026-06-17T11:05:00Z",
    "first_question": {
        "question_id": "q_101",
        "content": "Design a URL shortener service like bit.ly...",
        "difficulty": "hard",
        "estimated_time_minutes": 45,
        "followup_hints": ["Consider scalability requirements", "Discuss trade-offs"]
    },
    "websocket_url": "wss://api.example.com/interviews/sess_abc123/stream"
}
```

---

#### POST /api/v1/interviews/{interview_id}/answer

Submit answer to interview question.

**Request**:
```json
{
    "answer_text": "To design a URL shortener, I would...",
    "time_spent_seconds": 600
}
```

**Response** (200 OK):
```json
{
    "answer_id": "ans_789",
    "received_at": "2026-06-17T10:15:00Z",
    "evaluation_status": "processing",
    "evaluation_id": "eval_123",
    "estimated_evaluation_time_seconds": 15
}
```

**Note**: Real-time evaluation results are streamed via WebSocket.

---

#### GET /api/v1/interviews/{interview_id}

Get interview details and current state.

**Response** (200 OK):
```json
{
    "interview_id": "int_456",
    "user_id": "user_123",
    "interview_type": "system_design",
    "status": "in_progress",
    "difficulty_level": "hard",
    "started_at": "2026-06-17T10:05:00Z",
    "current_question_index": 2,
    "total_questions_planned": 5,
    "current_question": {
        "question_id": "q_102",
        "content": "...",
        "difficulty": "hard"
    },
    "metrics": {
        "overall_score": 76.5,
        "technical_score": 75.2,
        "communication_score": 78.0,
        "current_difficulty_adjusted": "hard",
        "average_response_time_seconds": 580
    },
    "elapsed_time_seconds": 1200
}
```

---

#### POST /api/v1/interviews/{interview_id}/complete

Complete an interview session.

**Request**:
```json
{
    "reason": "finished_all_questions",
    "feedback": "Great session"
}
```

**Response** (200 OK):
```json
{
    "interview_id": "int_456",
    "status": "completed",
    "completed_at": "2026-06-17T11:05:00Z",
    "total_duration_seconds": 3600,
    "questions_answered": 5,
    "final_scores": {
        "overall_score": 77.6,
        "technical_score": 76.2,
        "communication_score": 79.0
    },
    "summary_report": {
        "strengths": ["Good problem decomposition", "Clear communication"],
        "improvements": ["Could discuss edge cases more"],
        "skill_gaps_identified": [
            {
                "skill": "distributed_systems",
                "severity": "medium"
            }
        ]
    },
    "next_steps": "Review distributed systems concepts"
}
```

---

#### GET /api/v1/interviews?limit=20&offset=0

List user's interviews with pagination.

**Response** (200 OK):
```json
{
    "total": 25,
    "limit": 20,
    "offset": 0,
    "interviews": [
        {
            "interview_id": "int_456",
            "interview_type": "system_design",
            "difficulty_level": "hard",
            "status": "completed",
            "overall_score": 77.6,
            "completed_at": "2026-06-17T11:05:00Z",
            "duration_minutes": 60
        }
    ]
}
```

---

### 3.2 WebSocket API (Real-time Interview Stream)

#### WS /api/v1/interviews/{session_id}/stream

Real-time interview event stream.

**Message Types**:

**1. Question Event**:
```json
{
    "type": "question",
    "event_type": "question_presented",
    "question": {
        "question_id": "q_101",
        "content": "Design a URL shortener...",
        "difficulty": "hard",
        "followup_hints": ["Consider scalability"]
    },
    "timestamp": "2026-06-17T10:05:00Z"
}
```

**2. Evaluation Event** (streamed during answer processing):
```json
{
    "type": "evaluation",
    "event_type": "evaluation_complete",
    "evaluation": {
        "technical_accuracy": 78,
        "communication": 82,
        "problem_solving": 75,
        "overall": 78,
        "feedback": "Good approach, but missing some edge cases"
    },
    "timestamp": "2026-06-17T10:15:00Z"
}
```

**3. Difficulty Adjustment Event**:
```json
{
    "type": "difficulty_adjustment",
    "new_difficulty": "expert",
    "reason": "Answered correctly, increasing difficulty",
    "next_question_preview": "..."
}
```

**4. Metrics Update Event**:
```json
{
    "type": "metrics_update",
    "metrics": {
        "overall_score": 78.5,
        "technical_score": 77.2,
        "communication_score": 79.8
    }
}
```

**5. Error Event**:
```json
{
    "type": "error",
    "error_code": "EVALUATION_FAILED",
    "message": "Failed to evaluate answer. Please try again.",
    "can_retry": true
}
```

---

## 4. Evaluation API

### 4.1 Evaluation Endpoints

#### GET /api/v1/evaluations/{evaluation_id}

Get detailed evaluation results.

**Response** (200 OK):
```json
{
    "evaluation_id": "eval_123",
    "answer_id": "ans_789",
    "question_id": "q_101",
    "evaluated_at": "2026-06-17T10:15:00Z",
    "scores": {
        "technical_accuracy": {
            "score": 78,
            "max_score": 100,
            "rubric_items": [
                {
                    "criterion": "Correctness",
                    "weight": 0.4,
                    "score": 80
                },
                {
                    "criterion": "Completeness",
                    "weight": 0.3,
                    "score": 75
                }
            ]
        },
        "communication_quality": {
            "score": 82,
            "breakdown": {...}
        },
        "problem_solving": {
            "score": 75,
            "breakdown": {...}
        },
        "confidence_level": {
            "score": 80
        },
        "overall_composite": 78
    },
    "feedback": {
        "strengths": [
            "Clear system decomposition",
            "Discussed scalability considerations"
        ],
        "improvements": [
            "Could have discussed consistency models",
            "Missing mention of fault tolerance"
        ],
        "gaps_identified": [
            {
                "skill": "distributed_systems",
                "severity": "high",
                "suggestion": "Review consensus algorithms"
            }
        ]
    },
    "evaluator_confidence": 0.92,
    "rubric_version": "1.0",
    "evaluation_model": "gemini-flash"
}
```

---

#### GET /api/v1/interviews/{interview_id}/evaluations

Get all evaluations for an interview.

**Response** (200 OK):
```json
{
    "interview_id": "int_456",
    "total_evaluations": 5,
    "evaluations": [
        {
            "question_index": 1,
            "question_id": "q_101",
            "overall_score": 78,
            "evaluated_at": "2026-06-17T10:15:00Z"
        }
    ],
    "interview_summary": {
        "average_score": 77.6,
        "score_trend": "improving",
        "key_strengths": [...],
        "key_improvements": [...]
    }
}
```

---

## 5. Learning API

### 5.1 Learning Plan Endpoints

#### POST /api/v1/learning-plans/generate

Generate personalized learning plan based on assessment.

**Request**:
```json
{
    "based_on_interview_id": "int_456",
    "target_proficiency": 85,
    "available_hours_per_week": 10,
    "learning_pace": "medium"
}
```

**Response** (201 Created):
```json
{
    "learning_plan_id": "plan_789",
    "user_id": "user_123",
    "title": "System Design Mastery Plan",
    "description": "Focus on distributed systems and scalability patterns",
    "target_proficiency": 85,
    "target_completion_date": "2026-09-17",
    "estimated_total_hours": 40,
    "milestones": [
        {
            "milestone_id": "mile_1",
            "name": "Distributed Systems Fundamentals",
            "sequence": 1,
            "target_score": 70,
            "estimated_days": 14,
            "resources": [
                {
                    "title": "Designing Data-Intensive Applications",
                    "type": "book",
                    "url": "https://...",
                    "estimated_time_minutes": 1800,
                    "proficiency_level": "intermediate"
                }
            ]
        }
    ],
    "created_at": "2026-06-17T10:05:00Z"
}
```

---

#### GET /api/v1/learning-plans/{plan_id}

Get learning plan details and progress.

**Response** (200 OK):
```json
{
    "learning_plan_id": "plan_789",
    "status": "in_progress",
    "progress_percentage": 35,
    "milestones": [
        {
            "milestone_id": "mile_1",
            "name": "Distributed Systems Fundamentals",
            "status": "in_progress",
            "completion_percentage": 60,
            "resources": [
                {
                    "resource_id": "res_1",
                    "title": "Designing Data-Intensive Applications",
                    "type": "book",
                    "status": "in_progress",
                    "completion_percentage": 40,
                    "started_at": "2026-06-10T10:00:00Z"
                }
            ]
        }
    ],
    "skill_gaps": [
        {
            "skill": "distributed_systems",
            "current_score": 45,
            "target_score": 85,
            "improvement_needed": 40,
            "estimated_days_to_target": 30
        }
    ]
}
```

---

#### POST /api/v1/learning-plans/{plan_id}/resource-completion

Mark a learning resource as completed.

**Request**:
```json
{
    "resource_id": "res_1",
    "completion_percentage": 100,
    "notes": "Completed book, understood concepts"
}
```

**Response** (200 OK):
```json
{
    "resource_id": "res_1",
    "completed_at": "2026-06-17T10:05:00Z",
    "milestone_progress": 45,
    "plan_progress": 32
}
```

---

#### GET /api/v1/users/skill-gaps

Get identified skill gaps for user.

**Response** (200 OK):
```json
{
    "total_gaps": 5,
    "skill_gaps": [
        {
            "gap_id": "gap_123",
            "skill": "distributed_systems",
            "current_score": 45,
            "gap_severity": 0.85,
            "identified_from_interview": "int_456",
            "recommended_resources": [
                {
                    "title": "Distributed Systems Course",
                    "type": "course",
                    "url": "https://..."
                }
            ],
            "identified_at": "2026-06-17T10:00:00Z"
        }
    ]
}
```

---

## 6. Knowledge Base API

### 6.1 Search Endpoints

#### GET /api/v1/knowledge-base/search

Search knowledge base for questions and resources.

**Query Parameters**:
- `query` (string): Search query
- `skill_area` (string): Filter by skill (system_design, algorithms, etc.)
- `difficulty` (string): Filter by difficulty (easy, medium, hard, expert)
- `limit` (integer): Results limit (default: 5, max: 50)

**Request**:
```
GET /api/v1/knowledge-base/search?query=cache+design&skill_area=system_design&difficulty=hard&limit=5
```

**Response** (200 OK):
```json
{
    "query": "cache design",
    "filters": {
        "skill_area": "system_design",
        "difficulty": "hard"
    },
    "total_results": 24,
    "results": [
        {
            "type": "question",
            "question_id": "q_123",
            "title": "Design a distributed cache",
            "content_preview": "Design a scalable distributed caching system...",
            "difficulty": "hard",
            "skill_areas": ["system_design", "distributed_systems"],
            "relevance_score": 0.98,
            "source": "leetcode_premium"
        },
        {
            "type": "resource",
            "resource_id": "res_456",
            "title": "Caching Patterns and Strategies",
            "type": "article",
            "url": "https://...",
            "estimated_read_time": 15,
            "relevance_score": 0.92
        }
    ]
}
```

---

## 7. Analytics API

### 7.1 User Analytics Endpoints

#### GET /api/v1/analytics/dashboard

Get user analytics dashboard.

**Response** (200 OK):
```json
{
    "user_id": "user_123",
    "interview_stats": {
        "total_interviews": 25,
        "completed_interviews": 24,
        "average_score": 76.5,
        "interviews_this_month": 8
    },
    "skill_progression": {
        "total_skills_tracked": 12,
        "average_proficiency": 72,
        "skills_improved_last_30_days": 4,
        "overall_trend": "improving",
        "trend_percentage": 5.2
    },
    "top_performing_skills": [
        {
            "skill": "algorithms",
            "proficiency": 85,
            "interviews_count": 8
        }
    ],
    "weak_skills": [
        {
            "skill": "machine_learning",
            "proficiency": 45,
            "recommended_action": "Complete ML fundamentals course"
        }
    ],
    "learning_progress": {
        "active_learning_plans": 2,
        "total_hours_spent": 24,
        "average_hours_per_week": 6
    },
    "engagement": {
        "days_active_30": 18,
        "days_active_90": 65,
        "streak_current": 7
    }
}
```

---

#### GET /api/v1/analytics/skill-progression

Get skill progression over time.

**Query Parameters**:
- `skill_area` (string, required): Skill to track
- `period` (string): Time period (7d, 30d, 90d, 1y, all)

**Response** (200 OK):
```json
{
    "skill_area": "system_design",
    "period": "90d",
    "data_points": [
        {
            "date": "2026-03-17",
            "score": 62,
            "assessment_count": 1
        },
        {
            "date": "2026-04-14",
            "score": 68,
            "assessment_count": 3
        },
        {
            "date": "2026-06-17",
            "score": 76,
            "assessment_count": 12
        }
    ],
    "trend": {
        "direction": "up",
        "improvement_percentage": 22.6,
        "average_improvement_per_week": 1.6
    }
}
```

---

## 8. Error Handling

All APIs follow a consistent error response format:

```json
{
    "error": {
        "code": "INVALID_REQUEST",
        "message": "Missing required field: interview_type",
        "details": {
            "field": "interview_type",
            "reason": "required"
        },
        "request_id": "req_123abc",
        "timestamp": "2026-06-17T10:05:00Z"
    }
}
```

**Common Error Codes**:
- `INVALID_REQUEST` (400): Malformed request
- `UNAUTHORIZED` (401): Missing/invalid authentication
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `CONFLICT` (409): Resource conflict (e.g., duplicate email)
- `RATE_LIMITED` (429): Rate limit exceeded
- `INTERNAL_SERVER_ERROR` (500): Server error
- `SERVICE_UNAVAILABLE` (503): Service unavailable (LLM API down)

---

## 9. Rate Limiting

Rate limits apply per user:

```
GET /api/v1/knowledge-base/search: 100 requests/minute
POST /api/v1/interviews/start: 10 requests/hour
POST /api/v1/interviews/{id}/answer: Unlimited (per active interview)
GET /api/v1/analytics/*: 50 requests/minute
```

Rate limit headers in response:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1623925500
```

---

## 10. Pagination

List endpoints support pagination:

**Query Parameters**:
- `limit` (integer): Items per page (default: 20, max: 100)
- `offset` (integer): Number of items to skip (default: 0)

**Response**:
```json
{
    "total": 150,
    "limit": 20,
    "offset": 0,
    "items": [...]
}
```

---

## 11. Versioning

API uses URL-based versioning:
- `/api/v1/` - Current version
- `/api/v2/` - Future major version (backward incompatible changes)

Deprecation notices are provided via response headers:
```
Deprecation: true
Sunset: Wed, 21 Dec 2027 23:59:59 GMT
```

---

## 12. Documentation

Interactive API documentation available at:
- **Swagger UI**: `https://api.example.com/docs`
- **ReDoc**: `https://api.example.com/redoc`
- **OpenAPI Schema**: `https://api.example.com/openapi.json`
