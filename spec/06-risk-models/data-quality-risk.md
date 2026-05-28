# Risk Model: Data Quality

## Overview

| Attribute | Value |
|-----------|-------|
| Risk ID | RISK-DQ-001 |
| Category | Data Quality |
| Severity | HIGH |
| Owner | Data Management |
| Review Cycle | Weekly |

Data quality risk measures the probability that clinical data collected
during a study contains errors, inconsistencies, or omissions that
compromise the statistical integrity of the trial or delay submission.

---

## Trigger Conditions

Triggers are evaluated against [Entity:CRFPage], [Entity:Query],
[Entity:LabResult], and [Entity:AdverseEvent] data sourced from
[System:EDC].

| ID | Condition | Threshold | Severity |
|----|-----------|-----------|----------|
| DQ-T01 | Open query rate per CRF page | > 3 queries/page across study | WARNING |
| DQ-T02 | Query aging — open queries past SLA | > 15% of queries open > 21 calendar days | CRITICAL |
| DQ-T03 | Missing required CRF pages | > 5% of expected CRF pages not entered | WARNING |
| DQ-T04 | Lab data out-of-range rate | > 10% of lab results flagged abnormal without resolution | WARNING |
| DQ-T05 | Protocol deviation rate | > 8% of visits have ≥1 deviation | CRITICAL |
| DQ-T06 | Duplicate data entry detected | > 0 duplicate subject records per site | CRITICAL |
| DQ-T07 | Visit date inconsistencies | > 3% of visits have actual_date outside window_start..window_end | WARNING |
| DQ-T08 | eSignature missing on critical CRFs | > 2% of CRF pages requiring e-signature unsigned | CRITICAL |

---

## Detection Method

### Data Sources

- [System:EDC] — CRF pages, queries, edit checks, e-signatures
- [System:LIMS] — laboratory results, reference ranges
- [System:CTMS] — protocol deviations, monitoring visit findings

### Detection Algorithm

```
FOR EACH study IN active_studies:
    # Query density
    total_queries = COUNT(queries WHERE status = 'OPEN')
    total_crf_pages = COUNT(crf_pages WHERE status = 'COMPLETED')
    query_rate = total_queries / total_crf_pages

    IF query_rate > 3.0:
        TRIGGER DQ-T01

    # Query aging
    aged_queries = COUNT(queries WHERE status = 'OPEN'
                         AND created_at < TODAY - 21 days)
    aged_pct = aged_queries / total_queries * 100

    IF aged_pct > 15:
        TRIGGER DQ-T02

    # Missing CRFs
    expected_pages = COUNT(visits) * COUNT(expected_crf_per_visit)
    completed_pages = COUNT(crf_pages WHERE status = 'COMPLETED')
    missing_pct = (expected_pages - completed_pages) / expected_pages * 100

    IF missing_pct > 5:
        TRIGGER DQ-T03

    # Lab out-of-range
    abnormal_unresolved = COUNT(lab_results
                          WHERE abnormal_flag IN ('LOW','HIGH','ABNORMAL')
                          AND query_status != 'RESOLVED')
    abnormal_pct = abnormal_unresolved / COUNT(lab_results) * 100

    IF abnormal_pct > 10:
        TRIGGER DQ-T04
```

### Monitoring Frequency

| Trigger | Frequency | System |
|---------|-----------|--------|
| DQ-T01 | Weekly | [System:EDC] |
| DQ-T02 | Daily | [System:EDC] |
| DQ-T03 | Weekly | [System:EDC] |
| DQ-T04 | Bi-weekly | [System:LIMS], [System:EDC] |
| DQ-T05 | Monthly | [System:CTMS] |
| DQ-T06 | On-change (event-driven) | [System:EDC] |
| DQ-T07 | Weekly | [System:EDC] |
| DQ-T08 | Weekly | [System:EDC] |

---

## Mitigation Strategy

### DQ-T01: High Query Rate

1. Review edit check specifications for over-triggering rules
2. Tighten data entry guidelines and retrain site staff
3. Implement real-time edit checks in [System:EDC] to catch errors at entry
4. Add auto-query resolution for non-critical discrepancies

### DQ-T02: Query Aging Beyond SLA

1. Escalate open queries to site coordinators with 48-hour deadline
2. Assign dedicated CRA to clear aged query backlog
3. Implement weekly query aging dashboard in [System:CTMS]
4. For queries > 42 days, escalate to Study Manager

### DQ-T03: Missing CRF Pages

1. Generate missing data report from [System:EDC] per site
2. Issue data entry reminders to sites via [System:CTMS]
3. During monitoring visits, verify source documents against CRFs
4. If systemic, evaluate site for data management support intervention

### DQ-T05: Protocol Deviation Rate

1. Analyze deviation types (eligibility, dosing, visit windows)
2. Implement additional edit checks in [System:EDC] for common deviations
3. Update site training materials based on deviation patterns
4. If eligibility-related, review [Entity:Protocol] inclusion/exclusion criteria

### DQ-T06: Duplicate Records

1. Immediately quarantine duplicate records in [System:EDC]
2. Investigate root cause (data entry error vs. system defect)
3. Merge records preserving audit trail per 21 CFR Part 11
4. Implement duplicate detection rules as pre-entry edit check

---

## Impact on Data Models

| Affected Entity | Impact | Action |
|-----------------|--------|--------|
| [Entity:CRFPage] | May require correction or clarification | Update via query resolution |
| [Entity:Query] | Query count and aging metrics drive risk level | Monitor status transitions |
| [Entity:LabResult] | abnormal_flag values may need resolution | Re-query or confirm results |
| [Entity:AdverseEvent] | Missing or delayed AE reports degrade safety data | Ensure timely capture |
| [Entity:Visit] | Date inconsistencies require correction | Update actual_date |
| [Entity:Subject] | Duplicate or invalid records need merge/retire | Subject status update |

### Affected Transforms

- [Transform:EDC→SDTM] — All SDTM domain derivations are affected by data quality
- Edit check failures propagate to query generation rules
- Lab data transforms require valid reference ranges for abnormal_flag derivation

### CDISC Impact

| Variable | Domain | Risk Impact |
|----------|--------|-------------|
| LBSTRESN, LBNRIND | LB | Lab out-of-range results affect analysis datasets |
| AESTDTC, AEENDTC | AE | Missing dates prevent duration derivation |
| SVSTDTC | SV | Visit date errors affect timing variables |
| DMRFSTDTC | DM | Reference date errors cascade to all relative timing |

---

## Escalation Matrix

| Severity | Escalation To | SLA |
|----------|--------------|-----|
| WARNING | Data Manager | Review within 5 business days |
| CRITICAL | Head of Data Management | Review within 2 business days |
| CRITICAL (persistent > 4 weeks) | Study Director | Review within 1 week |

---

## Cross-References

- Related: [Risk:Regulatory] (data quality issues may trigger regulatory risk)
- Data source: [System:EDC], [System:LIMS], [System:CTMS]
- Entities: [Entity:CRFPage], [Entity:Query], [Entity:LabResult],
  [Entity:AdverseEvent], [Entity:Visit], [Entity:Subject]
