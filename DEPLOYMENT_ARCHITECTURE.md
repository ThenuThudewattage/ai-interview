# Deployment Architecture & Infrastructure Strategy

## Overview

This document details the deployment architecture, infrastructure setup, CI/CD pipelines, and operational procedures for the AI Interview Intelligence Platform.

---

## 1. Multi-Environment Architecture

### 1.1 Environment Strategy

```
┌─────────────────────────────────────────────────────────────┐
│              Development Environment (dev)                  │
│  • Local docker-compose for rapid iteration                 │
│  • Seeded test data                                         │
│  • Full observability (all logs, traces)                    │
│  • Direct API access (no auth requirements)                 │
│  • Feature flags enabled for experimentation                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            Staging Environment (staging)                     │
│  • AKS cluster with 2 nodes                                 │
│  • Production-like configuration                            │
│  • Load balancing enabled                                   │
│  • Data anonymized from production                          │
│  • Performance testing environment                          │
│  • Security scanning enabled                                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          Production Environment (prod)                       │
│  • AKS cluster with auto-scaling (3-10 nodes)              │
│  • Multi-AZ deployment for HA                              │
│  • Database read replicas                                  │
│  • Redis cluster with sentinel                             │
│  • WAF and DDoS protection                                 │
│  • Blue-green deployment strategy                          │
│  • Real-time monitoring and alerting                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Environment-Specific Configuration

```yaml
# dev
DATABASE_REPLICAS: 0
CACHE_MODE: standalone
LLM_RATE_LIMIT: unlimited
AUTO_SCALING: false
LOG_LEVEL: DEBUG
ENABLE_PROFILING: true

# staging
DATABASE_REPLICAS: 1
CACHE_MODE: cluster
LLM_RATE_LIMIT: 1000/hour
AUTO_SCALING: true (2-5)
LOG_LEVEL: INFO
ENABLE_PROFILING: false

# production
DATABASE_REPLICAS: 2
CACHE_MODE: cluster_with_sentinel
LLM_RATE_LIMIT: rate_limit_per_user
AUTO_SCALING: true (3-10)
LOG_LEVEL: WARN
ENABLE_PROFILING: false
```

---

## 2. Azure Infrastructure Design

### 2.1 High-Level Azure Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      Azure Subscription                         │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Resource Group: ai-interview-platform-prod             │  │
│  │                                                         │  │
│  │ ┌───────────────────────────────────────────────────┐  │  │
│  │ │ Virtual Network (10.0.0.0/16)                    │  │  │
│  │ │ • Subnet-1: AKS Nodes (10.0.1.0/24)            │  │  │
│  │ │ • Subnet-2: Database (10.0.2.0/24)             │  │  │
│  │ │ • Subnet-3: Cache (10.0.3.0/24)                │  │  │
│  │ │ • Subnet-4: Bastion/Jumpbox (10.0.4.0/24)      │  │  │
│  │ └───────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │ ┌──────────────────┐  ┌───────────────────────────┐  │  │
│  │ │ Application      │  │ Storage & Database        │  │  │
│  │ │ Gateway          │  │                           │  │  │
│  │ │ (WAF Enabled)    │  │ • Azure PostgreSQL Server│  │  │
│  │ │                  │  │   - HA-enabled           │  │  │
│  │ │                  │  │   - Read replicas        │  │  │
│  │ │                  │  │ • Azure Cache for Redis  │  │  │
│  │ │                  │  │ • Azure Blob Storage     │  │  │
│  │ │                  │  │ • Azure Cosmos DB (opt)  │  │  │
│  │ └──────────────────┘  └───────────────────────────┘  │  │
│  │         │                                              │  │
│  │         ▼                                              │  │
│  │  ┌────────────────────────────────────────┐           │  │
│  │  │ Azure Kubernetes Service (AKS)         │           │  │
│  │  │ • 3-10 nodes (auto-scaling)            │           │  │
│  │  │ • System node pool: 2 nodes (d-series) │           │  │
│  │  │ • User node pool: 1-8 nodes (f-series) │           │  │
│  │  │                                         │           │  │
│  │  │ ┌─────────────────────────────────────┐│           │  │
│  │  │ │ Workloads:                          ││           │  │
│  │  │ │ • Backend API (3+ replicas)         ││           │  │
│  │  │ │ • Frontend (2+ replicas)            ││           │  │
│  │  │ │ • Background Jobs                   ││           │  │
│  │  │ │ • Monitoring Stack                  ││           │  │
│  │  │ └─────────────────────────────────────┘│           │  │
│  │  └────────────────────────────────────────┘           │  │
│  │         │                                              │  │
│  │  Monitoring & Logging                                 │  │
│  │  • Azure Monitor (Metrics, Alerts)                    │  │
│  │  • Log Analytics (Logs)                               │  │
│  │  • Application Insights (APM)                         │  │
│  │  • Azure DevOps (Pipelines, Repos)                    │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Details

#### Application Gateway with WAF

```yaml
Azure Application Gateway:
  SKU: WAF_v2
  Min Instances: 2
  Max Instances: 10
  Auto-scaling: enabled
  
  Rules:
    - Rate Limiting: 1000 req/minute per IP
    - IP Whitelisting: (Optional)
    - Web Application Firewall: OWASP Top 10 protection
    
  Backends:
    - Backend Pool 1: AKS Service (Backend API)
    - Backend Pool 2: AKS Service (Frontend)
    
  Routing Rules:
    - /api/* -> Backend API
    - / -> Frontend
```

#### AKS Cluster Configuration

```yaml
AKS Cluster:
  Name: ai-interview-aks-prod
  Kubernetes Version: 1.30+
  Network Plugin: Azure CNI
  
  System Node Pool:
    VM Size: Standard_D2s_v3 (2 vCPU, 8GB RAM)
    Count: 2 (fixed)
    OS Disk Size: 128GB
    
  User Node Pool:
    VM Size: Standard_F4s_v2 (4 vCPU, 8GB RAM)
    Min Count: 1
    Max Count: 8
    Auto-scale: enabled
    
  Addons:
    - HTTP Application Routing: enabled
    - Azure Monitor: enabled
    - Monitoring: enabled
```

#### Database Configuration

```yaml
Azure Database for PostgreSQL:
  Service Tier: Standard (B, General Purpose, Memory Optimized)
  Sku: Standard_B2s (for dev/staging)
          Standard_D4s_v3 (for prod)
  
  High Availability:
    Enabled: true
    Standby Replica: Same AZ or different AZ
    
  Backups:
    Retention: 35 days
    Geo-redundant: enabled
    
  Performance:
    Storage: 100GB-4TB (auto-grow)
    IOPS: 3100-40000
    
  Extensions:
    - pgvector (for embeddings)
    - uuid-ossp (for UUIDs)
    - pg_stat_statements (monitoring)
```

#### Redis Cache

```yaml
Azure Cache for Redis:
  SKU: Standard or Premium
  Size: C1 (dev), C2 (staging), C3+ (prod)
  Replication: enabled
  High Availability: enabled (Premium)
  
  Persistence:
    RDB Snapshot: daily
    AOF Persistence: enabled (Premium)
    
  Network:
    Virtual Network: integrated
    Firewall: enabled
    Private Link: enabled (Premium)
```

---

## 3. CI/CD Pipeline Architecture

### 3.1 GitHub Actions Pipeline

```yaml
Trigger: On push to main/develop, PR creation

┌─────────────────────────────────────────────────────────────┐
│ CI Pipeline (Continuous Integration)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Stage 1: Code Quality Checks                               │
│   ├─ Linting (Backend: pylint, Frontend: eslint)          │
│   ├─ Type Checking (Backend: mypy, Frontend: tsc)         │
│   ├─ Code Formatting (Backend: black, Frontend: prettier) │
│   └─ SAST (SonarQube, Snyk)                               │
│                                                              │
│ Stage 2: Unit & Integration Tests                          │
│   ├─ Backend: pytest with coverage (>80%)                │
│   ├─ Frontend: Jest with coverage (>75%)                 │
│   ├─ Database: Integration tests with TestContainers     │
│   └─ API: Contract tests                                  │
│                                                              │
│ Stage 3: Build Docker Images                              │
│   ├─ Backend image (Python:3.11-slim)                    │
│   ├─ Frontend image (Node:20-alpine → nginx)             │
│   ├─ Security scanning (Trivy, Grype)                    │
│   └─ Push to Container Registry                          │
│                                                              │
│ Stage 4: Artifact Generation                              │
│   ├─ Generate SBOM (Software Bill of Materials)          │
│   ├─ Create release notes                                │
│   └─ Tag images with git commit SHA                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │ Approval Gate (Manual Review)  │
            └───────────────┬───────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
    [Deploy to DEV]                     [Deploy to STAGING]
        │                                       │
        ▼                                       ▼
    [Smoke Tests]                       [Full Test Suite]
        │                                       │
        ▼                                       ▼
    [E2E Tests]                         [Load Tests]
        │                                       │
        └───────────────┬───────────────────────┘
                        │
                        ▼
            ┌───────────────────────────────┐
            │ Approval Gate (Release Lead)   │
            └───────────────┬───────────────┘
                            │
                            ▼
                  [Deploy to PRODUCTION]
                            │
                            ▼
                  [Health Checks]
                            │
                            ▼
                  [Blue-Green Cutover]
                            │
                            ▼
                  [Smoke Tests]
                            │
                            ▼
                 [Monitor for Issues]
```

### 3.2 GitHub Actions Workflow Definition

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Backend Linting
        run: |
          pip install pylint
          pylint backend/app --exit-zero
      
      - name: Backend Type Check
        run: |
          pip install mypy
          mypy backend/app
      
      - name: Frontend Linting
        run: |
          cd frontend
          npm ci
          npm run lint
      
      - name: Security Scanning
        run: |
          npm install -g snyk
          snyk test --severity-threshold=high

  unit-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-pgvector
        env:
          POSTGRES_DB: test
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      
      - name: Backend Unit Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/unit --cov=app --cov-report=xml
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
      
      - name: Frontend Unit Tests
        run: |
          cd frontend
          npm ci
          npm run test:coverage

  build-images:
    needs: [code-quality, unit-tests]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and Push Backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Build and Push Frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Scan Images
        run: |
          npm install -g trivy
          trivy image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ github.sha }}
          trivy image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ github.sha }}

  deploy-dev:
    needs: build-images
    runs-on: ubuntu-latest
    environment:
      name: development
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Dev
        run: |
          ./infrastructure/scripts/deploy.sh dev ${{ github.sha }}
      
      - name: Run Smoke Tests
        run: |
          npm install -g newman
          newman run tests/smoke-tests.postman_collection.json

  deploy-staging:
    needs: build-images
    runs-on: ubuntu-latest
    environment:
      name: staging
      approval_required: true
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Staging
        run: |
          ./infrastructure/scripts/deploy.sh staging ${{ github.sha }}
      
      - name: Run Full Test Suite
        run: |
          npm install -g cypress
          cypress run

  deploy-prod:
    needs: [deploy-dev, deploy-staging]
    runs-on: ubuntu-latest
    environment:
      name: production
      approval_required: true
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production (Blue-Green)
        run: |
          ./infrastructure/scripts/deploy.sh prod ${{ github.sha }}
      
      - name: Health Checks
        run: |
          ./infrastructure/scripts/health-check.sh prod
      
      - name: Verify Deployment
        run: |
          ./infrastructure/scripts/verify.sh prod
```

---

## 4. Kubernetes Deployment

### 4.1 Kustomize Structure

```
kubernetes/
├── base/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   └── kustomization.yaml
│
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── patches/
    │       ├── replicas.yaml
    │       ├── resources.yaml
    │       └── env.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   └── patches/
    └── prod/
        ├── kustomization.yaml
        └── patches/
            ├── replicas.yaml
            ├── resources.yaml
            ├── autoscaling.yaml
            └── pod-disruption-budget.yaml
```

### 4.2 Example Deployment Manifest

```yaml
# kubernetes/base/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
        version: v1
    spec:
      containers:
      - name: backend
        image: ghcr.io/ai-interview/backend:latest
        ports:
        - name: http
          containerPort: 8000
        - name: metrics
          containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: connection-string
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - backend
              topologyKey: kubernetes.io/hostname
```

---

## 5. Monitoring & Observability

### 5.1 Azure Monitoring Stack

```yaml
# Metrics Collection
Azure Monitor Metrics:
  ├─ Application Gateway
  │  ├─ Request count
  │  ├─ Response latency
  │  ├─ Backend health
  │  └─ WAF block rate
  ├─ AKS
  │  ├─ CPU usage
  │  ├─ Memory usage
  │  ├─ Pod restarts
  │  └─ Network I/O
  ├─ Database
  │  ├─ CPU percentage
  │  ├─ Memory usage
  │  ├─ Query latency
  │  └─ Connection count
  └─ Redis
     ├─ Connected clients
     ├─ Memory usage
     ├─ Operations/sec
     └─ Evictions

# Logs Collection
Log Analytics:
  ├─ AKS Container Logs
  │  ├─ Application logs
  │  ├─ System logs
  │  └─ Pod events
  ├─ Application Logs
  │  ├─ Request logs
  │  ├─ Error logs
  │  └─ Audit logs
  └─ Database Logs
     ├─ Query logs
     └─ Error logs

# Tracing
Application Insights:
  ├─ Distributed tracing
  ├─ Dependency tracking
  ├─ Exception analysis
  └─ Performance counters

# Alerts
Alert Rules:
  ├─ Error rate > 1%
  ├─ API latency p99 > 2s
  ├─ Pod restart count > 3
  ├─ Database CPU > 80%
  ├─ Redis memory > 80%
  └─ Cost overrun > 10%
```

### 5.2 Alert Routing

```
Alert Severity:
  CRITICAL → PagerDuty (Immediate escalation)
  HIGH → Slack (#incidents channel)
  MEDIUM → Email (Summary)
  LOW → Dashboard (View only)
```

---

## 6. Backup & Disaster Recovery

### 6.1 Backup Strategy

```
Database:
  ├─ Automated backups: Daily
  ├─ Retention: 35 days
  ├─ Geo-redundant: Yes
  ├─ Recovery Time Objective (RTO): 5 minutes
  └─ Recovery Point Objective (RPO): 5 minutes

Application State:
  ├─ Configuration: Git (version controlled)
  ├─ Secrets: Azure Key Vault (encrypted, audited)
  └─ Artifacts: Container Registry

Data:
  ├─ Blob Storage: Geo-redundant (RA-GRS)
  ├─ Retention: 90 days for archived data
  └─ Encryption: Azure Storage Encryption
```

### 6.2 Disaster Recovery Procedures

```
Scenario: Database failure
  ├─ Automatic failover to replica (< 1 minute)
  ├─ Application retry logic
  └─ Alert to on-call engineer

Scenario: AKS cluster failure
  ├─ Auto-healing of failed nodes
  ├─ Pod rescheduling to healthy nodes
  ├─ Manual intervention if > 2 nodes down
  └─ Cluster recreation from IaC within 30 minutes

Scenario: Regional outage
  ├─ Manual failover to secondary region
  ├─ Update DNS records
  ├─ Restore from geo-redundant backups
  └─ Full recovery within 4 hours (target)
```

---

## 7. Security Compliance

### 7.1 Security Layers

```
Perimeter:
  ├─ DDoS Protection (Azure DDoS Protection Standard)
  ├─ WAF Rules (OWASP Top 10)
  ├─ IP Allowlisting (Optional)
  └─ Rate Limiting

Network:
  ├─ Private Virtual Network
  ├─ Network Security Groups
  ├─ Private Link for databases/cache
  └─ No direct internet access to databases

Application:
  ├─ TLS 1.2+ for all communications
  ├─ JWT token-based authentication
  ├─ RBAC authorization
  ├─ Input validation
  └─ SQL injection prevention (parameterized queries)

Data:
  ├─ Encryption at rest (Azure encryption)
  ├─ Encryption in transit (TLS)
  ├─ PII masking in logs
  ├─ GDPR compliance (right to delete)
  └─ SOC 2 compliance
```

### 7.2 Compliance Checklist

```
☐ SSL/TLS certificates (Let's Encrypt or Azure)
☐ Secrets in Azure Key Vault (not in code/config)
☐ RBAC configured for all services
☐ Network security groups configured
☐ WAF rules enabled on App Gateway
☐ Logging enabled for audit trail
☐ Backup testing completed
☐ Disaster recovery plan documented
☐ Security patches applied monthly
☐ Penetration testing completed annually
```

This deployment architecture provides:
- ✅ High availability and fault tolerance
- ✅ Automatic scaling and load balancing
- ✅ Comprehensive observability
- ✅ Secure multi-layer defense
- ✅ Disaster recovery capability
- ✅ Compliance and auditability
