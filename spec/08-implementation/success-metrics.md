# CDOS Success Metrics

## Overview

This document defines quantified success metrics for the Clinical Development Operating System (CDOS). Each metric includes a baseline (current state), target (CDOS-enabled state), unit of measurement, and measurement method. These metrics are used to evaluate CDOS ROI (see cost-model.md) and validate Phase exit criteria (see roadmap.md).

---

## Metric 1: Data Reconciliation Time

**Description:** Time required to reconcile data across EDC, CTMS, Safety, and LIMS systems for a single study at database lock.

| Attribute | Value |
|-----------|-------|
| **Baseline** | 2-4 weeks (10-20 business days) |
| **Target** | 2-4 hours |
| **Reduction** | 95-99% |
| **Unit** | Hours per study at database lock |

**Measurement Method:**
1. Track wall-clock time from initiation of reconciliation process to confirmed data consistency across all source systems
2. Measure via CDOS audit trail timestamps: `reconciliation_start` → `reconciliation_complete` events
3. Compare against historical reconciliation logs from manual processes (pre-CDOS baseline)
4. Report as median and P95 across all studies in measurement period

**Data Sources:**
- CDOS audit trail (canonical entity reconciliation events)
- EDC system export timestamps
- Manual reconciliation logs (historical baseline)

**Target Validation:** Metric is met when 90% of studies complete reconciliation within 4 hours.

---

## Metric 2: Query Resolution Cycle Time

**Description:** Average time from data clarification query generation to resolution.

| Attribute | Value |
|-----------|-------|
| **Baseline** | 14 days (median) |
| **Target** | 3 days (median) |
| **Reduction** | 79% |
| **Unit** | Days per query |

**Measurement Method:**
1. Track query lifecycle: `query.raised` → `query.resolved` timestamps in CDOS event bus
2. Calculate median cycle time across all queries per study per month
3. Segment by query type (manual, auto-generated, edit check) and severity
4. Compare against historical EDC query aging reports (pre-CDOS baseline)

**Data Sources:**
- CDOS event bus (query.raised, query.responded, query.resolved events)
- Canonical entity: [Entity:Query]
- Historical EDC query management reports

**Target Validation:** Metric is met when median query cycle time ≤ 3 days across all active studies.

---

## Metric 3: SDTM/ADaM Dataset Generation Time

**Description:** Time required to generate submission-ready SDTM and ADaM datasets from raw EDC data.

| Attribute | Value |
|-----------|-------|
| **Baseline** | 6-8 weeks per study (programming + QC) |
| **Target** | 1 week per study |
| **Reduction** | 83-87% |
| **Unit** | Weeks per study |

**Measurement Method:**
1. Track transformation pipeline execution: raw data ingestion → SDTM validation (Pinnacle 21) → ADaM generation → Define-XML output
2. Measure wall-clock time from data freeze to validated dataset delivery
3. Include QC time (programmer review, P21 conformance check)
4. Compare against historical SDTM/ADaM programming timelines

**Data Sources:**
- CDOS transformation pipeline logs (Airflow DAG execution records)
- Pinnacle 21 validation reports (conformance pass/fail timestamps)
- Historical biostatistics programming timesheets

**Target Validation:** Metric is met when 90% of studies produce validated SDTM/ADaM datasets within 5 business days of data freeze.

---

## Metric 4: SAE Processing Time

**Description:** Time from SAE report receipt to entry in the safety database (Argus Safety).

| Attribute | Value |
|-----------|-------|
| **Baseline** | 5-7 days |
| **Target** | < 24 hours |
| **Reduction** | 80-86% |
| **Unit** | Hours per SAE |

**Measurement Method:**
1. Track SAE lifecycle: `ae.reported` (EDC) → `safety_report.submitted` (Argus Safety) timestamps
2. Measure end-to-end latency including medical review, coding, and seriousness assessment
3. Segment by SAE type (expected/unexpected, SUSAR/non-SUSAR)
4. Compare against historical SAE processing logs from manual workflow

**Data Sources:**
- CDOS event bus (ae.reported, ae.coded, safety_report.submitted events)
- Safety system (Argus Safety) submission timestamps
- Historical SAE processing tracking sheets

**Target Validation:** Metric is met when 95% of SAEs are processed within 24 hours of initial report.

---

## Metric 5: Time to Database Lock

**Description:** Total time from last patient last visit (LPLV) to confirmed database lock.

| Attribute | Value |
|-----------|-------|
| **Baseline** | 8-12 weeks |
| **Target** | 2-4 weeks |
| **Reduction** | 50-75% |
| **Unit** | Weeks from LPLV to database lock |

**Measurement Method:**
1. Track from LPLV date to database lock confirmation event
2. Component breakdown: data cleaning (query resolution), medical coding, reconciliation, final QC
3. Measure via CDOS canonical entity status transitions (Subject, CRFPage, Query)
4. Compare against historical database lock timelines across therapeutic areas

**Data Sources:**
- CDOS canonical entity audit trail (study.status transitions)
- EDC system database lock timestamps
- Historical study milestone tracking (CTMS)

**Target Validation:** Metric is met when median time to database lock ≤ 4 weeks across all completed studies.

---

## Metric 6: Regulatory Submission Assembly Time

**Description:** Time required to assemble a complete eCTD submission package from CDOS-managed artifacts.

| Attribute | Value |
|-----------|-------|
| **Baseline** | 4-6 weeks per submission |
| **Target** | 1 week per submission |
| **Reduction** | 80-83% |
| **Unit** | Weeks per submission |

**Measurement Method:**
1. Track from submission planning initiation to eCTD package validation (gateway acceptance)
2. Include: document compilation, Define-XML generation, dataset formatting, eCTD structure validation
3. Measure via CDOS submission artifact assembly pipeline timestamps
4. Compare against historical regulatory affairs submission timelines

**Data Sources:**
- CDOS transformation pipeline (submission assembly DAG)
- Regulatory submission system (eCTD validator results)
- Historical regulatory affairs project timelines

**Target Validation:** Metric is met when 90% of submissions are assembled within 5 business days.

---

## Metric 7: Data Quality Score

**Description:** Percentage of data fields passing all validation rules (edit checks, CDISC conformance, business rules) on first submission.

| Attribute | Value |
|-----------|-------|
| **Baseline** | 70-80% first-pass acceptance rate |
| **Target** | 95% first-pass acceptance rate |
| **Improvement** | 19-36% improvement |
| **Unit** | Percentage of fields passing validation |

**Measurement Method:**
1. Calculate: (fields passing all validation / total fields submitted) × 100
2. Measure at each transformation gate: CDASH → SDTM → ADaM
3. Track Pinnacle 21 conformance check results (error count, warning count)
4. Compare against historical edit check failure rates from EDC systems

**Data Sources:**
- CDOS data quality engine validation logs
- Pinnacle 21 validation reports (error/warning counts)
- Historical EDC edit check failure reports

**Target Validation:** Metric is met when 95% of data fields pass all validation on first submission across all active studies.

---

## Metric 8: System Integration Latency (P99)

**Description:** End-to-end latency for data propagation between integrated clinical systems.

| Attribute | Value |
|-----------|-------|
| **Baseline** | 24-72 hours (batch ETL cycles) |
| **Target** | < 5 seconds (event-driven) |
| **Reduction** | 99.99% |
| **Unit** | Seconds (P99 latency) |

**Measurement Method:**
1. Track event production → consumption timestamps across Kafka topics
2. Measure P99 latency for each adapter pair (EDC→CDOS, CDOS→Safety, CDOS→CTMS)
3. Use OpenTelemetry distributed tracing for end-to-end latency measurement
4. Report separately for API calls (< 500ms target) and event delivery (< 5s target)

**Data Sources:**
- Kafka consumer lag metrics
- OpenTelemetry trace spans
- Grafana latency dashboards

**Target Validation:** Metric is met when P99 latency < 500ms for API calls and < 5s for event delivery, sustained over 30-day measurement window.

---

## Metric 9: Platform Availability

**Description:** CDOS platform uptime excluding planned maintenance windows.

| Attribute | Value |
|-----------|-------|
| **Baseline** | N/A (new platform) |
| **Target** | 99.9% uptime |
| **Tolerance** | < 8.76 hours unplanned downtime per year |
| **Unit** | Percentage uptime |

**Measurement Method:**
1. Monitor via OpenTelemetry health checks and Grafana uptime dashboards
2. Calculate: (total minutes - unplanned downtime minutes) / total minutes × 100
3. Exclude planned maintenance windows (communicated 72 hours in advance)
4. Track per-component availability (API, event bus, transformation pipeline)

**Data Sources:**
- Kubernetes health check logs
- Grafana uptime monitoring
- Incident management system (PagerDuty/Opsgenie)

**Target Validation:** Metric is met when platform availability ≥ 99.9% measured over rolling 30-day window.

---

## Metric 10: Concurrent Study Capacity

**Description:** Number of concurrent clinical studies the platform can support without performance degradation.

| Attribute | Value |
|-----------|-------|
| **Baseline** | 1-2 studies (manual processes) |
| **Target** | 10+ concurrent studies |
| **Improvement** | 5-10x capacity increase |
| **Unit** | Number of concurrent studies |

**Measurement Method:**
1. Load test with simulated multi-study workload (10 studies × 500 subjects × 20 visits)
2. Monitor P99 latency, database query time, and Kafka consumer lag under load
3. Verify no performance degradation (latency increase < 10% from single-study baseline)
4. Validate data isolation: no cross-study data leakage via row-level security audit

**Data Sources:**
- Load testing results (k6/Grafana k6)
- PostgreSQL query performance (pg_stat_statements)
- Kafka partition metrics
- Row-level security audit logs

**Target Validation:** Metric is met when platform supports 10 concurrent studies with P99 latency < 200ms (API) and < 2s (events).

---

## Metrics Summary Table

| # | Metric | Baseline | Target | Reduction | Unit |
|---|--------|----------|--------|-----------|------|
| 1 | Data Reconciliation Time | 2-4 weeks | 2-4 hours | 95-99% | hours/study |
| 2 | Query Resolution Cycle Time | 14 days | 3 days | 79% | days/query |
| 3 | SDTM/ADaM Generation Time | 6-8 weeks | 1 week | 83-87% | weeks/study |
| 4 | SAE Processing Time | 5-7 days | < 24 hours | 80-86% | hours/SAE |
| 5 | Time to Database Lock | 8-12 weeks | 2-4 weeks | 50-75% | weeks |
| 6 | Submission Assembly Time | 4-6 weeks | 1 week | 80-83% | weeks/submission |
| 7 | Data Quality Score | 70-80% | 95% | 19-36% improvement | % first-pass |
| 8 | Integration Latency (P99) | 24-72 hours | < 5 seconds | 99.99% | seconds |
| 9 | Platform Availability | N/A | 99.9% | N/A | % uptime |
| 10 | Concurrent Study Capacity | 1-2 studies | 10+ studies | 5-10x | studies |

---

## Measurement Cadence

| Metric | Frequency | Report To |
|--------|-----------|-----------|
| Data Reconciliation Time | Per study lock | Data Management Lead |
| Query Resolution Cycle Time | Weekly | Clinical Operations |
| SDTM/ADaM Generation Time | Per study | Biostatistics Lead |
| SAE Processing Time | Per SAE event | Medical Monitor, Safety Lead |
| Time to Database Lock | Per study | Study Manager |
| Submission Assembly Time | Per submission | Regulatory Affairs Lead |
| Data Quality Score | Daily (rolling 7-day) | Data Management Lead |
| Integration Latency | Continuous (Grafana) | Platform Engineering |
| Platform Availability | Continuous (Grafana) | IT Operations |
| Concurrent Study Capacity | Quarterly | Program Management |

---

## Cross-References

- Cost model ROI calculations: [Cost Model](cost-model.md)
- Implementation roadmap phases: [Implementation Roadmap](roadmap.md)
- Data quality risk model: [Module 06: Risk Models](../06-risk-models/data-quality-risk.md)
- Compliance requirements: [Module 07: Compliance](../07-compliance/21-cfr-part11.md)
- Integration SLAs: [Module 04: Integrations](../04-integrations/api-contracts.md)
- Architecture observability: [Module 01: Architecture](../01-architecture/technology-stack.md)
