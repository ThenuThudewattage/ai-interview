# AI Interview Intelligence Platform - Production Architecture

## Executive Summary

This is a production-grade Agentic AI system designed to help software engineers prepare for technical interviews through intelligent, adaptive, and data-driven coaching. The platform leverages multi-agent architectures, retrieval-augmented generation, and advanced observability to deliver personalized interview preparation.

### Key Innovation Principles

1. **Agentic Intelligence**: Agents are autonomous entities that perceive, decide, and act within defined boundaries
2. **Multi-Agent Orchestration**: Specialized agents work in concert without central coordination (loosely coupled)
3. **RAG-Powered Context**: All agent decisions grounded in verified, retrievable knowledge
4. **Observability-First**: Every decision is traceable, measurable, and evaluable
5. **Incremental Adaptation**: System learns from each interaction to improve future performance

---

## 1. SYSTEM ARCHITECTURE

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Angular Frontend                         │
│        (Dashboard, Interview UI, Analytics)                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway & Auth                         │
│              (FastAPI + JWT + Rate Limiting)                │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────────┬────────────────┐
        │                         │                │
        ↓                         ↓                ↓
┌───────────────────┐  ┌──────────────────┐  ┌─────────────┐
│  User Management  │  │  Interview API   │  │  Analytics  │
│      Service      │  │     Service      │  │   Service   │
└───────────────────┘  └──────────────────┘  └─────────────┘
                             │
                             ↓
        ┌────────────────────────────────────────┐
        │   LangGraph Orchestration Layer        │
        │   (Multi-Agent Coordinator)            │
        └────────────────────┬───────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ↓                    ↓                    ↓
┌──────────────────┐ ┌───────────────────┐ ┌──────────────┐
│ Interview Agent  │ │ Feedback Agent    │ │ Learning Agent│
│ (Conductor)      │ │ (Evaluator)       │ │ (Coach)      │
└──────────────────┘ └───────────────────┘ └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ↓                         ↓               ↓
┌──────────────────┐    ┌──────────────────┐    ┌──────────┐
│  RAG Pipeline    │    │  Tool Layer      │    │  Memory  │
│  (pgvector)      │    │  (Calling)       │    │  Layer   │
└──────────────────┘    └──────────────────┘    └──────────┘
        │                       │                    │
        └───────────┬───────────┴────────────────────┘
                    │
        ┌───────────┴──────────────┐
        │                          │
        ↓                          ↓
┌──────────────────┐        ┌──────────────┐
│  PostgreSQL      │        │  Redis       │
│  + pgvector      │        │  (Sessions)  │
└──────────────────┘        └──────────────┘
        │                          │
        │      Observability       │
        └──────────┬───────────────┘
                   │
        ┌──────────┴──────────────┐
        │                         │
        ↓                         ↓
┌──────────────────┐     ┌─────────────┐
│  Logging System  │     │  Tracing    │
│  (Structured)    │     │  (OpenTel)  │
└──────────────────┘     └─────────────┘
```

### 1.2 Architectural Principles

#### Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────┐
│         Interview Conductor Agent           │
│  (Business Logic - Domain Core)             │
├─────────────────────────────────────────────┤
│ Primary Ports (Inbound)                     │
│  • Interview Service Port                   │
│  • Query Port                               │
├─────────────────────────────────────────────┤
│ Secondary Ports (Outbound)                  │
│  • RAG Repository Port                      │
│  • Tool Execution Port                      │
│  • Memory Store Port                        │
├─────────────────────────────────────────────┤
│ Adapters (Implementation)                   │
│  • REST Adapter → Interview Service         │
│  • pgvector Adapter → RAG Repository        │
│  • Redis Adapter → Memory Store             │
│  • Tool Adapter → External Services         │
└─────────────────────────────────────────────┘
```

#### Domain-Driven Design (Bounded Contexts)

```
Interview Domain
├── Interview Aggregate
│   ├── Interview (Root)
│   ├── InterviewSession
│   ├── Question
│   └── Answer
├── Value Objects
│   ├── InterviewDifficulty
│   ├── SkillArea
│   └── InterviewMetrics
└── Repositories
    ├── InterviewRepository
    └── QuestionRepository

Evaluation Domain
├── Evaluation Aggregate
│   ├── Evaluation (Root)
│   ├── EvaluationMetrics
│   └── Feedback
├── Value Objects
│   ├── Score
│   ├── Confidence
│   └── Gap
└── Repositories
    └── EvaluationRepository

Learning Domain
├── LearningPlan Aggregate
│   ├── LearningPlan (Root)
│   ├── Resource
│   └── Progress
├── Value Objects
│   ├── SkillGap
│   ├── Competency
│   └── Milestone
└── Repositories
    └── LearningPlanRepository

Knowledge Domain
├── Knowledge Aggregate
│   ├── Document (Root)
│   ├── Chunk
│   └── Embedding
├── Value Objects
│   ├── Vector
│   ├── Metadata
│   └── Source
└── Repositories
    └── KnowledgeRepository
```

#### Event-Driven Architecture

```
Events Flow:

InterviewStartedEvent
  ├─→ [Interview Agent] Start conducting
  ├─→ [Learning Agent] Initialize context
  └─→ [Observability] Log session start

QuestionAskedEvent
  ├─→ [Interview Agent] Store question
  ├─→ [Observability] Log question
  └─→ [RAG] Update context

AnswerProvidedEvent
  ├─→ [Feedback Agent] Evaluate answer
  ├─→ [Memory] Store answer
  ├─→ [Observability] Log interaction
  └─→ [Learning Agent] Update skill gaps

EvaluationCompleteEvent
  ├─→ [Interview Agent] Adjust difficulty
  ├─→ [Learning Agent] Update plan
  ├─→ [Analytics] Record metrics
  └─→ [User Notification] Send feedback

InterviewCompletedEvent
  ├─→ [Feedback Agent] Generate report
  ├─→ [Learning Agent] Generate roadmap
  ├─→ [Analytics] Aggregate metrics
  └─→ [User Notification] Send summary
```

---

## 2. MULTI-AGENT SYSTEM DESIGN

### 2.1 Agent Taxonomy & Responsibilities

#### Interview Agent (Conductor)

**Purpose**: Primary orchestrator for interview flow

**Responsibilities**:
- Conduct interview sessions
- Select questions based on skill level
- Ask follow-up questions
- Adapt difficulty dynamically based on performance
- Manage time and pacing
- Transition between topics

**Memory Requirements**:
- Short-term: Current answer, current question context
- Long-term: Interview history, performance trends

**Tools Required**:
- `search_knowledge_base()` - Find relevant questions
- `get_user_profile()` - Retrieve skill levels
- `log_interaction()` - Record for observability
- `get_next_question()` - Question selection logic

**Constraints**:
- Cannot evaluate answers (deferred to Feedback Agent)
- Cannot modify learning plans (deferred to Learning Agent)
- Must respect time limits
- Must maintain conversation context

**State Machine**:
```
IDLE
  ↓ (start_interview)
INITIALIZING
  ↓ (load_context)
ASKING_QUESTION
  ↓ (receive_answer)
PROCESSING
  ↓ (await_evaluation)
ADJUSTING (based on evaluation)
  ↓ (select_next_question)
ASKING_QUESTION | CONCLUDING (if complete)
  ↓ (end_interview)
IDLE
```

#### Feedback Agent (Evaluator)

**Purpose**: Assess answer quality and provide structured feedback

**Responsibilities**:
- Evaluate technical accuracy
- Score completeness
- Assess communication quality
- Identify knowledge gaps
- Provide constructive feedback
- Generate rubric scores

**Memory Requirements**:
- Short-term: Current answer, rubric context
- Long-term: Evaluation history, pattern recognition

**Tools Required**:
- `retrieve_expected_answer()` - Get ideal response
- `retrieve_rubric()` - Get evaluation criteria
- `calculate_metrics()` - Compute scores
- `generate_feedback()` - Create human-readable feedback

**Constraints**:
- Cannot modify questions or difficulty
- Cannot make decisions about learning plans
- Must provide objective, measurable scores
- Must explain scores with evidence

**Evaluation Rubric**:
```
Technical Accuracy (0-100)
├─ Correctness (0-40)
├─ Completeness (0-30)
└─ Precision (0-30)

Communication Quality (0-100)
├─ Clarity (0-35)
├─ Structure (0-35)
└─ Conciseness (0-30)

Problem-Solving Approach (0-100)
├─ Systematic Thinking (0-40)
├─ Trade-off Analysis (0-35)
└─ Alternative Solutions (0-25)

Confidence (0-100)
├─ Demonstrated Certainty (0-50)
└─ Ability to Justify (0-50)

Overall Composite Score (0-100)
└─ Weighted Average of Above
```

#### Learning Agent (Coach)

**Purpose**: Identify gaps and guide skill development

**Responsibilities**:
- Identify skill gaps from evaluations
- Generate personalized learning plans
- Recommend resources
- Track progress over time
- Suggest next interview topics
- Predict proficiency growth

**Memory Requirements**:
- Short-term: Current evaluation results
- Long-term: Full learning history, progress tracking

**Tools Required**:
- `analyze_skill_gaps()` - Gap identification
- `search_learning_resources()` - Find materials
- `generate_learning_plan()` - Create roadmap
- `predict_proficiency()` - ML-based prediction

**Constraints**:
- Cannot conduct interviews
- Cannot evaluate answers
- Must base recommendations on objective data
- Must consider learner's pace

**Learning Plan Structure**:
```
LearningPlan
├─ Gap1: Design Patterns
│  ├─ Severity: High (35/100)
│  ├─ Resources
│  │  ├─ Article: "SOLID Principles"
│  │  ├─ Video: "Design Pattern Mastery"
│  │  └─ Practice: "Pattern Implementation Tasks"
│  ├─ MilestoneTarget: 80/100
│  └─ EstimatedWeeks: 4
├─ Gap2: System Design
│  ├─ Severity: Medium (55/100)
│  └─ ...
└─ NextInterviewTopic: "Database Optimization"
```

### 2.2 Agent Communication Protocol

#### Message Format

```python
{
    "message_type": "agent_request" | "agent_response" | "event",
    "source_agent": "interview_agent",
    "target_agent": "feedback_agent",
    "correlation_id": "uuid",
    "timestamp": "2026-06-17T10:30:00Z",
    "payload": {
        "action": "evaluate_answer",
        "data": {
            "question_id": "q_001",
            "answer": "...",
            "context": {...}
        }
    },
    "metadata": {
        "priority": "high",
        "timeout_ms": 5000,
        "retry_policy": "exponential_backoff"
    }
}
```

#### Request/Response Pattern

```
Interview Agent → Feedback Agent (Request)
{
    "action": "evaluate_answer",
    "question": {...},
    "answer": {...},
    "expected_context": {...}
}
        ↓ (Process)
        ↓ (Call Feedback Agent)
        ↓
Feedback Agent → Interview Agent (Response)
{
    "technical_score": 78,
    "communication_score": 82,
    "problem_solving_score": 75,
    "confidence_score": 80,
    "overall_score": 79,
    "feedback": "...",
    "gaps_identified": [...]
}
```

### 2.3 LangGraph Workflow Design

```
Interview Flow (Compiled Graph):

INPUT: (user_input, context)
  │
  ├─→ [Parse Input Node]
  │   └─→ Extract question/answer/command
  │
  ├─→ [Retrieve Context Node]
  │   ├─→ Get current session
  │   ├─→ Get user profile
  │   └─→ Get interview history
  │
  ├─→ [Interview Agent Node]
  │   ├─→ Decision: Is this first interaction?
  │   │   ├─ YES → Initialize interview
  │   │   └─ NO → Process answer
  │   │
  │   ├─→ Process Answer (if applicable)
  │   │   ├─→ [Call Feedback Agent]
  │   │   ├─→ [Update Memory]
  │   │   └─→ [Log Event]
  │   │
  │   ├─→ Adapt Difficulty
  │   │   ├─ If score < 60 → Lower difficulty
  │   │   ├─ If score > 85 → Increase difficulty
  │   │   └─ Otherwise → Maintain
  │   │
  │   └─→ Generate Next Question
  │       ├─→ [Call RAG]
  │       ├─→ [Check Question Variety]
  │       └─→ [Format Question]
  │
  ├─→ [Update Memory Node]
  │   ├─→ Store question/answer
  │   ├─→ Store evaluation
  │   └─→ Update skill tracking
  │
  ├─→ [Observability Node]
  │   ├─→ Log prompt usage
  │   ├─→ Track latency
  │   ├─→ Record token usage
  │   └─→ Emit event
  │
  └─→ OUTPUT: (response, metadata)

Tool Calling Flow:

Agent Decision → Tool Selection
  ├─ Tool: search_knowledge_base
  │  ├─ Params: [skill_area, difficulty, exclude_ids]
  │  └─ Returns: [questions]
  │
  ├─ Tool: get_user_profile
  │  ├─ Params: [user_id]
  │  └─ Returns: {skills, weaknesses, preferences}
  │
  ├─ Tool: analyze_answer_quality
  │  ├─ Params: [question, answer, rubric]
  │  └─ Returns: {scores, feedback}
  │
  └─ Tool: get_learning_recommendations
     ├─ Params: [skill_gaps, learning_history]
     └─ Returns: {resources, plan}
```

---

## 3. RAG ARCHITECTURE

### 3.1 RAG Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   DOCUMENT INGESTION                        │
│  (PDFs, Markdown, JSON, Web Articles)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    PREPROCESSING                            │
│  • Format normalization                                     │
│  • Language detection                                       │
│  • Metadata extraction                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    SEMANTIC CHUNKING                        │
│  • Sentence boundary detection                             │
│  • Chunk size: 512 tokens (with 50-token overlap)         │
│  • Preserve semantic coherence                             │
│  • Associate parent document for retrieval                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              EMBEDDING GENERATION                          │
│  • Model: Google's text-embedding-3-small                  │
│  • Dimension: 384                                          │
│  • Batch: 32 chunks per API call                           │
│  • Normalize embeddings for cosine similarity              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│           VECTOR STORAGE (pgvector)                         │
│  • Store embeddings in PostgreSQL                          │
│  • Create HNSW index for efficient search                  │
│  • Store metadata: source, timestamp, skill_area           │
│  • Associate chunk_id → question_id (optional)             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────────┐
        │                             │
        ↓                             ↓
┌─────────────────┐         ┌──────────────────┐
│  QUERY TIME     │         │  OFFLINE ANALYTICS
│  • User Query   │         │  • Embedding Drift
│  • Embed Query  │         │  • Chunk Quality
│  • Vector Search│         │  • Update Cadence
│  • Hybrid Search│         │  • Performance Metrics
└────────┬────────┘         └──────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────┐
│             RETRIEVAL & RANKING                             │
│  • BM25 (keyword search)                                    │
│  • Vector similarity (cosine)                               │
│  • Hybrid score: 0.6 * vector + 0.4 * BM25                │
│  • Re-rank with LLM (optional)                              │
│  • Return top-K (K=3 for context injection)                 │
└────────┬─────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────┐
│          CONTEXT AUGMENTATION                               │
│  • Insert retrieved chunks into prompt                      │
│  • Add source attribution                                   │
│  • Prepare for LLM consumption                              │
└────────┬─────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────┐
│             AGENT DECISION MAKING                           │
│  • Interview Agent uses context to guide interview          │
│  • Feedback Agent uses context to evaluate answers          │
│  • Learning Agent uses context to recommend resources       │
└────────┬─────────────────────────────────────────────────────┘
         │
         └──→ Response generation with RAG context
```

### 3.2 Knowledge Base Structure

```
Knowledge Base Documents:

1. Interview Question Banks
   ├─ System Design Questions (150 Q)
   ├─ Data Structure Questions (120 Q)
   ├─ Algorithm Questions (200 Q)
   ├─ Behavioral Questions (80 Q)
   └─ Domain-Specific Questions (Platform-dependent)

2. System Design Examples
   ├─ Design Patterns (SOLID, Creational, Structural, Behavioral)
   ├─ Architecture Patterns (MVC, Microservices, Event-Driven)
   ├─ Case Studies (Twitter, Instagram, LinkedIn)
   └─ Trade-off Analysis Documents

3. Behavioral Interview Guides
   ├─ STAR Method Examples
   ├─ Company-Specific Patterns
   ├─ Conflict Resolution Scenarios
   └─ Technical Communication

4. Data Science Interview Datasets
   ├─ ML Concepts
   ├─ Statistical Methods
   ├─ Feature Engineering
   └─ Model Evaluation

5. Company Interview Patterns
   ├─ FAANG Interview Styles
   ├─ Startup Interview Patterns
   ├─ Company-Specific Questions
   └─ Interview Feedback Patterns

Chunking Strategy:

Question Chunk:
{
    "type": "question",
    "content": "Design a URL shortener like bit.ly...",
    "difficulty": "hard",
    "skill_areas": ["system_design", "scalability"],
    "expected_depth": "deep",
    "chunked_size_tokens": 512,
    "metadata": {
        "source": "system_design_questions_db",
        "company_filter": ["google", "meta"],
        "frequency": "common",
        "last_updated": "2026-06-15"
    }
}

Example Chunk:
{
    "type": "example",
    "content": "Example answer for design question...",
    "parent_question_id": "q_001",
    "quality_score": 0.92,
    "metadata": {
        "source": "leetcode_solutions",
        "approach": "scalable_solution",
        "language": "system_design"
    }
}

Resource Chunk:
{
    "type": "resource",
    "content": "Link and summary of learning material",
    "topic": "system_design",
    "proficiency_level": "intermediate",
    "time_to_complete": 120,
    "metadata": {
        "source": "coursera_course",
        "rating": 4.8
    }
}
```

### 3.3 Vector Search Implementation

```python
# Search Query Example

query = "How do I design a real-time notification system?"

# 1. Embed query
query_embedding = embed_model.embed_query(query)

# 2. Perform hybrid search
bm25_results = bm25_search(query, limit=10)
vector_results = pgvector_search(query_embedding, limit=10)

# 3. Hybrid ranking
hybrid_results = rank_results(
    bm25_results=bm25_results,
    vector_results=vector_results,
    bm25_weight=0.4,
    vector_weight=0.6
)

# 4. Re-rank with LLM (optional)
reranked_results = llm_rerank(
    query=query,
    candidates=hybrid_results[:10],
    top_k=3
)

# 5. Return top results
return reranked_results  # [Chunk, Chunk, Chunk]
```

---

## 4. TOOL CALLING SYSTEM

### 4.1 Tool Specifications

#### Tool: `search_knowledge_base`

```yaml
Name: search_knowledge_base
Description: Search the knowledge base for interview questions and resources
Parameters:
  - name: skill_area
    type: enum
    values: [system_design, data_structures, algorithms, behavioral, ml, etc.]
    required: true
    
  - name: difficulty
    type: enum
    values: [easy, medium, hard, expert]
    required: true
    
  - name: query
    type: string
    required: true
    description: Natural language search query
    
  - name: limit
    type: integer
    default: 5
    description: Number of results to return

Returns:
  - questions: List[Question]
    - id: string
    - content: string
    - difficulty: string
    - skill_areas: List[string]
    - followup_hints: List[string]
    
  - resources: List[Resource]
    - title: string
    - url: string
    - type: string (article, video, course)
    - estimated_time: integer (minutes)
    - proficiency_level: string

Example Call:
{
    "skill_area": "system_design",
    "difficulty": "hard",
    "query": "distributed cache design",
    "limit": 3
}

Response:
{
    "questions": [
        {
            "id": "q_122",
            "content": "Design a distributed caching layer...",
            "difficulty": "hard",
            "skill_areas": ["system_design", "distributed_systems"],
            "followup_hints": ["discuss cache invalidation", "talk about consistency"]
        }
    ],
    "resources": [...]
}
```

#### Tool: `get_user_profile`

```yaml
Name: get_user_profile
Description: Retrieve user's skill profile, interview history, and preferences
Parameters:
  - name: user_id
    type: string
    required: true

Returns:
  - user_id: string
  - name: string
  - current_skills: Map[SkillArea, Proficiency(0-100)]
  - skill_gaps: List[SkillGap]
  - interview_history: List[InterviewSummary]
  - preferences:
      - preferred_difficulty: string
      - topics_to_focus: List[string]
      - interview_duration_minutes: integer
  - learning_plan: LearningPlan

Example Response:
{
    "user_id": "user_123",
    "name": "John Doe",
    "current_skills": {
        "system_design": 72,
        "algorithms": 68,
        "behavioral": 75,
        "ml": 45
    },
    "skill_gaps": [
        {
            "area": "machine_learning",
            "severity": 0.85,
            "last_assessed": "2026-06-10"
        }
    ],
    "preferences": {
        "preferred_difficulty": "hard",
        "topics_to_focus": ["system_design", "distributed_systems"]
    }
}
```

#### Tool: `analyze_answer_quality`

```yaml
Name: analyze_answer_quality
Description: Evaluate answer quality using defined rubrics
Parameters:
  - name: question_id
    type: string
    required: true
    
  - name: answer
    type: string
    required: true
    
  - name: rubric_type
    type: enum
    values: [system_design, algorithm, behavioral, technical]
    required: true

Returns:
  - scores:
      - technical_accuracy: 0-100
      - completeness: 0-100
      - communication: 0-100
      - problem_solving_approach: 0-100
      - confidence: 0-100
      - composite_score: 0-100
  - feedback:
      - strengths: List[string]
      - improvements: List[string]
      - gaps_identified: List[SkillGap]
  - metadata:
      - rubric_version: string
      - evaluation_model: string
      - confidence_in_evaluation: 0-1
```

#### Tool: `generate_learning_plan`

```yaml
Name: generate_learning_plan
Description: Create personalized learning roadmap based on skill gaps
Parameters:
  - name: user_id
    type: string
    required: true
    
  - name: skill_gaps
    type: List[SkillGap]
    required: true
    
  - name: target_proficiency
    type: integer (0-100)
    required: true
    default: 80

Returns:
  - learning_plan:
      - plan_id: string
      - created_at: timestamp
      - target_date: timestamp
      - milestones: List[Milestone]
        - name: string
        - target_score: integer
        - resources: List[Resource]
        - estimated_hours: integer
        - completion_percentage: 0-100
      - total_estimated_hours: integer
      - recommended_study_schedule: List[DailyPlan]
```

#### Tool: `update_memory`

```yaml
Name: update_memory
Description: Store information in short-term and long-term memory
Parameters:
  - name: memory_type
    type: enum
    values: [short_term, long_term]
    required: true
    
  - name: key
    type: string
    required: true
    
  - name: value
    type: any
    required: true
    
  - name: ttl_minutes
    type: integer
    description: For short-term memory, TTL in minutes
    default: 60

Returns:
  - success: boolean
  - stored_at: timestamp
  - memory_id: string
```

#### Tool: `log_interaction`

```yaml
Name: log_interaction
Description: Log interaction for observability and analytics
Parameters:
  - name: event_type
    type: enum
    values: [question_asked, answer_provided, evaluation_completed, plan_generated]
    required: true
    
  - name: payload
    type: dict
    required: true
    
  - name: metadata
    type: dict
    default: {}
    description: Additional context

Returns:
  - event_id: string
  - logged_at: timestamp
  - tracing_id: string
```

### 4.2 Tool Availability by Agent

```
Interview Agent can call:
├─ search_knowledge_base
├─ get_user_profile
├─ update_memory
├─ log_interaction
└─ evaluate_answer (async → Feedback Agent)

Feedback Agent can call:
├─ search_knowledge_base
├─ get_expected_answer
├─ analyze_answer_quality
├─ update_memory
└─ log_interaction

Learning Agent can call:
├─ search_knowledge_base
├─ get_user_profile
├─ analyze_skill_gaps
├─ generate_learning_plan
├─ update_memory
└─ log_interaction
```

---

## 5. MEMORY SYSTEM

### 5.1 Short-Term Memory (Session-Based)

```
Session Memory (Redis):

Key: session:{session_id}

{
    "session_id": "sess_abc123",
    "user_id": "user_123",
    "created_at": "2026-06-17T10:00:00Z",
    "current_question": {
        "id": "q_45",
        "content": "...",
        "difficulty": "hard",
        "asked_at": "2026-06-17T10:05:00Z"
    },
    "current_interview_state": {
        "status": "answering",
        "questions_asked": 5,
        "score_running_average": 76.5,
        "current_difficulty": "hard"
    },
    "agent_context": {
        "interview_agent_state": {...},
        "feedback_agent_state": {...},
        "learning_agent_state": {...}
    },
    "ttl": 3600  // Expires after 1 hour
}

Question Context:
{
    "question_id": "q_45",
    "skill_area": "system_design",
    "difficulty": "hard",
    "asked_at": "2026-06-17T10:05:00Z",
    "time_spent_seconds": 0,
    "followup_asked": false,
    "hints_provided": []
}

Answer Context:
{
    "answer_id": "ans_123",
    "question_id": "q_45",
    "answer_text": "...",
    "provided_at": "2026-06-17T10:15:00Z",
    "time_taken_seconds": 600
}
```

### 5.2 Long-Term Memory (Persistent)

```
PostgreSQL Tables:

interview_history
├─ id (PK)
├─ user_id (FK)
├─ created_at
├─ completed_at
├─ total_score
├─ difficulty_level
└─ metadata (JSON)

interview_answers
├─ id (PK)
├─ interview_id (FK)
├─ question_id (FK)
├─ answer_text
├─ evaluation_score
├─ feedback_provided
└─ timestamp

skill_assessments
├─ id (PK)
├─ user_id (FK)
├─ skill_area
├─ proficiency_score (0-100)
├─ assessed_at
├─ assessment_count
└─ trend

user_learning_history
├─ id (PK)
├─ user_id (FK)
├─ skill_area
├─ resources_completed
├─ progress_percentage
├─ estimated_hours_spent
└─ effectiveness_score

user_preferences
├─ user_id (PK)
├─ preferred_difficulty
├─ preferred_interview_duration
├─ preferred_skill_areas
├─ preferred_question_types
└─ last_updated
```

### 5.3 Memory Access Patterns

```
Write Pattern:
Interview Session → Update memory
├─ Short-term: Redis (immediate)
├─ Publish: Event (for subscribers)
└─ Long-term: PostgreSQL (async job)

Read Pattern:
Agent requires context:
├─ Check Redis (short-term) → Hit rate ~90% during session
├─ If miss → Check PostgreSQL (long-term)
└─ Cache result in Redis (for next 5 minutes)

Flush Pattern:
Session End:
├─ Aggregate session data
├─ Calculate final scores
├─ Store in long-term memory
├─ Delete from short-term
└─ Trigger learning plan update
```

---

## 6. EVALUATION FRAMEWORK

### 6.1 Evaluation Metrics

```
Evaluation Model: Multi-Dimensional Rubric

Level 1: Atomic Metrics
├─ Technical Accuracy
│  ├─ Correctness (40 pts)
│  ├─ Completeness (30 pts)
│  └─ Precision (30 pts)
│
├─ Communication Quality
│  ├─ Clarity (35 pts)
│  ├─ Structure (35 pts)
│  └─ Conciseness (30 pts)
│
├─ Problem Solving
│  ├─ Systematic Approach (40 pts)
│  ├─ Trade-off Analysis (35 pts)
│  └─ Alternative Solutions (25 pts)
│
├─ Confidence Level
│  ├─ Demonstrated Certainty (50 pts)
│  └─ Ability to Justify (50 pts)
│
└─ Time Management
   ├─ Response Time Appropriateness (50 pts)
   └─ Pace Management (50 pts)

Level 2: Composite Scores
├─ Technical Composite = Avg(Accuracy, Problem Solving)
├─ Soft Skill Composite = Avg(Communication, Confidence)
└─ Overall Score = 0.6 * Technical + 0.4 * Soft Skills

Level 3: Trends
├─ Moving Average (last 5 interviews)
├─ Skill Area Trends
├─ Difficulty Progression
└─ Improvement Velocity
```

### 6.2 Scoring Logic

```python
def calculate_score(
    question_type: str,
    answer: str,
    rubric: Rubric,
    expected_answer: str,
    context: Dict
) -> EvaluationScore:
    
    # 1. Technical Accuracy Assessment
    accuracy = assess_accuracy(
        answer=answer,
        expected_answer=expected_answer,
        question_type=question_type
    )
    
    # 2. Communication Quality
    communication = assess_communication(
        answer=answer,
        rubric=rubric
    )
    
    # 3. Problem-Solving Approach
    problem_solving = assess_approach(
        answer=answer,
        question_type=question_type
    )
    
    # 4. Confidence Detection
    confidence = detect_confidence(
        answer=answer,
        question_type=question_type
    )
    
    # 5. Composite Calculation
    technical_composite = (
        accuracy * 0.4 + 
        problem_solving * 0.6
    )
    
    soft_skill_composite = (
        communication * 0.6 + 
        confidence * 0.4
    )
    
    overall_score = (
        technical_composite * 0.6 + 
        soft_skill_composite * 0.4
    )
    
    return EvaluationScore(
        technical_accuracy=accuracy,
        communication=communication,
        problem_solving=problem_solving,
        confidence=confidence,
        technical_composite=technical_composite,
        soft_skill_composite=soft_skill_composite,
        overall_score=overall_score,
        reasoning=generate_scoring_explanation(...)
    )
```

### 6.3 Evaluation Storage

```
Database: evaluations table

{
    "evaluation_id": "eval_123",
    "interview_id": "int_456",
    "question_id": "q_789",
    "answer_id": "ans_101",
    "evaluator_model": "gemini-flash",
    "evaluation_timestamp": "2026-06-17T10:15:00Z",
    
    "scores": {
        "technical_accuracy": 78,
        "completeness": 75,
        "communication": 82,
        "problem_solving": 76,
        "confidence": 80,
        "overall": 78
    },
    
    "feedback": {
        "strengths": [
            "Clear problem decomposition",
            "Good communication of trade-offs"
        ],
        "improvements": [
            "Could discuss edge cases more thoroughly",
            "Missing discussion on scalability"
        ],
        "gaps_identified": [
            {
                "skill": "distributed_systems",
                "severity": "high",
                "related_topics": ["consistency_models", "partition_tolerance"]
            }
        ]
    },
    
    "metadata": {
        "answer_length_words": 450,
        "response_time_seconds": 600,
        "model_confidence": 0.92,
        "re_evaluation_count": 0
    }
}
```

---

## 7. OBSERVABILITY FRAMEWORK

### 7.1 Observability Layers

#### Layer 1: Logging

```
Structured Logging Format (JSON):

{
    "timestamp": "2026-06-17T10:15:30.123Z",
    "level": "INFO",
    "service": "interview_agent",
    "correlation_id": "corr_123abc",
    "tracing_id": "trace_456def",
    "user_id": "user_789",
    
    "event": {
        "type": "question_generated",
        "action": "search_knowledge_base",
        "status": "success"
    },
    
    "context": {
        "session_id": "sess_123",
        "interview_id": "int_456",
        "question_index": 3
    },
    
    "metrics": {
        "latency_ms": 234,
        "tokens_used": 1250,
        "cost_usd": 0.0125
    },
    
    "data": {
        "query": "distributed cache design",
        "results_count": 5,
        "skill_area": "system_design"
    }
}

Log Levels:
├─ DEBUG: Detailed diagnostics (LLM prompt, full response)
├─ INFO: Key events (question asked, evaluation done)
├─ WARN: Performance degradation, rate limit approaching
└─ ERROR: Failed operations, exceptions
```

#### Layer 2: Metrics/Monitoring

```
Key Metrics (Time-Series):

Agent Metrics:
├─ interview_agent_question_latency_ms
├─ interview_agent_context_retrieval_latency_ms
├─ feedback_agent_evaluation_latency_ms
└─ learning_agent_plan_generation_latency_ms

LLM Metrics:
├─ llm_prompt_tokens_per_call
├─ llm_completion_tokens_per_call
├─ llm_total_cost_usd_cumulative
├─ llm_latency_ms
└─ llm_error_rate

RAG Metrics:
├─ rag_query_latency_ms
├─ rag_retrieval_relevance_score
├─ rag_cache_hit_rate
└─ rag_embedding_cache_hit_rate

System Metrics:
├─ database_query_latency_p99_ms
├─ redis_operation_latency_p99_ms
├─ api_response_time_p99_ms
└─ error_rate_percentage
```

#### Layer 3: Tracing (OpenTelemetry)

```
Trace Span Structure:

Root Span: "handle_interview_message"
├─ Span: "parse_user_input"
│  ├─ Attribute: "user_id"
│  ├─ Attribute: "message_length"
│  └─ Event: "input_parsed"
│
├─ Span: "retrieve_session_context"
│  ├─ Attribute: "session_id"
│  ├─ Attribute: "cache_hit"
│  └─ Event: "context_retrieved"
│
├─ Span: "interview_agent_process"
│  ├─ Span: "search_knowledge_base"
│  │  ├─ Attribute: "query"
│  │  ├─ Attribute: "results_count"
│  │  └─ Event: "search_completed"
│  │
│  ├─ Span: "call_llm_for_question"
│  │  ├─ Attribute: "model"
│  │  ├─ Attribute: "prompt_tokens"
│  │  ├─ Attribute: "completion_tokens"
│  │  └─ Event: "llm_response_received"
│  │
│  └─ Event: "question_generated"
│
├─ Span: "feedback_agent_evaluate"
│  ├─ Span: "call_llm_for_evaluation"
│  │  ├─ Attribute: "rubric_version"
│  │  └─ Attribute: "confidence"
│  │
│  └─ Event: "evaluation_completed"
│
├─ Span: "update_memory"
│  └─ Event: "memory_updated"
│
└─ Event: "response_sent"

Trace Sampling:
├─ 100% for errors
├─ 10% for normal operations
└─ 50% for slow operations (>1s latency)
```

#### Layer 4: Cost Tracking

```
Cost Model:

Per LLM Call:
├─ Model: gemini-flash
├─ Input tokens: 1250
├─ Output tokens: 450
├─ Cost per 1M input tokens: $0.075
├─ Cost per 1M output tokens: $0.30
│
├─ Input cost: 1250 * (0.075 / 1_000_000) = $0.00009375
├─ Output cost: 450 * (0.30 / 1_000_000) = $0.000135
└─ Total: $0.00022875

Per RAG Operation:
├─ Embedding generation: ~$0.00002 per query
├─ Vector search: ~$0.000001 (negligible)
└─ BM25 search: ~$0 (local)

Cost Aggregation:
├─ Per interview: Sum of all LLM + RAG costs
├─ Per user (monthly): Sum of all interviews
├─ System-wide (hourly/daily): Total costs
└─ ROI tracking: Cost per successful interview preparation
```

### 7.2 Observability Implementation

```python
# Instrumentation Example

from opentelemetry import trace, metrics
from structlog import get_logger

logger = get_logger()
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

@log_with_tracing(span_name="conduct_interview")
async def conduct_interview(
    user_id: str,
    session_id: str
):
    with tracer.start_as_current_span("interview_flow") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("session_id", session_id)
        
        # Load context
        with tracer.start_as_current_span("load_context") as child_span:
            context = await load_user_context(user_id)
            child_span.set_attribute("context_size", len(context))
            logger.info("context_loaded", user_id=user_id, items=len(context))
        
        # Search knowledge base
        with tracer.start_as_current_span("search_knowledge_base") as child_span:
            questions = await search_knowledge_base(
                skill_area=context.next_skill_area,
                difficulty=context.current_difficulty
            )
            child_span.set_attribute("results_count", len(questions))
            logger.info("questions_found", count=len(questions))
        
        # Generate question with LLM
        with tracer.start_as_current_span("generate_question") as child_span:
            question = await generate_question_with_llm(
                base_questions=questions,
                user_context=context
            )
            child_span.set_attribute("model", "gemini-flash")
            child_span.set_attribute("tokens_used", question.metadata.tokens)
            
            # Record cost
            cost = calculate_llm_cost(question.metadata.tokens)
            logger.info(
                "question_generated",
                cost_usd=cost,
                tokens=question.metadata.tokens
            )
        
        return question
```

---

## 8. TECHNOLOGY RATIONALE

### 8.1 Backend Stack Justification

**FastAPI**
- Reason: Built-in OpenAPI/Swagger, async support, automatic validation with Pydantic
- Use Case: Serving REST APIs with minimal boilerplate, enabling real-time WebSocket for interview sessions
- Trade-off: Less mature than Django, but async-first design is critical for handling multiple concurrent interviews

**LangGraph**
- Reason: Purpose-built for multi-agent orchestration, explicit state management, debuggable workflow execution
- Use Case: Define interview flow as a DAG, handle agent communication, manage memory at edges
- Trade-off: Abstraction over raw LLM calling, but forces good architectural patterns

**PydanticAI**
- Reason: Structured output validation, agent framework with built-in tool calling
- Use Case: Define agents with explicit prompts, validate LLM outputs deterministically
- Trade-off: Tight coupling to Pydantic ecosystem, but eliminates JSON parsing bugs

**PostgreSQL + pgvector**
- Reason: Relational data for normalized storage, pgvector extension for vector indexing (HNSW)
- Use Case: OLTP for user/interview data, vectors for semantic search
- Trade-off: Complexity over SQLite, but necessary for production scale and vector operations

**Redis**
- Reason: In-memory session store, sub-millisecond response times for memory access
- Use Case: Short-term session state, question cache, rate limiting
- Trade-off: Requires cluster for HA, but critical for low-latency memory access

### 8.2 Frontend Stack Justification

**Angular 20**
- Reason: Enterprise-grade framework, strong typing (TypeScript), built-in RxJS
- Use Case: Complex real-time dashboard, reactive form handling, interview UI
- Trade-off: Steeper learning curve than React, but better for large teams

**Angular Material**
- Reason: Comprehensive component library aligned with Material Design, accessibility built-in
- Use Case: Professional UI components, consistent design across app
- Trade-off: Opinionated styling, but reduces CSS burden

**RxJS**
- Reason: Reactive programming for handling async streams
- Use Case: WebSocket real-time updates, stream of interview events, state management
- Trade-off: Learning curve, but elegant for event-driven UI

### 8.3 Infrastructure Stack Justification

**Docker**
- Reason: Reproducible environments, simplified deployment, language-agnostic
- Use Case: Package backend (Python), frontend (Node build), ensure dev≈prod
- Trade-off: Overhead vs bare metal, but essential for cloud deployment

**Docker Compose**
- Reason: Local multi-container development, easy to add PostgreSQL, Redis, Ollama
- Use Case: Dev environment parity with production
- Trade-off: Not for production (use Kubernetes), but perfect for development

**GitHub Actions**
- Reason: Native GitHub integration, free tier, no additional platform costs
- Use Case: CI/CD pipeline for testing, building, and deploying
- Trade-off: Limited compared to enterprise CI/CD, but sufficient for most projects

### 8.4 LLM Stack Justification

**Gemini Flash (Primary)**
- Reason: Cost-effective, fast inference, strong multimodal support, good for structured outputs
- Use Case: Question generation, answer evaluation, learning recommendations
- Trade-off: API dependency, rate limits, but best cost/performance ratio

**OpenRouter (Fallback)**
- Reason: Route to multiple models (Claude, GPT-4, Mixtral) based on cost/quality requirements
- Use Case: A/B testing different models, graceful degradation on Gemini rate limits
- Trade-off: Adds complexity, but critical for production reliability

**Ollama (Local)**
- Reason: Run open-source models locally (Llama 2, Mistral) for data privacy
- Use Case: Development, on-premise deployments, privacy-critical scenarios
- Trade-off: Requires local GPU/resources, but no external API costs

---

## 9. ARCHITECTURAL PATTERNS EMPLOYED

### 9.1 Design Patterns

```
Agent Pattern (Autonomous Entity)
├─ Self-contained decision logic
├─ Tool-based action execution
├─ State persistence
└─ Event-driven communication

Tool Pattern (Capability Extension)
├─ Explicit parameter schema
├─ Deterministic execution
├─ Error handling
└─ Result caching (optional)

Strategy Pattern (Evaluation Rubrics)
├─ Different rubrics for different question types
├─ Runtime strategy selection
├─ Strategy versioning
└─ A/B testing support

Repository Pattern (Data Abstraction)
├─ Interface-based data access
├─ Multiple implementations (SQL, vector, cache)
├─ Transaction management
└─ Query caching

Observer Pattern (Event Emission)
├─ Agents emit events
├─ Subscribers react asynchronously
├─ Decoupled communication
└─ Event sourcing capability

State Machine (Interview Flow)
├─ Explicit state transitions
├─ Guarded transitions
├─ State context preservation
└─ Audit trail
```

### 9.2 Architectural Patterns

```
Hexagonal Architecture
├─ Core domain logic isolated
├─ Multiple adapters for same port
├─ Easy to test and refactor
└─ Framework-agnostic business logic

Domain-Driven Design
├─ Bounded contexts for each domain
├─ Aggregate roots define consistency boundaries
├─ Value objects for immutable data
├─ Repository abstractions
└─ Event sourcing capability

Event-Driven Architecture
├─ Asynchronous communication
├─ Loose coupling between components
├─ Audit trail and replay capability
├─ Scalability through event streaming
└─ CQRS potential for read/write separation

Pipeline Pattern (RAG)
├─ Composable stages
├─ Each stage has clear interface
├─ Easy to add/modify stages
├─ Testable independently
└─ Monitoring per stage

Strangler Pattern (Migration)
├─ Run old and new systems side-by-side
├─ Gradually migrate functionality
├─ Reduce deployment risk
└─ Rollback capability
```

---

## 10. PRODUCTION CONSIDERATIONS

### 10.1 Scalability Strategy

```
Horizontal Scaling:

1. Stateless API Layer
   └─ Deploy multiple FastAPI instances behind load balancer
   
2. Agent Workers (LangGraph)
   ├─ Run agents in worker pods
   ├─ Use message queue for agent communication
   └─ Scale workers independently by agent type

3. Database Scaling
   ├─ Read replicas for query load
   ├─ Write to primary, read from replicas
   ├─ Connection pooling
   └─ Separate OLTP and analytical workloads

4. Cache Scaling
   ├─ Redis cluster for high availability
   ├─ Consistent hashing for key distribution
   └─ Circuit breaker for cache failures

Vertical Scaling:
├─ Increase pod resources for high-latency agents
├─ Use GPUs for embedding generation
└─ Tune database indexes
```

### 10.2 Reliability Strategy

```
High Availability:

1. Redundancy
   ├─ Multiple API instances
   ├─ Database replication
   ├─ Redis cluster
   └─ Load balancing

2. Circuit Breakers
   ├─ For external LLM calls (rate limits, failures)
   ├─ For database queries
   ├─ For cache operations
   └─ Graceful degradation on failures

3. Timeouts & Retries
   ├─ Per-operation timeouts
   ├─ Exponential backoff for retries
   ├─ Max retry limits to prevent cascading failures
   └─ Dead letter queues for failed jobs

4. Monitoring & Alerting
   ├─ Alerts for error rates > 1%
   ├─ Alerts for latency p99 > 2s
   ├─ Alerts for pod crashes
   └─ Alerts for cost overruns
```

### 10.3 Security Strategy

```
Defense in Depth:

1. Authentication
   ├─ JWT tokens with expiry
   ├─ Refresh token rotation
   ├─ MFA for sensitive operations
   └─ OAuth2 for social login

2. Authorization
   ├─ Role-based access control (RBAC)
   ├─ Row-level security for interviews
   ├─ API key scoping
   └─ Audit logging for all access

3. Data Protection
   ├─ TLS/SSL for all communications
   ├─ Data encryption at rest
   ├─ PII masking in logs
   ├─ Secure secrets management (HashiCorp Vault)
   └─ GDPR compliance (right to deletion, export)

4. API Security
   ├─ Rate limiting per user
   ├─ Input validation with Pydantic
   ├─ CORS configuration
   ├─ SQL injection prevention (ORM)
   └─ CSRF protection
```

### 10.4 Cost Optimization

```
Cost Reduction Strategies:

1. LLM Cost
   ├─ Use cheaper models (Gemini Flash vs GPT-4)
   ├─ Prompt caching to reduce repeated calls
   ├─ Batch processing for non-realtime operations
   ├─ Model selection based on question type
   └─ Fallback to Ollama for common questions

2. Embedding Cost
   ├─ Cache embeddings for knowledge base (one-time)
   ├─ Batch embedding generation
   ├─ Model compression techniques
   └─ Quantization for local Ollama

3. Infrastructure Cost
   ├─ Auto-scaling based on load
   ├─ Spot instances for non-critical workloads
   ├─ Reserved instances for baseline load
   ├─ Serverless functions for sporadic tasks
   └─ CDN for static assets

4. Database Cost
   ├─ Index optimization
   ├─ Partitioning for large tables
   ├─ Archive old data
   └─ Read replicas only for high-traffic queries
```

---

## 11. SUMMARY & NEXT STEPS

This architecture provides:

✅ **Agentic Intelligence**: Autonomous agents making contextual decisions  
✅ **Multi-Agent Orchestration**: Specialized agents working in concert  
✅ **RAG-Powered Context**: All decisions grounded in verified knowledge  
✅ **Production-Grade**: Observability, reliability, security, scalability  
✅ **Enterprise Patterns**: Hexagonal, DDD, Event-Driven  
✅ **Cost-Optimized**: Smart LLM model selection, caching strategies  
✅ **Extensible**: Easy to add new agents, tools, question types  

**Next Steps**:
1. Database schema design (Chapter 3)
2. API contract specifications (Chapter 4)
3. LangGraph workflow implementation (Chapter 5)
4. Folder structure and project scaffolding (Chapter 6)
5. Deployment architecture (Chapter 7)
6. Development roadmap (Chapter 8)
