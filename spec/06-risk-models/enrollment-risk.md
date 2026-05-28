# Risk Model: Enrollment

## Overview

| Attribute | Value |
|-----------|-------|
| Risk ID | RISK-ENR-001 |
| Category | Enrollment |
| Severity | HIGH |
| Owner | Clinical Operations |
| Review Cycle | Weekly |

Enrollment risk is the probability that a study fails to recruit sufficient
subjects within the planned timeline and budget. It is the most common cause
of clinical trial delays.

---

## Trigger Conditions

Triggers are evaluated on a rolling 4-week window against [Entity:Study]
and [Entity:Subject] data sourced from [System:CTMS].

| ID | Condition | Threshold | Severity |
|----|-----------|-----------|----------|
| ENR-T01 | Site enrollment rate | < 2 subjects/site/month | WARNING |
| ENR-T02 | Overall enrollment pace vs. plan | < 80% of cumulative target at any milestone | CRITICAL |
| ENR-T03 | Screen failure rate | > 40% of screened subjects | WARNING |
| ENR-T04 | Sites activated but zero enrollment for | > 8 consecutive weeks | CRITICAL |
| ENR-T05 | Dropout rate mid-study | > 20% of enrolled subjects | WARNING |
| ENR-T06 | Country-level enrollment shortfall | < 50% of country target at 50% timeline | CRITICAL |
| ENR-T07 | Pediatric or rare disease cohort | < 1 subject/site/month (adjusted threshold) | WARNING |

---

## Detection Method

### Data Sources

- [System:CTMS] — subject enrollment dates, site activation dates, screening logs
- [System:EDC] — subject status changes (SCREENING → ENROLLED → WITHDRAWN)
- [System:IWRS] — randomization confirmations (validates true enrollment)

### Detection Algorithm

```
FOR EACH study IN active_studies:
    enrollment_rate = COUNT(subjects WHERE enrollment_date >= TODAY - 28 days)
                     / COUNT(active_sites)
                     / 1 month

    IF enrollment_rate < 2.0:
        TRIGGER ENR-T01

    cumulative_pct = COUNT(enrolled_subjects) / study.target_enrollment * 100
    planned_pct    = (TODAY - study.start_date) / planned_duration * 100

    IF cumulative_pct < 0.80 * planned_pct:
        TRIGGER ENR-T02

    screen_fail_rate = COUNT(screen_failed) / COUNT(screened) * 100
    IF screen_fail_rate > 40:
        TRIGGER ENR-T03
```

### Monitoring Frequency

| Trigger | Frequency | System |
|---------|-----------|--------|
| ENR-T01 | Weekly | [System:CTMS] |
| ENR-T02 | Weekly | [System:CTMS] |
| ENR-T03 | Bi-weekly | [System:EDC] |
| ENR-T04 | Weekly | [System:CTMS] |
| ENR-T05 | Monthly | [System:EDC] |
| ENR-T06 | Monthly | [System:CTMS] |

---

## Mitigation Strategy

### ENR-T01: Low Site Enrollment Rate

1. Investigate root cause via site monitoring visit from [System:CTMS]
2. Provide additional CRA support or principal investigator training
3. Expand referral networks at the site
4. If persisting > 12 weeks, consider site replacement

### ENR-T02: Overall Enrollment Pace Below Plan

1. Activate reserve sites (pre-identified in site feasibility)
2. Expand to additional countries with faster regulatory timelines
3. Increase advertising and community outreach budgets by 25%
4. Amend protocol inclusion/exclusion criteria if clinically justified

### ENR-T03: High Screen Failure Rate

1. Review screening logs in [System:EDC] to identify top failure reasons
2. Tighten pre-screening questionnaires at sites
3. If criterion-related, evaluate protocol amendment with [Entity:Protocol]
4. Add more sites to compensate for lower yield per site

### ENR-T04: Activated Sites With Zero Enrollment

1. Trigger CRA site visit within 2 weeks
2. Escalate to site management committee
3. If no improvement in 4 additional weeks, initiate site close-out

### ENR-T05: High Dropout Rate

1. Analyze withdrawal reasons from [Entity:Subject].status = WITHDRAWN
2. Implement retention strategies (visit reminders, travel reimbursement)
3. Reduce visit burden if protocol allows (e.g., telemedicine visits)

---

## Impact on Data Models

| Affected Entity | Impact | Action |
|-----------------|--------|--------|
| [Entity:Study] | target_enrollment may need revision | Update via protocol amendment |
| [Entity:Subject] | Status transitions: ENROLLED → WITHDRAWN | Monitor status field |
| [Entity:Site] | Status changes: ACTIVE → CLOSED | Update site status |
| [Entity:Visit] | Missed visits increase with enrollment stress | Track MISSED visit status |
| [Entity:Protocol] | Inclusion/exclusion criteria may change | Version increment required |

### Affected Transforms

- [Transform:EDC→SDTM] — DM domain records increase with new enrollments
- Subject disposition derivation (DM.ACTARM) must reflect status changes

### CDISC Impact

| Variable | Domain | Risk Impact |
|----------|--------|-------------|
| USUBJID | DM | Count affected by enrollment pace |
| ACTARM | DM | Disposition code changes on dropout |
| RFSTDTC / RFENDTC | DM | Date range shifts with delays |
| SITEID | DM | Site count changes with additions/removals |

---

## Escalation Matrix

| Severity | Escalation To | SLA |
|----------|--------------|-----|
| WARNING | Study Manager | Review within 5 business days |
| CRITICAL | Clinical Operations Director | Review within 2 business days |
| CRITICAL (persistent > 4 weeks) | Executive Steering Committee | Review within 1 week |

---

## Cross-References

- Referenced by: [Risk:Site] (ENR-T04 triggers site risk evaluation)
- Data source: [System:CTMS], [System:EDC], [System:IWRS]
- Entities: [Entity:Study], [Entity:Subject], [Entity:Site], [Entity:Protocol]
