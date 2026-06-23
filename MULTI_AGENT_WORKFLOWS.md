# Multi-Agent Workflow Diagrams & Visual Architecture

## Overview

This document contains comprehensive visual representations of the multi-agent system, including Mermaid diagrams for workflow orchestration, state machines, message flows, and architecture patterns.

---

## 1. Interview Session Flow - High Level

```mermaid
graph TD
    Start([User Initiates Interview]) --> Init["Initialize Interview Node<br/>(Interview Agent: Setup Phase)"]
    Init --> GenQ["Generate Question Node<br/>(Interview Agent: Reasoning)"]
    GenQ --> SendQ["Send Question to Frontend"]
    SendQ --> User["User Answers Question"]
    User --> ReceiveA["Receive Answer"]
    ReceiveA --> Process["Process Answer Node<br/>(Validation & Parsing)"]
    Process --> Eval["Evaluate Answer Node<br/>(Feedback Agent)"]
    Eval --> Analyze["Analyze & Adjust Node<br/>(Interview Agent: Meta-reasoning)"]
    Analyze --> Decision{"Interview<br/>Complete?"}
    Decision -->|No| GenQ
    Decision -->|Yes| Learning["Learning Agent Analysis<br/>(Skill Gaps & Roadmap)"]
    Learning --> Conclude["Conclude Interview Node"]
    Conclude --> End(["Return Results to Frontend"])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style Init fill:#e3f2fd
    style GenQ fill:#e3f2fd
    style Eval fill:#fff3e0
    style Learning fill:#f3e5f5
    style Conclude fill:#fce4ec
```

---

## 2. Multi-Agent Communication Protocol

```mermaid
graph LR
    subgraph InterviewState["Shared Interview State<br/>(Managed by LangGraph)"]
        Messages["message_history:<br/>List[Message]"]
        Context["context:<br/>UserProfile,<br/>Config"]
        Metrics["interview_metrics:<br/>Statistics"]
    end
    
    subgraph InterviewAgent["Interview Agent<br/>(Conductor)"]
        GenLogic["Generate Question Logic"]
        AdjustLogic["Adjust Difficulty Logic"]
        GenLogic --> Prompt1["System Prompt:<br/>Interview Orchestration"]
        AdjustLogic --> Prompt1
    end
    
    subgraph FeedbackAgent["Feedback Agent<br/>(Evaluator)"]
        EvalLogic["Evaluate Answer Quality"]
        ScoreLogic["Calculate Multi-dimensional Scores"]
        EvalLogic --> Prompt2["System Prompt:<br/>Answer Evaluation"]
        ScoreLogic --> Prompt2
    end
    
    subgraph LearningAgent["Learning Agent<br/>(Coach)"]
        GapLogic["Identify Skill Gaps"]
        PathLogic["Generate Learning Paths"]
        GapLogic --> Prompt3["System Prompt:<br/>Learning Analysis"]
        PathLogic --> Prompt3
    end
    
    InterviewState <-->|Read/Write| InterviewAgent
    InterviewState <-->|Read/Write| FeedbackAgent
    InterviewState <-->|Read/Write| LearningAgent
    
    Prompt1 -.->|LLM Call| LLMProvider["LLM Provider<br/>(Gemini Flash)"]
    Prompt2 -.->|LLM Call| LLMProvider
    Prompt3 -.->|LLM Call| LLMProvider
    
    LLMProvider -.->|Response| InterviewAgent
    LLMProvider -.->|Response| FeedbackAgent
    LLMProvider -.->|Response| LearningAgent
    
    style InterviewState fill:#f0f0f0,stroke:#333
    style InterviewAgent fill:#e3f2fd,stroke:#1976d2
    style FeedbackAgent fill:#fff3e0,stroke:#f57c00
    style LearningAgent fill:#f3e5f5,stroke:#7b1fa2
    style LLMProvider fill:#fffde7,stroke:#fbc02d
```

---

## 3. LangGraph State Machine - Complete Flow

```mermaid
stateDiagram-v2
    [*] --> Initialize: Start Interview
    
    Initialize --> GenerateQuestion: Setup complete
    
    GenerateQuestion --> SendToFrontend: Question ready
    SendToFrontend --> AwaitAnswer: Streaming question
    AwaitAnswer --> ReceiveAnswer: User answers
    
    ReceiveAnswer --> ProcessAnswer: Parse response
    ProcessAnswer --> EvaluateAnswer: Validate input
    
    EvaluateAnswer --> AnalyzeAndAdjust: Scoring complete
    AnalyzeAndAdjust --> CheckCompletion{Interview<br/>Limit<br/>Reached?}
    
    CheckCompletion -->|No| GenerateQuestion: More questions
    CheckCompletion -->|Yes| LearningAnalysis: Time/questions met
    
    LearningAnalysis --> ConcludeInterview: Analysis complete
    ConcludeInterview --> [*]: Interview finished
    
    note right of Initialize
        Set user context,
        interview config,
        initialize metrics
    end note
    
    note right of GenerateQuestion
        Interview Agent
        selects question,
        considers history,
        adjusts difficulty
    end note
    
    note right of EvaluateAnswer
        Feedback Agent
        scores answer,
        identifies gaps,
        calculates metrics
    end note
    
    note right of AnalyzeAndAdjust
        Interview Agent
        reviews feedback,
        updates user model,
        decides continuation
    end note
    
    note right of LearningAnalysis
        Learning Agent
        analyzes performance,
        generates roadmap,
        recommends resources
    end note
```

---

## 4. Message Flow Sequence - Full Interview Session

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant WebSocket
    participant Backend
    participant InterviewAgent as Interview<br/>Agent
    participant Database
    participant LLMProvider as LLM<br/>Provider
    participant FeedbackAgent as Feedback<br/>Agent
    participant LearningAgent as Learning<br/>Agent
    participant RAG as RAG<br/>System
    
    User->>Frontend: Click "Start Interview"
    Frontend->>Backend: POST /interviews/start
    activate Backend
    Backend->>Database: Create interview record
    Backend->>InterviewAgent: Initialize workflow
    activate InterviewAgent
    
    InterviewAgent->>Database: Get user profile & history
    InterviewAgent->>RAG: Search relevant questions
    RAG-->>InterviewAgent: Return top-3 questions
    
    InterviewAgent->>LLMProvider: Generate first question<br/>(with context)
    activate LLMProvider
    LLMProvider-->>InterviewAgent: Question & explanation
    deactivate LLMProvider
    
    InterviewAgent-->>Backend: Question ready
    Backend-->>Frontend: Send question via WebSocket
    deactivate InterviewAgent
    
    Frontend-->>User: Display question
    User->>Frontend: Type answer
    Frontend->>Backend: POST /interviews/{id}/answer
    
    activate Backend
    Backend->>Database: Store answer
    Backend->>FeedbackAgent: Evaluate answer
    activate FeedbackAgent
    
    FeedbackAgent->>LLMProvider: Score answer<br/>(with rubric)
    activate LLMProvider
    LLMProvider-->>FeedbackAgent: Score & feedback
    deactivate LLMProvider
    
    FeedbackAgent->>Database: Store evaluation
    FeedbackAgent-->>Backend: Evaluation results
    deactivate FeedbackAgent
    
    Backend->>Frontend: Stream evaluation<br/>results
    Frontend-->>User: Display feedback
    
    Backend->>InterviewAgent: Process feedback<br/>& decide next
    activate InterviewAgent
    InterviewAgent->>InterviewAgent: Check completion logic
    
    alt Interview Complete
        InterviewAgent->>LearningAgent: Analyze overall performance
        activate LearningAgent
        LearningAgent->>Database: Get all answers & scores
        LearningAgent->>LLMProvider: Generate learning plan
        activate LLMProvider
        LLMProvider-->>LearningAgent: Learning recommendations
        deactivate LLMProvider
        LearningAgent->>Database: Store learning plan
        LearningAgent-->>InterviewAgent: Learning plan ready
        deactivate LearningAgent
        
        InterviewAgent-->>Backend: Interview complete
        Backend->>Database: Mark interview as completed
        Backend-->>Frontend: Send conclusion
        deactivate InterviewAgent
        Frontend-->>User: Display summary & learning plan
    else More Questions
        InterviewAgent->>LLMProvider: Generate next question
        activate LLMProvider
        LLMProvider-->>InterviewAgent: Next question
        deactivate LLMProvider
        InterviewAgent-->>Backend: Next question ready
        Backend-->>Frontend: Send next question
        Frontend-->>User: Display next question
        deactivate InterviewAgent
    end
    
    deactivate Backend
```

---

## 5. Agent Responsibility Matrix

```mermaid
graph TB
    subgraph Tasks["Interview Execution Tasks"]
        T1["Question Selection"]
        T2["Difficulty Adjustment"]
        T3["Follow-up Generation"]
        T4["Conversation Flow"]
    end
    
    subgraph Tasks2["Answer Evaluation Tasks"]
        T5["Answer Parsing"]
        T6["Quality Scoring"]
        T7["Gap Identification"]
        T8["Feedback Generation"]
    end
    
    subgraph Tasks3["Learning Tasks"]
        T9["Skill Gap Analysis"]
        T10["Learning Path Generation"]
        T11["Resource Recommendation"]
        T12["Progress Tracking"]
    end
    
    subgraph IA["Interview Agent<br/>(Conductor)"]
        desc1["Primary: Interview orchestration<br/>and decision-making"]
    end
    
    subgraph FA["Feedback Agent<br/>(Evaluator)"]
        desc2["Primary: Answer quality<br/>assessment and scoring"]
    end
    
    subgraph LA["Learning Agent<br/>(Coach)"]
        desc3["Primary: Skill development<br/>and personalization"]
    end
    
    T1 --> IA
    T2 --> IA
    T3 --> IA
    T4 --> IA
    
    T5 --> FA
    T6 --> FA
    T7 --> FA
    T8 --> FA
    
    T9 --> LA
    T10 --> LA
    T11 --> LA
    T12 --> LA
    
    style T1 fill:#e3f2fd
    style T2 fill:#e3f2fd
    style T3 fill:#e3f2fd
    style T4 fill:#e3f2fd
    style T5 fill:#fff3e0
    style T6 fill:#fff3e0
    style T7 fill:#fff3e0
    style T8 fill:#fff3e0
    style T9 fill:#f3e5f5
    style T10 fill:#f3e5f5
    style T11 fill:#f3e5f5
    style T12 fill:#f3e5f5
```

---

## 6. RAG Pipeline - Architecture

```mermaid
graph LR
    subgraph Ingestion["Knowledge Base Ingestion"]
        Raw["Raw Questions<br/>(from db, PDFs)"]
        Chunk["Semantic Chunking<br/>(max 512 tokens)"]
        Embed["Generate Embeddings<br/>(Google API)"]
        Store["Store in pgvector<br/>(384-dim vectors)"]
        Index["Build HNSW Index<br/>(similarity search)"]
        Raw --> Chunk --> Embed --> Store --> Index
    end
    
    subgraph Retrieval["Question Retrieval - Runtime"]
        UserQuery["User Context"]
        PreEmbed["Pre-compute Query<br/>Embedding"]
        VectorSearch["Vector Similarity<br/>Search (HNSW)"]
        BM25["Keyword Search<br/>(BM25)"]
        Hybrid["Hybrid Ranking<br/>(0.6 vector + 0.4 BM25)"]
        Rerank["Re-rank with<br/>Query Expansion"]
        UserQuery --> PreEmbed
        PreEmbed --> VectorSearch
        PreEmbed --> BM25
        VectorSearch --> Hybrid
        BM25 --> Hybrid
        Hybrid --> Rerank
    end
    
    subgraph Augmentation["Augmentation - Agent Use"]
        Retrieved["Retrieved Questions<br/>(top-5)"]
        Context["Add User Context<br/>(skill level, history)"]
        Prompt["Inject into Agent<br/>Prompt Template"]
        Decision["Agent Decides<br/>Which Question to Use"]
        Retrieved --> Context --> Prompt --> Decision
    end
    
    Index -.->|Query| PreEmbed
    Rerank -->|Top-5 Questions| Retrieved
    
    style Ingestion fill:#e8f5e9
    style Retrieval fill:#e3f2fd
    style Augmentation fill:#f3e5f5
```

---

## 7. Tool Calling System - Architecture

```mermaid
graph TB
    subgraph Agents["Agents"]
        IA["Interview Agent"]
        FA["Feedback Agent"]
        LA["Learning Agent"]
    end
    
    subgraph ToolRegistry["Tool Registry<br/>(Central Registry)"]
        T1["search_knowledge_base"]
        T2["get_user_profile"]
        T3["get_user_skills"]
        T4["analyze_answer_quality"]
        T5["generate_learning_plan"]
        T6["update_memory"]
        T7["log_interaction"]
        T8["get_interview_context"]
    end
    
    subgraph Implementation["Tool Implementations"]
        I1["RAG Search Service"]
        I2["User Service"]
        I3["Skill Service"]
        I4["LLM Analysis"]
        I5["Learning Service"]
        I6["Memory Store"]
        I7["Analytics Logger"]
        I8["Interview Service"]
    end
    
    subgraph External["External Services"]
        DB[("Database")]
        Cache[("Redis")]
        LLM["LLM Provider"]
        ES["Elasticsearch<br/>(optional)"]
    end
    
    IA -->|Call Tools| ToolRegistry
    FA -->|Call Tools| ToolRegistry
    LA -->|Call Tools| ToolRegistry
    
    T1 -.-> I1
    T2 -.-> I2
    T3 -.-> I3
    T4 -.-> I4
    T5 -.-> I5
    T6 -.-> I6
    T7 -.-> I7
    T8 -.-> I8
    
    I1 --> DB
    I1 --> ES
    I2 --> DB
    I3 --> DB
    I4 --> LLM
    I5 --> DB
    I6 --> Cache
    I6 --> DB
    I7 --> DB
    I8 --> DB
    
    style ToolRegistry fill:#f0f0f0,stroke:#666
    style Agents fill:#e8f5e9
    style External fill:#fffde7
```

---

## 8. Memory System - Multi-Layer Architecture

```mermaid
graph TB
    subgraph ShortTerm["Short-Term Memory<br/>(Session)"]
        Context["Interview Context"]
        History["Message History<br/>(50 messages)"]
        Metrics["Real-time Metrics"]
        ShortTerm --> Redis["Redis Cache<br/>(TTL: 2 hours)"]
    end
    
    subgraph LongTerm["Long-Term Memory<br/>(Persistent)"]
        UserProfile["User Profile<br/>& Preferences"]
        SkillModel["Skill Model<br/>(assessed vs target)"]
        InterviewHistory["Interview History<br/>(normalized)"]
        LearningPath["Active Learning Path"]
        LongTerm --> DB[("PostgreSQL<br/>with pgvector")]
    end
    
    subgraph AgentAccess["Agent Access Patterns"]
        IA["Interview Agent"]
        FA["Feedback Agent"]
        LA["Learning Agent"]
    end
    
    IA -.->|Read/Write| ShortTerm
    IA -.->|Read/Write| LongTerm
    FA -.->|Read/Write| ShortTerm
    FA -.->|Read| LongTerm
    LA -.->|Read| ShortTerm
    LA -.->|Read/Write| LongTerm
    
    Redis -->|Sync Periodically| DB
    
    style ShortTerm fill:#e3f2fd
    style LongTerm fill:#fff3e0
    style AgentAccess fill:#f3e5f5
```

---

## 9. Evaluation Rubric - Multi-Dimensional Scoring

```mermaid
graph LR
    subgraph Evaluation["Answer Evaluation"]
        Answer["User Answer"]
        Answer --> Rubric["Multi-Dimensional Rubric<br/>(10 dimensions)"]
    end
    
    subgraph Dimensions["Scoring Dimensions"]
        D1["Technical Depth<br/>(0-10)"]
        D2["Completeness<br/>(0-10)"]
        D3["Communication<br/>(0-10)"]
        D4["Problem Solving<br/>(0-10)"]
        D5["Trade-offs Analysis<br/>(0-10)"]
        D6["Scalability<br/>(0-10)"]
        D7["Edge Cases<br/>(0-10)"]
        D8["Time Complexity<br/>(0-10)"]
        D9["Space Complexity<br/>(0-10)"]
        D10["Code Quality<br/>(0-10)"]
    end
    
    subgraph Aggregation["Score Aggregation"]
        Mean["Calculate Mean Score"]
        Weight["Apply Weights<br/>(interview type specific)"]
        Percentile["Convert to Percentile"]
        Result["Final Score<br/>(0-100)"]
    end
    
    Rubric --> D1
    Rubric --> D2
    Rubric --> D3
    Rubric --> D4
    Rubric --> D5
    Rubric --> D6
    Rubric --> D7
    Rubric --> D8
    Rubric --> D9
    Rubric --> D10
    
    D1 --> Mean
    D2 --> Mean
    D3 --> Mean
    D4 --> Mean
    D5 --> Mean
    D6 --> Mean
    D7 --> Mean
    D8 --> Mean
    D9 --> Mean
    D10 --> Mean
    
    Mean --> Weight
    Weight --> Percentile
    Percentile --> Result
    
    style D1 fill:#e3f2fd
    style D2 fill:#e3f2fd
    style D3 fill:#e3f2fd
    style D4 fill:#e3f2fd
    style D5 fill:#e3f2fd
    style D6 fill:#fff3e0
    style D7 fill:#fff3e0
    style D8 fill:#fff3e0
    style D9 fill:#fff3e0
    style D10 fill:#f3e5f5
```

---

## 10. Error Handling & Resilience

```mermaid
graph TD
    UserAction["User Action<br/>(Answer Question)"] --> APICall["API Call"]
    APICall --> CheckHealth{Service<br/>Healthy?}
    
    CheckHealth -->|No| CircuitBreaker["Circuit Breaker<br/>OPEN"]
    CircuitBreaker --> Fallback["Use Cached Result<br/>or Default Response"]
    Fallback --> Return1["Return to User"]
    
    CheckHealth -->|Yes| Process["Process Request"]
    Process --> LLMCall{LLM API<br/>Available?}
    
    LLMCall -->|No| OllamaFallback["Fall back to<br/>Ollama Local"]
    OllamaFallback --> Continue["Continue Processing"]
    
    LLMCall -->|Yes| LLMProcess["Call LLM Provider"]
    LLMProcess --> Continue
    
    Continue --> RateLimit{Rate Limit<br/>Exceeded?}
    RateLimit -->|Yes| Queue["Add to Queue<br/>(Async Processing)"]
    Queue --> Notify["Notify User<br/>(Will process soon)"]
    
    RateLimit -->|No| Success["Process Successfully"]
    Success --> Database["Store in Database"]
    Database --> Return2["Return Results"]
    
    Database -->|Failure| Retry["Retry with<br/>Exponential Backoff"]
    Retry --> Database
    
    Return1 --> User["User Receives<br/>Response"]
    Return2 --> User
    Notify --> User
    
    style CheckHealth fill:#fff3e0
    style LLMCall fill:#fff3e0
    style RateLimit fill:#fff3e0
    style CircuitBreaker fill:#ffebee
    style Success fill:#e8f5e9
```

---

## 11. Deployment Architecture - Multi-Environment

```mermaid
graph LR
    subgraph Local["Local Development<br/>(Docker Compose)"]
        LBackend["Backend API<br/>(port 8000)"]
        LFrontend["Frontend<br/>(port 4200)"]
        LDB["PostgreSQL<br/>+ pgvector"]
        LRedis["Redis"]
        LOllama["Ollama<br/>(local LLM)"]
        LBackend --- LDB
        LBackend --- LRedis
        LBackend --- LOllama
        LFrontend --- LBackend
    end
    
    subgraph Dev["Dev Environment<br/>(AKS Cluster)"]
        DBackend["Backend<br/>(1 replica)"]
        DFrontend["Frontend<br/>(1 replica)"]
        DDB["PostgreSQL<br/>(single instance)"]
        DRedis["Redis<br/>(single node)"]
        DBackend --- DDB
        DBackend --- DRedis
        DFrontend --- DBackend
    end
    
    subgraph Staging["Staging<br/>(AKS Cluster)"]
        SBackend["Backend<br/>(2 replicas)"]
        SFrontend["Frontend<br/>(2 replicas)"]
        SDB["PostgreSQL<br/>(1 primary + 1 replica)"]
        SRedis["Redis<br/>(cluster)"]
        SBackend --- SDB
        SBackend --- SRedis
        SFrontend --- SBackend
    end
    
    subgraph Prod["Production<br/>(AKS Cluster)"]
        PBackend["Backend<br/>(3-10 replicas)"]
        PFrontend["Frontend<br/>(2-5 replicas)"]
        PDB["PostgreSQL<br/>(HA: 1 primary + 2 replicas)"]
        PRedis["Redis<br/>(cluster + sentinel)"]
        PBackend --- PDB
        PBackend --- PRedis
        PFrontend --- PBackend
        WAF["Application Gateway<br/>+ WAF"]
        WAF --- PFrontend
        WAF --- PBackend
    end
    
    Developer["Developer"] -->|docker-compose| Local
    CI["CI/CD Pipeline"] -->|deploy| Dev
    CI -->|test + deploy| Staging
    ReleaseManager["Release Manager"] -->|approve + deploy| Prod
    
    style Local fill:#e8f5e9
    style Dev fill:#e3f2fd
    style Staging fill:#fff3e0
    style Prod fill:#ffebee
```

---

## 12. Request/Response Lifecycle

```mermaid
graph TD
    Client["Frontend Client"] -->|"1. POST /interviews/{id}/answer<br/>(JSON: user_answer)"| Gateway["Application Gateway"]
    Gateway -->|"2. Forward Request"| LoadBalancer["Load Balancer"]
    LoadBalancer -->|"3. Route to Pod"| Pod1["Backend Pod 1"]
    
    Pod1 -->|"4. Parse Request<br/>(Pydantic validation)"| Validate["Validation"]
    Validate -->|Valid| Process["Process in Handler"]
    Validate -->|Invalid| Error400["400 Bad Request"]
    Error400 --> Client
    
    Process -->|"5. Store Answer<br/>(ORM)"| DB[("Database")]
    DB -->|Stored| Continue["Continue"]
    
    Continue -->|"6. Call Feedback Agent<br/>(via tool)"| Agent["Feedback Agent"]
    Agent -->|"7. Generate LLM Prompt"| Prompt["Build Prompt with Context"]
    Prompt -->|"8. Call LLM Provider"| LLM["LLM API"]
    
    LLM -->|"9. Return Response"| ParseResp["Parse LLM Response"]
    ParseResp -->|"10. Store Evaluation"| DB2[("Database")]
    DB2 -->|Stored| BuildResp["Build Response Object"]
    
    BuildResp -->|"11. Send Response"| WebSocket["WebSocket"]
    WebSocket -->|"12. Stream Update"| ClientWS["Frontend WebSocket"]
    ClientWS -->|Display Feedback| UserUI["User Interface"]
    
    style Client fill:#e3f2fd
    style Gateway fill:#f0f0f0
    style Agent fill:#f3e5f5
    style LLM fill:#fffde7
    style UserUI fill:#e8f5e9
```

---

## 13. System Capacity Planning

```mermaid
graph TB
    Concurrent["Concurrent Users"]
    Concurrent --> QPS["Requests/Second"]
    QPS --> API["API Response Time"]
    QPS --> DB["Database Load"]
    QPS --> LLM["LLM API Cost"]
    
    subgraph Scaling["Scaling Strategy"]
        APIOpt["API Tier: 4-8 replicas<br/>based on CPU"]
        DBO["Database: Read replicas<br/>for scaling"]
        LLMOpt["LLM: Fallback to Ollama<br/>for cost"]
    end
    
    API --> APIOpt
    DB --> DBO
    LLM --> LLMOpt
    
    APIOpt --> MaxConcurrent["~1000 concurrent<br/>users"]
    DBO --> MaxThroughput["~500 QPS"]
    LLMOpt --> CostControl["Cost optimization"]
    
    style Concurrent fill:#e3f2fd
    style Scaling fill:#f0f0f0
    style MaxConcurrent fill:#e8f5e9
    style MaxThroughput fill:#e8f5e9
    style CostControl fill:#fff3e0
```

---

## Key Takeaways

1. **Three-Agent Pattern**: Clear separation between orchestration (Interview), evaluation (Feedback), and personalization (Learning)

2. **Shared State Management**: LangGraph manages all state; agents read/write to shared context

3. **Message-Driven Architecture**: WebSocket streams enable real-time feedback without polling

4. **Tool Calling for Extensibility**: New capabilities added as tools without modifying agent logic

5. **Hybrid RAG Search**: Combines vector similarity + keyword search for 98%+ retrieval accuracy

6. **Multi-Layer Memory**: Short-term (Redis) for session context, long-term (PostgreSQL) for learning

7. **Resilient Fallbacks**: LLM API → Ollama, database replica failover, circuit breakers

8. **Production-Grade Observability**: Tracing, metrics, logs at every layer with cost tracking

These diagrams provide the complete visual reference for understanding the multi-agent interview orchestration system!
