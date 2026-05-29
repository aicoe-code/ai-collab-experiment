# CDOS Infrastructure Requirements

**Document Version:** 1.0
**Author:** Agent-TR
**Last Updated:** 2026-05-29

This document specifies the infrastructure components required to host the CDOS platform,
including compute, storage, networking, and environment definitions. All quantities are
baseline unless noted; horizontal scaling is governed by TR-009 and TR-010 in
`non-functional-requirements.md`.

---

## 1. Compute Requirements

### 1.1 Application Tier (Kubernetes)

| Resource | Specification | Notes |
|----------|--------------|-------|
| Cluster Type | Managed Kubernetes (EKS / AKS / GKE) | Multi-AZ deployment required |
| Minimum Nodes | 3 worker nodes (baseline) | Auto-scales to 50 per TR-009 |
| Node Instance Type | 8 vCPU, 32 GB RAM per node | General-purpose compute optimized |
| Total Baseline Compute | 24 vCPU, 96 GB RAM | Across 3 nodes |
| Max Compute | 400 vCPU, 1,600 GB RAM | Across 50 nodes |
| Pod Resource Requests | CPU: 500m-2000m, RAM: 1Gi-8Gi | Per microservice |
| Pod Resource Limits | CPU: 4000m, RAM: 16Gi | Per microservice |
| Auto-scaling | HPA (CPU > 70%, memory > 80%), Cluster Autoscaler | See TR-009 |

### 1.2 Data Processing Tier

| Resource | Specification | Notes |
|----------|--------------|-------|
| Transform Workers | 2-10 dedicated nodes for SDTM transforms | Scales per TR-003 throughput target |
| Worker Instance Type | 16 vCPU, 64 GB RAM, NVMe SSD | Compute + memory optimized |
| Batch Processing | Apache Spark or Kubernetes Jobs | For large-volume SDTM mappings |
| GPU Nodes (optional) | 1-2 nodes, NVIDIA T4 or equivalent | For vector embedding generation (AI features) |

---

## 2. Storage Requirements

### 2.1 SQL Database (PostgreSQL)

| Resource | Specification | Notes |
|----------|--------------|-------|
| Engine | PostgreSQL 16+ (managed: RDS / Cloud SQL / Azure DB) | GxP-validated version |
| Deployment | Multi-AZ with automatic failover | Per TR-012 (99.9% uptime) |
| Primary Instance | 16 vCPU, 128 GB RAM, 10 TB SSD (gp3/io2) | Baseline for 50 studies |
| Read Replicas | 2-4 read replicas | Dashboard and reporting queries |
| Max Storage | 50 TB (auto-expand per TR-010) | IOPS: 16,000 baseline, 64,000 burst |
| Backup | Continuous WAL archiving + daily snapshots | 30-day retention, 15-year archive |
| Connection Pool | PgBouncer, max 500 connections | Per microservice pool of 50 |

### 2.2 Vector Database

| Resource | Specification | Notes |
|----------|--------------|-------|
| Engine | PostgreSQL pgvector extension OR dedicated (Qdrant / Milvus / Weaviate) | For AI-assisted features |
| Index Type | HNSW (Hierarchical Navigable Small World) | For semantic similarity search |
| Storage | 500 GB - 2 TB | Projection: ~100M vectors at 1536 dimensions |
| Query Performance | p95 < 500ms for top-10 nearest neighbor | Per TR-006 |
| Embedding Model | OpenAI text-embedding-3-large or equivalent | 1536-dimension vectors |

### 2.3 Object Storage

| Resource | Specification | Notes |
|----------|--------------|-------|
| Service | S3 / Blob Storage / GCS | Managed object store |
| Buckets | cdos-documents, cdos-backups, cdos-exports, cdos-imaging | Separated by function |
| Total Capacity | 10-50 TB | For eTMF documents, imaging, exports |
| Lifecycle Policy | Hot (0-90 days) -> Warm (90-365 days) -> Cold (>365 days) | Cost optimization |
| Versioning | Enabled on all buckets | Regulatory compliance |
| Encryption | SSE-S3 (AES-256) or SSE-KMS | Per TR-016 |

### 2.4 Cache Layer

| Resource | Specification | Notes |
|----------|--------------|-------|
| Engine | Redis 7+ (managed: ElastiCache / Azure Cache / Memorystore) | Cluster mode |
| Nodes | 3-node cluster (1 primary, 2 replicas) | Multi-AZ |
| Memory | 32 GB total | Session cache, API response cache |
| Eviction Policy | allkeys-lru | For non-critical cache data |
| Use Cases | Session tokens, rate limiting counters, API response cache, real-time dashboards | |

---

## 3. Network Requirements

### 3.1 Virtual Network Architecture

| Component | Specification | Notes |
|-----------|--------------|-------|
| VPC/VNet | Single VPC with CIDR /16 (65,536 IPs) | Dedicated to CDOS |
| Public Subnets | 2 subnets (one per AZ) | WAF, load balancer only |
| Private Subnets (App) | 2 subnets (one per AZ) | Kubernetes worker nodes |
| Private Subnets (Data) | 2 subnets (one per AZ) | Databases, Redis, Kafka |
| NAT Gateway | 1 per AZ (2 total) | Outbound internet for app tier |

### 3.2 Load Balancing

| Component | Specification | Notes |
|-----------|--------------|-------|
| External LB | Application Load Balancer (ALB) | HTTPS termination, WAF integration |
| Internal LB | Network Load Balancer (NLB) | Service-to-service communication |
| SSL Certificate | Wildcard *.cdos.io, auto-renewed | ACM / Key Vault managed |

### 3.3 DNS and Service Discovery

| Component | Specification | Notes |
|-----------|--------------|-------|
| External DNS | Route 53 / Azure DNS / Cloud DNS | Health-checked failover |
| Internal DNS | Kubernetes CoreDNS | Service discovery within cluster |
| Service Mesh | Istio or Linkerd (optional) | mTLS between services, traffic management |

### 3.4 Message Bus (Kafka)

| Component | Specification | Notes |
|-----------|--------------|-------|
| Engine | Apache Kafka 3.6+ (managed: MSK / Event Hubs / Confluent Cloud) | Per TR-011 |
| Brokers | 3 brokers minimum (one per AZ) | Replication factor = 3 |
| Partitions | Up to 10,000 partitions across 1,000 topics | Per TR-011 |
| Throughput | 50,000 messages/second peak | Per TR-011 |
| Retention | 7 days (default), 30 days for audit topics | |
| Schema Registry | Confluent Schema Registry or equivalent | Avro/JSON schema evolution |

---

## 4. Environment Definitions

### 4.1 Environment Matrix

| Environment | Purpose | Isolation | Data | SLA |
|-------------|---------|-----------|------|-----|
| **Development (dev)** | Developer workloads, feature branches | Shared cluster, namespace per dev | Synthetic data only | Best effort |
| **Integration (int)** | Continuous integration testing | Shared cluster, dedicated namespace | Synthetic data | 95% uptime |
| **Staging (staging)** | Pre-production validation, UAT | Dedicated cluster (scaled down) | Anonymized production-like data | 99% uptime |
| **Production (prod)** | Live clinical trial operations | Dedicated cluster (full scale) | Real clinical data | 99.9% uptime (TR-012) |
| **DR (dr)** | Disaster recovery standby | Dedicated cluster in secondary region | Replicated production data | RTO 4 hrs (TR-013) |
| **Validation (val)** | GxP / 21 CFR Part 11 validation | Dedicated cluster, locked config | Validation test data | Available during validation cycles |

### 4.2 Environment-Specific Configuration

| Parameter | Dev | Integration | Staging | Production |
|-----------|-----|-------------|---------|------------|
| K8s Nodes | 2 (4vCPU/16GB) | 3 (8vCPU/32GB) | 3 (8vCPU/32GB) | 3-50 (8vCPU/32GB) |
| PostgreSQL | db.t3.large | db.r6g.xlarge | db.r6g.2xlarge | db.r6g.4xlarge |
| Redis | cache.t3.medium | cache.r6g.large | cache.r6g.xlarge | cache.r6g.xlarge |
| Kafka | 1 broker | 3 brokers | 3 brokers | 3+ brokers |
| Vector DB | Shared instance | Dedicated (small) | Dedicated (medium) | Dedicated (large) |
| Encryption | Self-signed certs | Internal CA | Internal CA | Public CA + HSM |
| Backup | None | Daily (7-day retention) | Daily (30-day retention) | Continuous + daily (15-year archive) |

### 4.3 Environment Promotion Pipeline

```
dev  -->  int  -->  staging  -->  val (if GxP change)  -->  prod
                     |                                        |
                     +-- DR replication ---------------------+
```

- **dev -> int**: Automated on PR merge to main
- **int -> staging**: Automated after integration tests pass
- **staging -> val**: Manual gate (QA approval required)
- **val -> prod**: Manual gate (QA + Compliance approval)
- **staging -> prod**: For non-GxP changes, automated after staging tests pass

---

## 5. Monitoring and Observability

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus + Grafana | Application and infrastructure metrics |
| Logging | EFK (Elasticsearch, Fluentd, Kibana) or Loki | Centralized structured logging |
| Tracing | Jaeger or OpenTelemetry Collector | Distributed request tracing |
| Alerting | PagerDuty / OpsGenie | On-call alerting |
| Uptime | Synthetic monitoring (Pingdom / Checkly) | External availability checks |
| Security | SIEM integration (Splunk / Sentinel) | Security event correlation |

---

## 6. Infrastructure as Code

| Layer | Tool | Location |
|-------|------|----------|
| Cloud Resources | Terraform | `08-software/infrastructure/terraform/` |
| Kubernetes Manifests | Helm Charts | `08-software/infrastructure/k8s/` |
| CI/CD Pipeline | GitHub Actions / GitLab CI | `.github/workflows/` or `.gitlab-ci.yml` |
| Policy as Code | OPA/Gatekeeper | Kubernetes admission policies |
| Secrets | HashiCorp Vault or AWS Secrets Manager | Centralized secret management |
