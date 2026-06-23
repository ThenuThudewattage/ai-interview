# Project Folder Structure & Organization

## Directory Layout

```
ai-interview-helper/
├── README.md                                    # Project overview
├── LICENSE                                      # MIT License
├── .gitignore                                   # Git ignore rules
├── .env.example                                 # Environment variables template
├── docker-compose.yml                           # Local dev environment
├── docker-compose.prod.yml                      # Production setup
│
├── backend/                                     # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                              # FastAPI app entry point
│   │   ├── config.py                            # Configuration management
│   │   │
│   │   ├── api/                                 # API layer (routes)
│   │   │   ├── __init__.py
│   │   │   ├── router.py                        # Main API router
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                      # Authentication endpoints
│   │   │   │   ├── users.py                     # User management
│   │   │   │   ├── interviews.py                # Interview endpoints
│   │   │   │   ├── evaluations.py               # Evaluation endpoints
│   │   │   │   ├── learning.py                  # Learning plan endpoints
│   │   │   │   ├── analytics.py                 # Analytics endpoints
│   │   │   │   ├── knowledge_base.py            # Knowledge base search
│   │   │   │   └── websocket.py                 # WebSocket endpoints
│   │   │   ├── middleware/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                      # JWT authentication
│   │   │   │   ├── error_handler.py             # Error handling
│   │   │   │   ├── rate_limiter.py              # Rate limiting
│   │   │   │   └── logger.py                    # Request logging
│   │   │   └── schemas/                         # Pydantic models
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── interview.py
│   │   │       ├── evaluation.py
│   │   │       └── learning.py
│   │   │
│   │   ├── agents/                              # Multi-agent orchestration
│   │   │   ├── __init__.py
│   │   │   ├── interview_agent.py               # Interview conductor
│   │   │   ├── feedback_agent.py                # Answer evaluator
│   │   │   ├── learning_agent.py                # Learning coach
│   │   │   ├── base_agent.py                    # Base agent class
│   │   │   ├── prompts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── interview_system.py
│   │   │   │   ├── feedback_system.py
│   │   │   │   └── learning_system.py
│   │   │   ├── tools/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── knowledge_base.py
│   │   │   │   ├── user_profile.py
│   │   │   │   ├── skill_analyzer.py
│   │   │   │   └── memory_manager.py
│   │   │   └── workflows/
│   │   │       ├── __init__.py
│   │   │       ├── interview_workflow.py        # LangGraph workflow
│   │   │       ├── states.py                    # State schemas
│   │   │       └── nodes.py                     # Workflow nodes
│   │   │
│   │   ├── services/                            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── interview_service.py
│   │   │   ├── evaluation_service.py
│   │   │   ├── learning_service.py
│   │   │   ├── rag_service.py                   # RAG retrieval
│   │   │   ├── embedding_service.py             # Embedding generation
│   │   │   ├── skill_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── llm_service.py                   # LLM API management
│   │   │
│   │   ├── repositories/                        # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── interview_repository.py
│   │   │   ├── answer_repository.py
│   │   │   ├── evaluation_repository.py
│   │   │   ├── question_repository.py
│   │   │   ├── skill_repository.py
│   │   │   ├── learning_plan_repository.py
│   │   │   └── document_repository.py
│   │   │
│   │   ├── models/                              # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── interview.py
│   │   │   ├── question.py
│   │   │   ├── answer.py
│   │   │   ├── evaluation.py
│   │   │   ├── skill.py
│   │   │   ├── learning_plan.py
│   │   │   ├── document.py
│   │   │   └── base.py                         # Base model class
│   │   │
│   │   ├── db/                                  # Database configuration
│   │   │   ├── __init__.py
│   │   │   ├── database.py                      # DB connection
│   │   │   ├── session.py                       # Session management
│   │   │   ├── migrations/
│   │   │   │   ├── env.py
│   │   │   │   ├── script.py.mako
│   │   │   │   └── versions/
│   │   │   │       ├── 001_initial_schema.py
│   │   │   │       ├── 002_add_embeddings.py
│   │   │   │       └── 003_add_rag_cache.py
│   │   │   └── seeds/
│   │   │       ├── __init__.py
│   │   │       ├── skill_areas.py               # Seed initial skills
│   │   │       └── sample_questions.py          # Sample Q&A data
│   │   │
│   │   ├── core/                                # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py                      # JWT, hashing
│   │   │   ├── exceptions.py
│   │   │   ├── constants.py
│   │   │   ├── enums.py
│   │   │   └── decorators.py
│   │   │
│   │   ├── utils/                               # Helper utilities
│   │   │   ├── __init__.py
│   │   │   ├── validators.py
│   │   │   ├── formatters.py
│   │   │   ├── cache.py                         # Redis operations
│   │   │   ├── logging.py                       # Structured logging
│   │   │   ├── metrics.py                       # Metrics collection
│   │   │   ├── tracing.py                       # OpenTelemetry
│   │   │   └── cost_tracker.py
│   │   │
│   │   └── external/                            # External integrations
│   │       ├── __init__.py
│   │       ├── llm/
│   │       │   ├── __init__.py
│   │       │   ├── gemini_client.py
│   │       │   ├── openrouter_client.py
│   │       │   ├── ollama_client.py
│   │       │   └── base_client.py
│   │       ├── embedding/
│   │       │   ├── __init__.py
│   │       │   ├── google_embedding.py
│   │       │   ├── huggingface_embedding.py
│   │       │   └── base_embedding.py
│   │       └── storage/
│   │           ├── __init__.py
│   │           ├── s3_client.py
│   │           ├── local_storage.py
│   │           └── base_storage.py
│   │
│   ├── tests/                                   # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py                          # Pytest configuration
│   │   ├── fixtures/
│   │   │   ├── __init__.py
│   │   │   ├── user_fixtures.py
│   │   │   ├── interview_fixtures.py
│   │   │   └── mock_data.py
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── services/
│   │   │   │   ├── test_user_service.py
│   │   │   │   ├── test_interview_service.py
│   │   │   │   └── test_evaluation_service.py
│   │   │   ├── agents/
│   │   │   │   ├── test_interview_agent.py
│   │   │   │   └── test_feedback_agent.py
│   │   │   └── utils/
│   │   │       └── test_validators.py
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_interview_flow.py
│   │   │   ├── test_api_endpoints.py
│   │   │   ├── test_database.py
│   │   │   └── test_rag_pipeline.py
│   │   └── e2e/
│   │       ├── __init__.py
│   │       ├── test_full_interview.py
│   │       └── test_learning_flow.py
│   │
│   ├── scripts/                                 # Utility scripts
│   │   ├── __init__.py
│   │   ├── seed_database.py                     # Populate initial data
│   │   ├── generate_embeddings.py               # Generate knowledge base embeddings
│   │   ├── migrate_data.py                      # Data migration utilities
│   │   └── cleanup.py                           # Cleanup utilities
│   │
│   ├── requirements.txt                         # Python dependencies
│   ├── pyproject.toml                           # Project metadata
│   ├── Dockerfile                               # Docker image
│   └── .dockerignore
│
├── frontend/                                    # Angular frontend
│   ├── angular.json                             # Angular configuration
│   ├── tsconfig.json                            # TypeScript configuration
│   ├── package.json                             # Node dependencies
│   ├── package-lock.json
│   │
│   ├── src/
│   │   ├── main.ts                              # Application entry point
│   │   ├── index.html
│   │   ├── styles.scss                          # Global styles
│   │   │
│   │   ├── app/
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   ├── app.routing.module.ts
│   │   │   │
│   │   │   ├── core/                            # Singleton services
│   │   │   │   ├── guards/
│   │   │   │   │   ├── auth.guard.ts
│   │   │   │   │   └── role.guard.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── auth.service.ts
│   │   │   │   │   ├── http.service.ts
│   │   │   │   │   ├── storage.service.ts
│   │   │   │   │   └── error.service.ts
│   │   │   │   └── interceptors/
│   │   │   │       ├── auth.interceptor.ts
│   │   │   │       ├── error.interceptor.ts
│   │   │   │       └── loading.interceptor.ts
│   │   │   │
│   │   │   ├── shared/                         # Shared components/directives
│   │   │   │   ├── components/
│   │   │   │   │   ├── navbar/
│   │   │   │   │   ├── loading-spinner/
│   │   │   │   │   ├── error-dialog/
│   │   │   │   │   └── confirmation-dialog/
│   │   │   │   ├── directives/
│   │   │   │   ├── pipes/
│   │   │   │   ├── models/
│   │   │   │   │   ├── user.model.ts
│   │   │   │   │   ├── interview.model.ts
│   │   │   │   │   ├── evaluation.model.ts
│   │   │   │   │   └── learning.model.ts
│   │   │   │   └── shared.module.ts
│   │   │   │
│   │   │   ├── modules/
│   │   │   │   ├── auth/
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── login/
│   │   │   │   │   │   ├── register/
│   │   │   │   │   │   └── forgot-password/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── auth.service.ts
│   │   │   │   │   └── auth.module.ts
│   │   │   │   │
│   │   │   │   ├── dashboard/
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── dashboard-overview/
│   │   │   │   │   │   ├── skill-chart/
│   │   │   │   │   │   ├── recent-interviews/
│   │   │   │   │   │   └── recommendations/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── dashboard.service.ts
│   │   │   │   │   └── dashboard.module.ts
│   │   │   │   │
│   │   │   │   ├── interview/
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── interview-start/
│   │   │   │   │   │   ├── interview-conductor/
│   │   │   │   │   │   ├── question-display/
│   │   │   │   │   │   ├── answer-input/
│   │   │   │   │   │   ├── evaluation-display/
│   │   │   │   │   │   └── interview-complete/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   ├── interview.service.ts
│   │   │   │   │   │   └── websocket.service.ts
│   │   │   │   │   ├── state/
│   │   │   │   │   │   └── interview.store.ts
│   │   │   │   │   └── interview.module.ts
│   │   │   │   │
│   │   │   │   ├── learning/
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── learning-dashboard/
│   │   │   │   │   │   ├── skill-gaps/
│   │   │   │   │   │   ├── learning-roadmap/
│   │   │   │   │   │   └── resource-viewer/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── learning.service.ts
│   │   │   │   │   └── learning.module.ts
│   │   │   │   │
│   │   │   │   ├── profile/
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── profile-view/
│   │   │   │   │   │   ├── profile-edit/
│   │   │   │   │   │   ├── resume-upload/
│   │   │   │   │   │   └── preferences/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── profile.service.ts
│   │   │   │   │   └── profile.module.ts
│   │   │   │   │
│   │   │   │   ├── analytics/
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── analytics-dashboard/
│   │   │   │   │   │   ├── score-chart/
│   │   │   │   │   │   ├── skill-heatmap/
│   │   │   │   │   │   └── progress-tracker/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── analytics.service.ts
│   │   │   │   │   └── analytics.module.ts
│   │   │   │   │
│   │   │   │   └── interview-history/
│   │   │   │       ├── components/
│   │   │   │       │   ├── history-list/
│   │   │   │       │   ├── interview-detail/
│   │   │   │       │   └── performance-review/
│   │   │   │       ├── services/
│   │   │   │       │   └── history.service.ts
│   │   │   │       └── interview-history.module.ts
│   │   │   │
│   │   │   └── app.module.ts
│   │   │
│   │   └── environments/
│   │       ├── environment.ts
│   │       └── environment.prod.ts
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── components/
│   │   │   └── services/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── Dockerfile
│   └── .dockerignore
│
├── infrastructure/                              # IaC and deployment
│   ├── docker/
│   │   ├── backend.Dockerfile                  # Backend image
│   │   └── frontend.Dockerfile                 # Frontend image
│   │
│   ├── kubernetes/
│   │   ├── base/
│   │   │   ├── namespace.yaml
│   │   │   ├── configmap.yaml
│   │   │   ├── secret.yaml
│   │   │   ├── backend-deployment.yaml
│   │   │   ├── backend-service.yaml
│   │   │   ├── frontend-deployment.yaml
│   │   │   ├── frontend-service.yaml
│   │   │   ├── postgres-statefulset.yaml
│   │   │   ├── redis-deployment.yaml
│   │   │   └── ingress.yaml
│   │   │
│   │   ├── overlays/
│   │   │   ├── dev/
│   │   │   │   ├── kustomization.yaml
│   │   │   │   └── patches/
│   │   │   ├── staging/
│   │   │   │   ├── kustomization.yaml
│   │   │   │   └── patches/
│   │   │   └── prod/
│   │   │       ├── kustomization.yaml
│   │   │       └── patches/
│   │   │
│   │   ├── helm/
│   │   │   ├── Chart.yaml
│   │   │   ├── values.yaml
│   │   │   ├── values-dev.yaml
│   │   │   ├── values-prod.yaml
│   │   │   └── templates/
│   │   │       ├── deployment.yaml
│   │   │       ├── service.yaml
│   │   │       ├── ingress.yaml
│   │   │       └── configmap.yaml
│   │   │
│   │   └── manifests/
│   │       ├── monitoring/
│   │       │   ├── prometheus-values.yaml
│   │       │   └── grafana-values.yaml
│   │       ├── logging/
│   │       │   └── loki-values.yaml
│   │       └── tracing/
│   │           └── jaeger-values.yaml
│   │
│   ├── terraform/
│   │   ├── main.tf                              # Main TF configuration
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── backend.tf                           # Remote state
│   │   │
│   │   ├── modules/
│   │   │   ├── networking/
│   │   │   │   ├── main.tf
│   │   │   │   └── variables.tf
│   │   │   ├── database/
│   │   │   │   ├── main.tf
│   │   │   │   └── variables.tf
│   │   │   ├── cache/
│   │   │   │   ├── main.tf
│   │   │   │   └── variables.tf
│   │   │   ├── container_registry/
│   │   │   │   ├── main.tf
│   │   │   │   └── variables.tf
│   │   │   └── aks_cluster/
│   │   │       ├── main.tf
│   │   │       ├── variables.tf
│   │   │       └── node_pool.tf
│   │   │
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   │   ├── terraform.tfvars
│   │   │   │   └── backend.tf
│   │   │   ├── staging/
│   │   │   │   ├── terraform.tfvars
│   │   │   │   └── backend.tf
│   │   │   └── prod/
│   │   │       ├── terraform.tfvars
│   │   │       └── backend.tf
│   │   │
│   │   └── scripts/
│   │       ├── deploy.sh
│   │       ├── destroy.sh
│   │       └── plan.sh
│   │
│   └── docker-compose.yml                       # Local dev compose
│
├── docs/                                        # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── DEPLOYMENT.md
│   ├── CONTRIBUTING.md
│   ├── DEVELOPMENT.md
│   └── TROUBLESHOOTING.md
│
├── .github/                                     # GitHub configuration
│   ├── workflows/
│   │   ├── ci.yml                               # CI pipeline
│   │   ├── deploy-dev.yml                       # Deploy to dev
│   │   ├── deploy-staging.yml                   # Deploy to staging
│   │   ├── deploy-prod.yml                      # Deploy to prod
│   │   └── security.yml                         # Security scanning
│   │
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   │
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .env.example                                 # Environment template
├── .dockerignore
├── .gitignore
├── Makefile                                     # Development commands
└── README.md                                    # Main documentation
```

---

## Key Directory Descriptions

### `/backend/app/`
- **Purpose**: Core Python application code
- **Structure**: Follows Hexagonal Architecture with clear separation of concerns
- **Key Patterns**: Dependency injection, repository pattern, service layer

### `/backend/app/agents/`
- **Purpose**: Multi-agent orchestration
- **Contains**: Agent classes, prompts, tools, workflows
- **Key**: Each agent is independent, communication via message passing

### `/backend/app/services/`
- **Purpose**: Business logic encapsulation
- **Responsibility**: Orchestrate repositories, external services, and agents
- **Example**: `interview_service` coordinates interview flow, RAG retrieval, and agent calls

### `/backend/app/repositories/`
- **Purpose**: Data access abstraction
- **Benefit**: Easy to swap implementations (SQL, cache, etc.)
- **Pattern**: Each entity has dedicated repository

### `/frontend/src/app/modules/`
- **Purpose**: Feature modules organized by domain
- **Structure**: Each module has components, services, and models
- **Pattern**: Lazy loading per module for performance

### `/infrastructure/`
- **Purpose**: Infrastructure as Code and deployment
- **Options**: Kubernetes (Kustomize, Helm) and Terraform
- **Environments**: dev, staging, prod with separate configs

---

## File Naming Conventions

```
Python Files:
├─ snake_case.py (modules, functions)
├─ PascalCase (classes)
└─ Constants: UPPER_SNAKE_CASE

TypeScript Files:
├─ kebab-case.ts (files)
├─ PascalCase (classes, interfaces)
├─ camelCase (functions, properties)
└─ UPPER_CASE (constants)

Database:
├─ snake_case (tables, columns)
├─ plural (table names: users, interviews)
└─ _id suffix (foreign keys: user_id)
```

---

## Key Dependencies by Layer

### Backend
```
Core:
├─ FastAPI: Web framework
├─ Pydantic: Data validation
├─ SQLAlchemy: ORM
└─ Alembic: Migrations

AI/ML:
├─ LangGraph: Agent orchestration
├─ PydanticAI: Agent framework
├─ Anthropic: Claude client
└─ OpenAI: GPT client

Data:
├─ psycopg2: PostgreSQL driver
├─ pgvector: Vector operations
├─ Redis: Caching
└─ SQLAlchemy-Utils: DB utilities

Observability:
├─ Structlog: Structured logging
├─ OpenTelemetry: Tracing
├─ Prometheus: Metrics
└─ Pydantic Settings: Config management

Testing:
├─ pytest: Test framework
├─ pytest-asyncio: Async testing
├─ TestContainers: Database testing
└─ unittest.mock: Mocking
```

### Frontend
```
Core:
├─ @angular/core
├─ @angular/material
├─ RxJS: Reactive programming
└─ TypeScript

HTTP:
├─ @angular/common/http
└─ ngx-http-client-utils

State:
├─ @ngrx/store (optional for scalability)
└─ Service-based state (for MVP)

Testing:
├─ Jasmine
├─ Karma
└─ Cypress (E2E)
```

---

## Environment Management

```
.env structure:

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_interview
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379

# LLM APIs
GEMINI_API_KEY=xxx
OPENROUTER_API_KEY=xxx
OLLAMA_BASE_URL=http://localhost:11434

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRY_HOURS=24

# Storage
STORAGE_PROVIDER=s3  # s3 or local
S3_BUCKET=ai-interview-bucket
S3_REGION=us-east-1

# Observability
TRACING_ENABLED=true
LOG_LEVEL=INFO

# Feature Flags
ENABLE_VECTOR_SEARCH=true
ENABLE_LEARNING_AGENT=true
```

---

## Development Workflow

```
Start development:
$ make dev                  # Start docker-compose with all services

Backend development:
$ cd backend/
$ python -m uvicorn app.main:app --reload

Frontend development:
$ cd frontend/
$ ng serve

Run tests:
$ make test-backend
$ make test-frontend

Database migration:
$ cd backend/
$ alembic upgrade head

Code quality:
$ make lint
$ make format
$ make type-check

Build for production:
$ docker-compose -f docker-compose.prod.yml build
```

This structure provides:
- ✅ Clear separation of concerns
- ✅ Scalability (modular architecture)
- ✅ Testability (layers, dependency injection)
- ✅ Maintainability (consistent conventions)
- ✅ DevOps-friendly (IaC, containerized)
