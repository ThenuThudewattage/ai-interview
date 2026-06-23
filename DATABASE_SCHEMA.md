# Database Schema Design

## Overview

This document details the complete database schema for the AI Interview Intelligence Platform, designed with normalization (3NF) for data integrity, ACID compliance, and query efficiency.

---

## 1. Core Tables

### 1.1 Users Domain

```sql
-- Users table: Core user information
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    profile_picture_url TEXT,
    bio TEXT,
    
    -- User preferences
    preferred_difficulty VARCHAR(50) DEFAULT 'medium',
    preferred_interview_duration_minutes INTEGER DEFAULT 60,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(50) DEFAULT 'en',
    
    -- Account status
    account_status VARCHAR(50) DEFAULT 'active', -- active, inactive, suspended
    email_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_difficulty CHECK (preferred_difficulty IN ('easy', 'medium', 'hard', 'expert')),
    CONSTRAINT valid_status CHECK (account_status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- User preferences: Extended preferences
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Interview preferences
    preferred_skill_areas TEXT[], -- Array of skill areas
    preferred_question_types TEXT[], -- Array of question types
    preferred_companies TEXT[], -- Array of company names
    
    -- Learning preferences
    learning_pace VARCHAR(50) DEFAULT 'medium', -- slow, medium, fast
    preferred_resources TEXT[], -- Array of resource types
    
    -- Notification settings
    email_notifications_enabled BOOLEAN DEFAULT TRUE,
    interview_reminders_enabled BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

-- User profiles: Resume and job information
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Resume information
    resume_url TEXT,
    resume_text TEXT,
    resume_parsed_json JSONB,
    
    -- Experience
    years_of_experience INTEGER,
    current_job_title VARCHAR(255),
    current_company VARCHAR(255),
    
    -- Target information
    target_position VARCHAR(255),
    target_companies TEXT[],
    target_salary_min INTEGER,
    target_salary_max INTEGER,
    
    -- Skills summary
    top_skills TEXT[],
    programming_languages TEXT[],
    frameworks TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);
```

### 1.2 Interviews Domain

```sql
-- Interviews: Interview sessions
CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session metadata
    title VARCHAR(255),
    description TEXT,
    status VARCHAR(50) DEFAULT 'in_progress', -- in_progress, completed, paused
    
    -- Interview configuration
    interview_type VARCHAR(50) NOT NULL, -- system_design, algorithms, behavioral, ml
    difficulty_level VARCHAR(50) DEFAULT 'medium', -- easy, medium, hard, expert
    target_company VARCHAR(255),
    target_role VARCHAR(255),
    
    -- Timing
    duration_minutes INTEGER,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    paused_at TIMESTAMP WITH TIME ZONE,
    
    -- Session state
    current_question_index INTEGER DEFAULT 0,
    total_questions_planned INTEGER DEFAULT 5,
    
    -- Overall metrics
    overall_score DECIMAL(5, 2), -- 0-100
    technical_score DECIMAL(5, 2),
    communication_score DECIMAL(5, 2),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb, -- Interview-specific metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_type CHECK (interview_type IN ('system_design', 'algorithms', 'behavioral', 'ml', 'general')),
    CONSTRAINT valid_status CHECK (status IN ('in_progress', 'completed', 'paused')),
    CONSTRAINT valid_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard', 'expert'))
);

CREATE INDEX idx_interviews_user_id ON interviews(user_id);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_started_at ON interviews(started_at);
CREATE INDEX idx_interviews_completed_at ON interviews(completed_at);

-- Questions: Interview questions
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Question metadata
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL, -- system_design, algorithm, behavioral, coding, ml
    skill_areas TEXT[] NOT NULL, -- [system_design, scalability, databases]
    
    -- Difficulty and complexity
    difficulty_level VARCHAR(50) NOT NULL, -- easy, medium, hard, expert
    estimated_time_minutes INTEGER DEFAULT 45,
    
    -- Expected solution
    expected_answer_summary TEXT,
    expected_answer_detailed TEXT,
    expected_answer_embedding vector(384),
    key_points TEXT[],
    
    -- Follow-up hints
    followup_hints TEXT[],
    common_mistakes TEXT[],
    
    -- Source and metadata
    source VARCHAR(255), -- leetcode, leetcode_hard, custom, company_specific
    company_filters TEXT[], -- Specific companies (optional)
    frequency_count INTEGER DEFAULT 1, -- How often this appears in interviews
    
    -- Vector for similarity search
    content_embedding vector(384),
    
    -- Version control
    version INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_type CHECK (question_type IN ('system_design', 'algorithm', 'behavioral', 'coding', 'ml', 'general')),
    CONSTRAINT valid_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard', 'expert'))
);

CREATE INDEX idx_questions_type ON questions(question_type);
CREATE INDEX idx_questions_difficulty ON questions(difficulty_level);
CREATE INDEX idx_questions_skill_areas ON questions USING GIN(skill_areas);
CREATE INDEX idx_questions_embedding ON questions USING ivfflat(content_embedding vector_cosine_ops);
CREATE INDEX idx_questions_is_latest ON questions(is_latest);

-- Interview Questions: Junction table for questions used in specific interviews
CREATE TABLE interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    
    -- Position in interview
    question_index INTEGER NOT NULL,
    asked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Question-specific metadata
    actual_difficulty_adjusted VARCHAR(50), -- May differ from question.difficulty_level
    time_spent_seconds INTEGER,
    
    -- Follow-ups
    followup_questions_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(interview_id, question_index)
);

CREATE INDEX idx_interview_questions_interview_id ON interview_questions(interview_id);
CREATE INDEX idx_interview_questions_question_id ON interview_questions(question_id);
```

### 1.3 Answers Domain

```sql
-- Answers: User answers to questions
CREATE TABLE answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_question_id UUID NOT NULL REFERENCES interview_questions(id) ON DELETE CASCADE,
    
    -- Answer content
    answer_text TEXT NOT NULL,
    answer_language VARCHAR(50), -- For coding answers
    answer_code TEXT, -- For coding questions
    
    -- Submission metadata
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    character_count INTEGER,
    word_count INTEGER,
    
    -- For follow-ups
    is_followup_answer BOOLEAN DEFAULT FALSE,
    followup_question_index INTEGER,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_answers_interview_question_id ON answers(interview_question_id);
CREATE INDEX idx_answers_submitted_at ON answers(submitted_at);
```

### 1.4 Evaluations Domain

```sql
-- Evaluations: Answer evaluations
CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_id UUID NOT NULL REFERENCES answers(id) ON DELETE CASCADE,
    
    -- Evaluator information
    evaluator_model VARCHAR(255) NOT NULL, -- gemini-flash, gpt-4, ollama-mistral
    evaluation_version INTEGER DEFAULT 1,
    
    -- Evaluation scores
    technical_accuracy DECIMAL(5, 2), -- 0-100
    completeness DECIMAL(5, 2), -- 0-100
    communication_quality DECIMAL(5, 2), -- 0-100
    problem_solving_approach DECIMAL(5, 2), -- 0-100
    confidence_level DECIMAL(5, 2), -- 0-100
    overall_score DECIMAL(5, 2), -- 0-100
    
    -- Rubric information
    rubric_version VARCHAR(50),
    rubric_type VARCHAR(50), -- system_design, algorithm, behavioral, coding
    
    -- Feedback
    strengths TEXT[],
    improvements TEXT[],
    key_gaps_identified TEXT[],
    feedback_summary TEXT,
    detailed_feedback TEXT,
    
    -- Confidence in evaluation
    evaluator_confidence DECIMAL(5, 2), -- 0-1 (0-100%)
    
    -- LLM metadata
    llm_prompt_tokens INTEGER,
    llm_completion_tokens INTEGER,
    llm_total_tokens INTEGER,
    llm_cost_usd DECIMAL(10, 6),
    
    -- Evaluation timing
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evaluations_answer_id ON evaluations(answer_id);
CREATE INDEX idx_evaluations_evaluated_at ON evaluations(evaluated_at);
```

---

## 2. Skill Tracking Domain

```sql
-- Skill Areas: Available skills in the system
CREATE TABLE skill_areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL, -- system_design, algorithms, etc.
    description TEXT,
    category VARCHAR(100), -- fundamentals, advanced, specialized
    parent_skill_id UUID REFERENCES skill_areas(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Skills: Track user proficiency in each skill
CREATE TABLE user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_area_id UUID NOT NULL REFERENCES skill_areas(id) ON DELETE CASCADE,
    
    -- Proficiency tracking
    proficiency_score DECIMAL(5, 2) DEFAULT 50, -- 0-100
    confidence_score DECIMAL(5, 2) DEFAULT 50, -- 0-100
    
    -- Assessment count
    assessment_count INTEGER DEFAULT 0,
    last_assessment_date TIMESTAMP WITH TIME ZONE,
    
    -- Trend tracking
    score_trend DECIMAL(5, 2), -- Month-over-month change
    velocity DECIMAL(5, 2), -- Improvement rate (points/week)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, skill_area_id)
);

CREATE INDEX idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX idx_user_skills_proficiency ON user_skills(proficiency_score DESC);

-- Skill Assessment History: Track how skills improve over time
CREATE TABLE skill_assessment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id UUID NOT NULL REFERENCES user_skills(id) ON DELETE CASCADE,
    
    -- Historical scores
    proficiency_score DECIMAL(5, 2),
    confidence_score DECIMAL(5, 2),
    
    -- Assessment context
    assessment_source VARCHAR(100), -- interview, quiz, assessment
    related_interview_id UUID REFERENCES interviews(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skill_history_user_skill_id ON skill_assessment_history(user_skill_id);
CREATE INDEX idx_skill_history_created_at ON skill_assessment_history(created_at DESC);
```

---

## 3. Learning Domain

```sql
-- Learning Plans: Personalized learning roadmaps
CREATE TABLE learning_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Plan metadata
    title VARCHAR(255),
    description TEXT,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, paused, archived
    
    -- Target and timeline
    target_proficiency_score DECIMAL(5, 2) DEFAULT 80, -- 0-100
    target_completion_date TIMESTAMP WITH TIME ZONE,
    estimated_hours_total INTEGER,
    estimated_hours_spent INTEGER DEFAULT 0,
    
    -- Focus areas
    focus_skill_areas TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_learning_plans_user_id ON learning_plans(user_id);
CREATE INDEX idx_learning_plans_status ON learning_plans(status);

-- Learning Milestones: Phases in a learning plan
CREATE TABLE learning_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learning_plan_id UUID NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
    
    -- Milestone details
    name VARCHAR(255),
    description TEXT,
    sequence_number INTEGER,
    
    -- Target
    target_score DECIMAL(5, 2),
    target_date TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Learning Resources: Recommended materials
CREATE TABLE learning_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learning_milestone_id UUID NOT NULL REFERENCES learning_milestones(id) ON DELETE CASCADE,
    
    -- Resource details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    resource_type VARCHAR(50), -- article, video, course, book, practice_set
    url TEXT,
    
    -- Metadata
    source VARCHAR(255), -- coursera, udemy, leetcode, etc.
    estimated_time_minutes INTEGER,
    proficiency_level VARCHAR(50), -- beginner, intermediate, advanced
    
    -- Quality metrics
    rating DECIMAL(3, 2), -- 1-5
    review_count INTEGER DEFAULT 0,
    relevance_score DECIMAL(3, 2), -- 0-1
    
    -- Status
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skill Gaps: Identified areas needing improvement
CREATE TABLE skill_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_area_id UUID NOT NULL REFERENCES skill_areas(id) ON DELETE CASCADE,
    
    -- Gap details
    gap_severity DECIMAL(5, 2), -- 0-1 (0-100%)
    related_interview_id UUID REFERENCES interviews(id),
    identified_by_agent VARCHAR(100), -- feedback_agent, learning_agent, system
    
    -- Resolution
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    identified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skill_gaps_user_id ON skill_gaps(user_id);
CREATE INDEX idx_skill_gaps_is_resolved ON skill_gaps(is_resolved);
```

---

## 4. Knowledge Base Domain

```sql
-- Documents: Knowledge base source documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Document metadata
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    document_type VARCHAR(50), -- question, example, resource, guide
    
    -- Source information
    source VARCHAR(255),
    source_url TEXT,
    author VARCHAR(255),
    
    -- Categorization
    skill_areas TEXT[],
    topics TEXT[],
    tags TEXT[],
    
    -- Dates
    published_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document Chunks: Chunked content for RAG
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Chunk content
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER,
    
    -- Embeddings
    embedding vector(384),
    
    -- Metadata
    chunk_metadata JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat(embedding vector_cosine_ops);

-- RAG Search Cache: Cache RAG search results
CREATE TABLE rag_search_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Query information
    query_text VARCHAR(500) NOT NULL,
    query_hash VARCHAR(64) NOT NULL UNIQUE,
    query_embedding vector(384),
    
    -- Results
    retrieved_chunks TEXT[], -- Array of chunk IDs
    retrieval_score DECIMAL(5, 2), -- Quality of retrieval
    
    -- Usage tracking
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '7 days'
);

CREATE INDEX idx_rag_search_query_hash ON rag_search_cache(query_hash);
CREATE INDEX idx_rag_search_expires_at ON rag_search_cache(expires_at);
```

---

## 5. Analytics Domain

```sql
-- Interview Metrics: Aggregated metrics for analysis
CREATE TABLE interview_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    
    -- Computed metrics
    questions_answered DECIMAL(5, 2), -- 0-100%
    average_question_score DECIMAL(5, 2),
    technical_accuracy_avg DECIMAL(5, 2),
    communication_quality_avg DECIMAL(5, 2),
    
    -- Timing metrics
    average_response_time_seconds INTEGER,
    total_duration_seconds INTEGER,
    
    -- Difficulty progression
    initial_difficulty VARCHAR(50),
    final_difficulty VARCHAR(50),
    difficulty_adjustments_count INTEGER,
    
    -- Engagement metrics
    followup_questions_count INTEGER,
    hints_requested_count INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Analytics: User-level aggregated statistics
CREATE TABLE user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Interview counts
    total_interviews INTEGER DEFAULT 0,
    completed_interviews INTEGER DEFAULT 0,
    average_interview_score DECIMAL(5, 2),
    
    -- Skill progression
    skills_improved INTEGER DEFAULT 0,
    average_skill_score DECIMAL(5, 2),
    
    -- Learning metrics
    learning_plans_created INTEGER DEFAULT 0,
    learning_plans_completed INTEGER DEFAULT 0,
    total_hours_spent_learning INTEGER DEFAULT 0,
    
    -- Trends
    score_trend_30_days DECIMAL(5, 2), -- Change in last 30 days
    score_trend_90_days DECIMAL(5, 2),
    
    -- Engagement
    days_active_30 INTEGER,
    days_active_90 INTEGER,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_analytics_user_id ON user_analytics(user_id);

-- Daily Activity Log: Track daily usage
CREATE TABLE daily_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Date
    activity_date DATE NOT NULL,
    
    -- Activity metrics
    interviews_conducted INTEGER DEFAULT 0,
    answers_submitted INTEGER DEFAULT 0,
    learning_resources_viewed INTEGER DEFAULT 0,
    minutes_spent INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, activity_date)
);
```

---

## 6. Observability Domain

```sql
-- Agent Execution Traces: Track agent decisions
CREATE TABLE agent_execution_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference
    correlation_id VARCHAR(100),
    tracing_id VARCHAR(100),
    
    -- Agent information
    agent_name VARCHAR(100),
    interview_id UUID REFERENCES interviews(id),
    
    -- Execution details
    action VARCHAR(255),
    decision_rationale TEXT,
    tool_calls JSONB, -- Array of tools called
    
    -- Timing
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    -- Cost
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    
    -- Status
    status VARCHAR(50), -- success, error, timeout
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_traces_interview_id ON agent_execution_traces(interview_id);
CREATE INDEX idx_agent_traces_correlation_id ON agent_execution_traces(correlation_id);
CREATE INDEX idx_agent_traces_created_at ON agent_execution_traces(created_at DESC);

-- LLM Call Logs: Track all LLM API calls
CREATE TABLE llm_call_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference
    correlation_id VARCHAR(100),
    agent_execution_trace_id UUID REFERENCES agent_execution_traces(id),
    
    -- LLM information
    model VARCHAR(100),
    provider VARCHAR(100), -- openai, google, anthropic, ollama
    
    -- Tokens
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    
    -- Cost
    cost_usd DECIMAL(10, 6),
    
    -- Latency
    request_time TIMESTAMP WITH TIME ZONE,
    response_time TIMESTAMP WITH TIME ZONE,
    latency_ms INTEGER,
    
    -- Status
    status INTEGER, -- HTTP status code
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_llm_call_logs_created_at ON llm_call_logs(created_at DESC);
CREATE INDEX idx_llm_call_logs_provider ON llm_call_logs(provider);
```

---

## 7. Indexes & Performance Optimization

```sql
-- Vector similarity search
CREATE INDEX idx_questions_embedding_hnsw 
    ON questions USING hnsw (content_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_document_chunks_embedding_hnsw
    ON document_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Partial indexes for active data
CREATE INDEX idx_interviews_active 
    ON interviews(user_id, started_at DESC) 
    WHERE status != 'completed';

CREATE INDEX idx_learning_plans_active 
    ON learning_plans(user_id) 
    WHERE status IN ('active', 'in_progress');

-- Composite indexes for common queries
CREATE INDEX idx_answers_by_interview_question 
    ON answers(interview_question_id, submitted_at DESC);

CREATE INDEX idx_evaluations_by_question 
    ON evaluations(answer_id, evaluated_at DESC);
```

---

## 8. Data Retention & Archival

```sql
-- Archive old interviews after 2 years
CREATE POLICY archive_old_interviews AS
    SELECT * FROM interviews 
    WHERE created_at > NOW() - INTERVAL '2 years'
    OR status NOT IN ('completed', 'paused');

-- Purge soft-deleted records after 90 days
DELETE FROM users WHERE deleted_at < NOW() - INTERVAL '90 days';

-- Truncate search cache monthly
DELETE FROM rag_search_cache WHERE expires_at < NOW();

-- Archive evaluation logs after 1 year
ALTER TABLE llm_call_logs 
    ADD COLUMN archive_date TIMESTAMP WITH TIME ZONE 
    GENERATED ALWAYS AS (created_at + INTERVAL '1 year') STORED;
```

---

## 9. Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│     users       │
│   (PK: id)      │
├─────────────────┤
│ id              │
│ email           │
│ username        │
│ ...             │
└────────┬────────┘
         │
    ┌────┴────┬────────────────┬─────────────────┐
    │          │                │                 │
    ▼          ▼                ▼                 ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│interviews   │  │user_profiles │  │user_skills   │  │learning_plans    │
│ (FK:user_id)│  │ (FK:user_id) │  │ (FK:user_id) │  │ (FK:user_id)     │
└──────┬──────┘  └──────────────┘  └──────────────┘  └────────┬─────────┘
       │                                                        │
       │                                         ┌──────────────┴─────────┐
       │                                         │                        │
       ▼                                         ▼                        ▼
┌──────────────────┐                   ┌─────────────────────┐  ┌───────────────────┐
│interview_question│                   │learning_milestones  │  │skill_gaps         │
│ (FK:interview_id)│                   │ (FK:learning_plan)  │  │ (FK:user_id)      │
│ (FK:question_id) │                   └─────────────────────┘  └───────────────────┘
└──────┬───────────┘
       │            ┌─ learning_resources
       │            │  (FK:learning_milestone)
       ▼            │
    ┌───────────┐   │
    │questions  │   │
    │ (id)      │◄──┘
    └───┬───────┘
        │
        ▼
    ┌─────────┐
    │answers  │
    │ (FK:   │
    │ question)
    └────┬────┘
         │
         ▼
    ┌─────────────┐
    │evaluations  │
    │ (FK:answer) │
    └─────────────┘
```

---

## 10. Migration Strategy

```sql
-- Version 1.0: Initial schema
-- Version 1.1: Add vector embeddings
ALTER TABLE questions ADD COLUMN content_embedding vector(384);
CREATE INDEX idx_questions_embedding ON questions USING ivfflat(content_embedding vector_cosine_ops);

-- Version 1.2: Add RAG cache
CREATE TABLE rag_search_cache (...);

-- Version 1.3: Add observability tables
CREATE TABLE agent_execution_traces (...);
CREATE TABLE llm_call_logs (...);

-- Migration rollback
-- Revert to version 1.0 by dropping added tables/columns
DROP TABLE rag_search_cache;
ALTER TABLE questions DROP COLUMN content_embedding;
```

This schema provides:
- ✅ Normalization (3NF) for data integrity
- ✅ ACID compliance for transactions
- ✅ Vector support for RAG with pgvector
- ✅ Efficient indexing for common queries
- ✅ Soft deletes for compliance
- ✅ Audit trails for observability
- ✅ Scalability to millions of interviews
