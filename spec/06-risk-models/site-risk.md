# Risk Model: Site

## Overview

| Attribute | Value |
|-----------|-------|
| Risk ID | RISK-SITE-001 |
| Category | Site Performance |
| Severity | HIGH |
| Owner | Clinical Operations |
| Review Cycle | Monthly |

Site risk measures the probability that an individual investigation site
fails to meet performance, compliance, or quality standards required for
a clinical trial. It encompasses investigator conduct, staff turnover,
regulatory compliance, and data quality at the site level.

---

## Trigger Conditions

Triggers are evaluated against [Entity:Site], [Entity:Subject],
[Entity:Investigator], and [Entity:Visit] data sourced from
[System:CTMS] and [System:EDC].

| ID | Condition | Threshold | Severity |
|----|-----------|-----------|----------|
| SITE-T01 | Site enrollment rate | < 1 subject/site/month for 3 consecutive months | WARNING |
| SITE-T02 | Query rate per site | > 2x the study-wide average query rate | WARNING |
| SITE-T03 | Protocol deviation rate per site | > 12% of visits with deviations vs. study average < 8% | CRITICAL |
| SITE-T04 | Monitoring visit findings severity | ≥ 3 major findings unresolved > 30 days | CRITICAL |
| SITE-T05 | CRA turnover at site | > 2 CRA changes in 12 months | WARNING |
| SITE-T06 | Site audit findings | ≥ 1 critical finding in GCP audit | CRITICAL |
| SITE-T07 | Subject retention rate per site | < 70% of enrolled subjects completing study | WARNING |
| SITE-T08 | Data entry timeliness | > 15% of CRF pages entered > 7 days after visit | WARNING |
| SITE-T09 | IRB/IEC approval lapse | Ethics approval expired or under review | CRITICAL |
| SITE-T10 | Investigator GCP training expiry | GCP certificate expired > 30 days | CRITICAL |

---

## Detection Method

### Data Sources

- [System:CTMS] — site profiles, monitoring visit reports, audit findings, training records
- [System:EDC] — CRF entry timestamps, query rates per site, protocol deviations
- [System:eTMF] — regulatory document status (IRB/IEC approvals, GCP certificates)

### Detection Algorithm

```
FOR EACH site IN active_sites:
    # Low enrollment
    rate = COUNT(subjects WHERE site_id = site.site_id
                 AND enrollment_date >= TODAY - 90 days) / 3

    IF rate < 1.0:
        TRIGGER SITE-T01

    # High query rate
    site_query_rate = COUNT(queries WHERE site_id = site.site_id)
                      / COUNT(crf_pages WHERE site_id = site.site_id)
    study_avg_query_rate = COUNT(queries) / COUNT(crf_pages)

    IF site_query_rate > 2.0 * study_avg_query_rate:
        TRIGGER SITE-T02

    # Protocol deviations
    site_dev_rate = COUNT(deviations WHERE site_id = site.site_id)
                    / COUNT(visits WHERE site_id = site.site_id) * 100

    IF site_dev_rate > 12:
        TRIGGER SITE-T03

    # Unresolved major findings
    major_open = COUNT(findings WHERE site_id = site.site_id
                       AND severity = 'MAJOR'
                       AND status != 'CLOSED'
                       AND created_at < TODAY - 30 days)

    IF major_open >= 3:
        TRIGGER SITE-T04

    # IRB/IEC approval status
    approval = etmf.get_approval(site_id = site.site_id, type = 'IRB')
    IF approval.expiry_date < TODAY OR approval.status = 'UNDER_REVIEW':
        TRIGGER SITE-T09
```

### Monitoring Frequency

| Trigger | Frequency | System |
|---------|-----------|--------|
| SITE-T01 | Monthly | [System:CTMS] |
| SITE-T02 | Bi-weekly | [System:EDC] |
| SITE-T03 | Monthly | [System:CTMS] |
| SITE-T04 | Per-monitoring visit | [System:CTMS] |
| SITE-T05 | Quarterly | [System:CTMS] |
| SITE-T06 | Per-audit (event-driven) | [System:CTMS], [System:eTMF] |
| SITE-T07 | Monthly | [System:CTMS] |
| SITE-T08 | Weekly | [System:EDC] |
| SITE-T09 | Monthly | [System:eTMF] |
| SITE-T10 | Monthly | [System:eTMF] |

---

## Mitigation Strategy

### SITE-T01: Low Site Enrollment

1. Conduct root cause analysis with site principal investigator
2. Provide additional training on recruitment strategies
3. Increase advertising support for the site
4. If no improvement in 6 months, initiate site close-out per [Risk:Enrollment] ENR-T04

### SITE-T02: High Query Rate

1. Review common query types at the site
2. Provide targeted training on data entry procedures
3. Assign experienced data entry support for 2-week intensive period
4. Implement pre-submission data quality checks at site

### SITE-T03: High Protocol Deviation Rate

1. Classify deviations (eligibility, dosing, visit window, prohibited medication)
2. Conduct protocol re-training with all site staff
3. Implement additional monitoring visits (monthly → bi-weekly)
4. If eligibility deviations, review [Entity:Protocol] criteria interpretation

### SITE-T04: Unresolved Monitoring Findings

1. Escalate to site management committee
2. Issue formal Corrective Action Plan (CAPA) to site
3. Increase monitoring frequency to monthly visits
4. If no resolution in 60 days, recommend site suspension

### SITE-T06: Critical Audit Finding

1. Immediately suspend site enrollment pending investigation
2. Conduct root cause analysis with Quality Assurance
3. Implement CAPA with defined timelines
4. Report to IRB/IEC and sponsor regulatory affairs
5. Resume site only after CAPA verification

### SITE-T09: IRB/IEC Approval Lapse

1. Immediately halt all study activities at site
2. Notify [System:CTMS] and update site status to SUSPENDED
3. Work with site to expedite re-approval
4. Do not resume until approval confirmation received via [System:eTMF]

### SITE-T10: Expired GCP Training

1. Notify principal investigator and site coordinator
2. Block data entry in [System:EDC] until training renewed
3. Allow 30-day grace period for renewal
4. If not renewed, escalate to site management

---

## Impact on Data Models

| Affected Entity | Impact | Action |
|-----------------|--------|--------|
| [Entity:Site] | Status changes: ACTIVE → SUSPENDED → CLOSED | Update status field |
| [Entity:Subject] | Subjects at suspended sites need transfer or close-out | Update site_id or status |
| [Entity:Visit] | Visits at suspended sites marked MISSED or CANCELLED | Update visit status |
| [Entity:Investigator] | Training status affects data entry authorization | Track GCP certificate |
| [Entity:AdverseEvent] | AE reporting may be delayed at underperforming sites | Monitor AE capture timeliness |
| [Entity:CRFPage] | Data entry delays tracked at site level | Monitor created_at vs. visit date |

### Affected Transforms

- [Transform:EDC→SDTM] — DM domain SITEID affected by site status changes
- Site status changes trigger disposition code updates in SDTM DS (Disposition)
- Protocol deviations mapped to SDTM DV domain

### CDISC Impact

| Variable | Domain | Risk Impact |
|----------|--------|-------------|
| SITEID | DM | Site identifier present across all domains |
| INVID | DM | Investigator changes require DM update |
| DSTERM, DSDECOD | DS | Site close-out dispositions captured |
| DVTERM | DV | Protocol deviations per site |

---

## Escalation Matrix

| Severity | Escalation To | SLA |
|----------|--------------|-----|
| WARNING | Clinical Research Associate | Review within 10 business days |
| CRITICAL | Study Manager | Review within 3 business days |
| CRITICAL (audit finding) | Quality Assurance Director | Immediate notification |
| CRITICAL (IRB lapse) | Regulatory Affairs Director | Immediate notification |

---

## Cross-References

- Related: [Risk:Enrollment] (SITE-T01 aligns with ENR-T04)
- Related: [Risk:DataQuality] (SITE-T02, SITE-T03 affect data quality metrics)
- Related: [Risk:Regulatory] (SITE-T06, SITE-T09 have regulatory implications)
- Data source: [System:CTMS], [System:EDC], [System:eTMF]
- Entities: [Entity:Site], [Entity:Subject], [Entity:Investigator],
  [Entity:Visit], [Entity:AdverseEvent], [Entity:CRFPage], [Entity:Protocol]
