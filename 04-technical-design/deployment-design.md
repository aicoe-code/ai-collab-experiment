# CDOS — Deployment Design

## 1. Overview

This document defines the deployment architecture for CDOS, covering Kubernetes infrastructure, CI/CD pipeline (GitHub Actions), and environment promotion (dev → staging → prod). This design satisfies:
- **04-F**: K8s, CI/CD, environments, Helm charts, pipeline stages

---

## 2. Environment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT ARCHITECTURE                                  │
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────┐ │
│  │ DEVELOPMENT  │────▶│ STAGING      │────▶│ PRODUCTION                   │ │
│  │              │     │              │     │                              │ │
│  │ • Local K8s  │     │ • AWS EKS    │     │ • AWS EKS (Multi-AZ)        │ │
│  │ • Single node│     │ • 3 nodes    │     │ • 6 nodes (2 per AZ)        │ │
│  │ • Mock ext.  │     │ • Test ext.  │     │ • Real external systems     │ │
│  │ • Auto-deploy│     │ • Manual gate│     │ • Manual gate + approval    │ │
│  └──────────────┘     └──────────────┘     └──────────────────────────────┘ │
│                                                                              │
│  Data: Synthetic      Data: Anonymized     Data: Real clinical data         │
│  Secrets: Local       Secrets: AWS Secrets  Secrets: HashiCorp Vault         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Environment Specifications

| Attribute | Development | Staging | Production |
|-----------|-------------|---------|------------|
| Cluster | kind / minikube | AWS EKS | AWS EKS |
| Nodes | 1 (8 CPU, 16GB) | 3 (16 CPU, 32GB each) | 6 (16 CPU, 32GB each) |
| Availability Zones | 1 | 2 | 3 |
| PostgreSQL | Single instance | Primary + 1 replica | Primary + 2 replicas |
| Kafka | 1 broker | 3 brokers | 3 brokers |
| Redis | Single instance | Sentinel (3 nodes) | Sentinel (3 nodes) |
| Secrets | env vars / .env | AWS Secrets Manager | HashiCorp Vault |
| External Systems | Mock servers | Test instances | Production instances |
| Data | Synthetic | Anonymized production | Real |
| TLS | Self-signed | Let's Encrypt | Let's Encrypt |
| Monitoring | Local Prometheus | CloudWatch + Grafana | CloudWatch + Grafana + PagerDuty |
| Deploy Trigger | Push to `develop` | Push to `staging` | Manual approval after staging |
| SLA | None | 99% | 99.9% |

---

## 3. Kubernetes Architecture

### 3.1 Cluster Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER (Production)                           │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Namespace: cdos-system                                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │ │
│  │  │ api-gateway  │  │ study-svc    │  │ subject-svc                  │ │ │
│  │  │ (Deployment) │  │ (Deployment) │  │ (Deployment)                 │ │ │
│  │  │ Replicas: 3  │  │ Replicas: 2  │  │ Replicas: 2                  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────────┘ │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │ │
│  │  │ ae-svc       │  │ transform-   │  │ edc-adapter                  │ │ │
│  │  │ (Deployment) │  │ engine       │  │ (Deployment)                 │ │ │
│  │  │ Replicas: 2  │  │ (Deployment) │  │ Replicas: 1                  │ │ │
│  │  └──────────────┘  │ Replicas: 3  │  └──────────────────────────────┘ │ │
│  │                    └──────────────┘                                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Namespace: cdos-data                                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │ │
│  │  │ PostgreSQL   │  │ Kafka        │  │ Redis                        │ │ │
│  │  │ (StatefulSet)│  │ (StatefulSet)│  │ (StatefulSet)                │ │ │
│  │  │ 3 replicas   │  │ 3 brokers    │  │ Sentinel: 3 nodes            │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Namespace: cdos-security                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │ │
│  │  │ Keycloak     │  │ Vault        │  │ cert-manager                 │ │ │
│  │  │ (Deployment) │  │ (StatefulSet)│  │ (Deployment)                 │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Namespace: cdos-monitoring                                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │ │
│  │  │ Prometheus   │  │ Grafana      │  │ Loki (logs)                  │ │ │
│  │  │ (Deployment) │  │ (Deployment) │  │ (StatefulSet)                │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Helm Chart Structure

```
cdos-helm/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-staging.yaml
├── values-prod.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── api-gateway/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   └── ingress.yaml
│   ├── services/
│   │   ├── study-service.yaml
│   │   ├── subject-service.yaml
│   │   ├── adverse-event-service.yaml
│   │   └── ...
│   ├── adapters/
│   │   ├── edc-adapter.yaml
│   │   ├── ctms-adapter.yaml
│   │   └── ...
│   ├── transform-engine/
│   │   └── deployment.yaml
│   ├── data/
│   │   ├── postgresql-statefulset.yaml
│   │   ├── kafka-statefulset.yaml
│   │   └── redis-statefulset.yaml
│   ├── security/
│   │   ├── network-policies.yaml
│   │   └── pod-security-policies.yaml
│   └── monitoring/
│       ├── service-monitors.yaml
│       └── prometheus-rules.yaml
└── charts/
    └── (sub-charts for dependencies)
```

### 3.3 Deployment Specification

```yaml
# api-gateway deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: cdos-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: api-gateway
          image: cdos/api-gateway:{{ .Values.image.tag }}
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: cdos-db-credentials
                  key: url
            - name: KAFKA_BROKERS
              value: "kafka-0.kafka:9092,kafka-1.kafka:9092,kafka-2.kafka:9092"
            - name: KEYCLOAK_URL
              value: "https://auth.cdos.io"
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

### 3.4 Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: cdos-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 4. CI/CD Pipeline (GitHub Actions)

### 4.1 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE (GitHub Actions)                           │
│                                                                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────┐  │
│  │  Lint   │──▶│  Test   │──▶│  Build  │──▶│  Scan   │──▶│  Deploy     │  │
│  │  & Type │   │  Unit + │   │  Docker │   │  SAST + │   │  Dev/Staging│  │
│  │  Check  │   │  Integ  │   │  Image  │   │  SCA    │   │  /Prod      │  │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────────┘  │
│                                                                              │
│  Trigger: Push to main / develop / staging / release/*                       │
│  Duration: ~15 minutes (full pipeline)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Pipeline Stages

#### Stage 1: Lint & Type Check (2 min)

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - run: pip install ruff mypy
    - run: ruff check .
    - run: mypy . --strict
    - run: yamllint .
```

#### Stage 2: Test (5 min)

```yaml
test:
  needs: lint
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16
      env:
        POSTGRES_DB: cdos_test
        POSTGRES_USER: test
        POSTGRES_PASSWORD: test
      ports:
        - 5432:5432
    kafka:
      image: confluentinc/cp-kafka:7.6.0
      ports:
        - 9092:9092
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - run: pip install -r requirements.txt
    - run: pytest tests/unit/ -v --cov=services --cov-report=xml
    - run: pytest tests/integration/ -v
    - uses: codecov/codecov-action@v4
      with:
        files: coverage.xml
        fail_ci_if_error: true
        target: 80%
```

#### Stage 3: Build Docker Image (3 min)

```yaml
build:
  needs: test
  runs-on: ubuntu-latest
  strategy:
    matrix:
      service:
        - api-gateway
        - study-service
        - subject-service
        - adverse-event-service
        - transform-engine
        - edc-adapter
        - ctms-adapter
        - lims-adapter
        - safety-adapter
        - iwrss-adapter
  steps:
    - uses: actions/checkout@v4
    - uses: docker/setup-buildx-action@v3
    - uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    - uses: docker/build-push-action@v5
      with:
        context: ./08-software/services/${{ matrix.service }}
        push: true
        tags: |
          ghcr.io/cdos/${{ matrix.service }}:${{ github.sha }}
          ghcr.io/cdos/${{ matrix.service }}:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

#### Stage 4: Security Scan (2 min)

```yaml
security-scan:
  needs: build
  runs-on: ubuntu-latest
  steps:
    - uses: aquasecurity/trivy-action@master
      with:
        image-ref: ghcr.io/cdos/api-gateway:${{ github.sha }}
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH'
    - uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: 'trivy-results.sarif'
```

#### Stage 5: Deploy (3 min)

```yaml
deploy-dev:
  needs: security-scan
  if: github.ref == 'refs/heads/develop'
  runs-on: ubuntu-latest
  environment: development
  steps:
    - uses: actions/checkout@v4
    - uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_DEV }}
        aws-region: us-east-1
    - run: |
        helm upgrade --install cdos ./08-software/infrastructure/k8s/cdos-helm \
          --namespace cdos-system \
          --values ./08-software/infrastructure/k8s/cdos-helm/values-dev.yaml \
          --set image.tag=${{ github.sha }} \
          --wait --timeout 5m

deploy-staging:
  needs: security-scan
  if: github.ref == 'refs/heads/staging'
  runs-on: ubuntu-latest
  environment: staging
  steps:
    - uses: actions/checkout@v4
    - uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_STAGING }}
        aws-region: us-east-1
    - run: |
        helm upgrade --install cdos ./08-software/infrastructure/k8s/cdos-helm \
          --namespace cdos-system \
          --values ./08-software/infrastructure/k8s/cdos-helm/values-staging.yaml \
          --set image.tag=${{ github.sha }} \
          --wait --timeout 10m
    - run: |
        # Run smoke tests
        pytest tests/smoke/ --base-url=https://staging-api.cdos.io

deploy-prod:
  needs: deploy-staging
  if: startsWith(github.ref, 'refs/heads/release/')
  runs-on: ubuntu-latest
  environment:
    name: production
    url: https://api.cdos.io
  steps:
    - uses: actions/checkout@v4
    - uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_PROD }}
        aws-region: us-east-1
    - run: |
        helm upgrade --install cdos ./08-software/infrastructure/k8s/cdos-helm \
          --namespace cdos-system \
          --values ./08-software/infrastructure/k8s/cdos-helm/values-prod.yaml \
          --set image.tag=${{ github.sha }} \
          --wait --timeout 15m
    - run: |
        # Run smoke tests
        pytest tests/smoke/ --base-url=https://api.cdos.io
```

### 4.3 Branch Strategy

```
main ──────────────────────────────────────────────────────────────▶
  │
  ├── develop ─────────────────────────────────────────────────────▶
  │     │
  │     ├── feature/xyz ──────▶ PR → develop
  │     │
  │     └── staging ──────────────────────────────────────────────▶
  │           │
  │           └── release/1.x ────────────────────────────────────▶
  │                 │
  │                 └── main (merge + tag)
```

| Branch | Environment | Auto-Deploy | Approval Required |
|--------|-------------|-------------|-------------------|
| develop | Development | Yes | No |
| staging | Staging | Yes | No |
| release/* | Production | After staging success | Yes (2 approvers) |
| hotfix/* | Production | After staging success | Yes (1 approver) |

---

## 5. Database Migration Strategy

### 5.1 Migration Tool

- **Tool**: Alembic (SQLAlchemy migration tool)
- **Pattern**: Version-controlled, forward-only migrations in production
- **Rollback**: Supported in dev/staging; manual in production

### 5.2 Migration Pipeline

```
Code PR includes migration → CI validates SQL → Deploy applies migration → Service starts
```

### 5.3 Migration Safety Rules

| Rule | Description |
|------|-------------|
| No destructive migrations in prod | DROP COLUMN requires 2-phase: mark deprecated → remove in next release |
| Backward compatible | New columns must be nullable or have defaults |
| Tested in staging | All migrations run in staging before production |
| Rollback plan | Every migration has a documented rollback procedure |

---

## 6. Monitoring & Observability

### 6.1 Monitoring Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus + Grafana | System and application metrics |
| Logs | Loki + Grafana | Centralized log aggregation |
| Traces | OpenTelemetry + Jaeger | Distributed tracing |
| Alerts | Alertmanager + PagerDuty | Incident notification |
| Uptime | Synthetic monitoring | Endpoint availability |

### 6.2 Key Metrics

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| API latency (p99) | Prometheus | >500ms |
| API error rate | Prometheus | >1% |
| Kafka consumer lag | Prometheus | >1000 messages |
| PostgreSQL connections | Prometheus | >80% of max |
| Pod restart count | Kubernetes | >3 in 5 minutes |
| Disk usage | Prometheus | >85% |
| Certificate expiry | cert-manager | <30 days |

### 6.3 Health Endpoints

```python
# Each service exposes:
GET /health    # Liveness probe (is the service running?)
GET /ready     # Readiness probe (is the service ready to accept traffic?)
GET /metrics   # Prometheus metrics (OpenMetrics format)
```

---

## 7. Disaster Recovery

### 7.1 Backup Strategy

| Component | Backup Method | Frequency | Retention | RPO |
|-----------|--------------|-----------|-----------|-----|
| PostgreSQL | pg_dump + WAL archiving | Hourly WAL, Daily full | 30 days | 1 hour |
| Kafka | Topic replication (factor=3) | Continuous | 90 days topic retention | 0 |
| S3 (submissions) | Cross-region replication | Continuous | Indefinite | 0 |
| Vault | Raft snapshot | Hourly | 30 days | 1 hour |

### 7.2 Recovery Procedures

| Scenario | RTO | Procedure |
|----------|-----|-----------|
| Single pod failure | <1 min | Kubernetes auto-restart |
| Database failure | <15 min | Failover to replica |
| Full cluster failure | <1 hour | Restore from backup to new cluster |
| Data corruption | <4 hours | Point-in-time recovery from WAL |

---

## 8. Infrastructure as Code

### 8.1 Terraform Structure

```
infrastructure/terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── eks/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── msk/          # Managed Kafka
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── s3/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    ├── dev.tfvars
    ├── staging.tfvars
    └── prod.tfvars
```

### 8.2 Terraform Apply Pipeline

```yaml
terraform:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: hashicorp/setup-terraform@v3
    - run: terraform init
    - run: terraform plan -var-file=environments/${{ env.ENV }}.tfvars
    - run: terraform apply -auto-approve -var-file=environments/${{ env.ENV }}.tfvars
      if: github.ref == 'refs/heads/main'
```
