# CDOS Performance / Load Test Specification

| Document ID | CDOS-PT-001 |
|-------------|-------------|
| Version | 1.0 |
| Date | 2026-05-29 |
| Status | Draft |
| Author | Agent-Tests |

Tests: TR-001, TR-002, TR-003, TR-004, TR-005, TR-006, TR-007, TR-008, TR-009, TR-010, TR-011

---

## 1. Performance Targets (from TR-001 through TR-011)

| NFR ID | Metric | Target |
|--------|--------|--------|
| TR-001 | API Response Time (p50) | < 200ms |
| TR-002 | API Response Time (p99) | < 500ms (CRUD), < 2000ms (aggregation) |
| TR-003 | Transform Throughput | >= 500 records/sec/node |
| TR-004 | Event Bus Publish Latency (p95) | < 100ms |
| TR-005 | End-to-End Ingestion Latency | Batch < 5 min, Real-time < 30 sec |
| TR-006 | Database Query Performance | SQL < 3s (10K subjects), vector search p95 < 500ms |
| TR-007 | Concurrent User Capacity | >= 2,000 concurrent authenticated users |
| TR-008 | Study Data Volume | 500 studies x 10K subjects x 500K CRF pages |
| TR-009 | Horizontal Scaling | 3 → 50 nodes in < 5 min |
| TR-010 | Storage Growth | Auto-expand to 100 TB, zero downtime |
| TR-011 | Kafka Throughput | 1,000 topics, 50K msg/sec, consumer lag < 10s |

---

## 2. Load Test Scenarios

### Scenario 1: API CRUD Steady-State Load

| Parameter | Value |
|-----------|-------|
| Target TPS | 500 requests/sec |
| Duration | 30 minutes |
| Ramp-up | 5 minutes (0 → 500 TPS) |
| User model | 2,000 concurrent authenticated users |
| Endpoints | GET/POST /studies, /subjects, /crf-pages, /queries |
| Success Criteria | p50 < 200ms, p95 < 400ms, p99 < 500ms, error rate < 0.1% |

### Scenario 2: Aggregation Query Spike

| Parameter | Value |
|-----------|-------|
| Target TPS | 100 requests/sec |
| Duration | 15 minutes |
| Endpoints | GET /studies/{id}/dashboard, /studies/{id}/enrollment-forecast |
| Success Criteria | p99 < 2000ms, error rate < 0.5% |

### Scenario 3: Data Ingestion Burst (EDC Sync)

| Parameter | Value |
|-----------|-------|
| Target TPS | 1,000 records/sec (batch ingestion) |
| Duration | 10 minutes |
| Payload | CRF pages (avg 5KB each) |
| Success Criteria | All records ingested within 5 min, transform throughput >= 500 rec/sec/node |

### Scenario 4: Event Bus High-Volume

| Parameter | Value |
|-----------|-------|
| Target | 50,000 messages/sec |
| Duration | 10 minutes |
| Topics | 100 concurrent topics |
| Success Criteria | Publish p95 < 100ms, consumer lag < 10s |

### Scenario 5: Scale-Out Test

| Parameter | Value |
|-----------|-------|
| Starting Nodes | 3 |
| Target Nodes | 50 |
| Trigger | CPU > 70% sustained for 2 min |
| Success Criteria | Scale-out completes in < 5 min, zero request failures during scaling |

### Scenario 6: Database Volume Test

| Parameter | Value |
|-----------|-------|
| Data Volume | 500 studies, 5M subjects, 500M CRF pages |
| Query Types | Point lookups, range scans, aggregation |
| Success Criteria | SQL < 3s, vector search p95 < 500ms |

---

## 3. Test Tooling

| Tool | Purpose |
|------|---------|
| Locust | HTTP load generation (Scenarios 1-3) |
| k6 | Event-driven load generation (Scenario 4) |
| kubectl | Scale-out measurement (Scenario 5) |
| pgbench | Database benchmarking (Scenario 6) |
| Prometheus + Grafana | Metrics collection and visualization |

---

## 4. Environment

| Resource | Specification |
|----------|--------------|
| K8s Cluster | 3-50 nodes (auto-scaling), 8 vCPU / 32 GB RAM per node |
| Database | PostgreSQL 16, 3-node HA cluster, 1 TB SSD |
| Kafka | 5-broker cluster, 100 partitions per topic |
| Load Generators | 4 x c5.4xlarge instances |

---

## 5. Reporting

After each test run, produce:
- Latency distribution chart (p50, p95, p99)
- Throughput over time graph
- Error rate timeline
- Resource utilization (CPU, memory, disk I/O, network)
- Comparison against target thresholds (pass/fail)
