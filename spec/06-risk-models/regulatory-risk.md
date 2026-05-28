# Risk Model: Regulatory

## Overview

| Attribute | Value |
|-----------|-------|
| Risk ID | RISK-REG-001 |
| Category | Regulatory Compliance |
| Severity | CRITICAL |
| Owner | Regulatory Affairs |
| Review Cycle | Monthly |

Regulatory risk measures the probability that a study fails to meet the
requirements of health authorities (FDA, EMA, PMDA, etc.) resulting in
clinical holds, warning letters, refusal-to-file decisions, or data
integrity findings that invalidate trial results.

---

## Trigger Conditions

Triggers are evaluated against [Entity:Protocol], [Entity:AdverseEvent],
[Entity:Submission], and [Entity:Subject] data sourced from
[System:Safety], [System:RegSubmit], [System:eTMF], and [System:EDC].

| ID | Condition | Threshold | Severity |
|----|-----------|-----------|----------|
| REG-T01 | SUSAR reporting timeliness | > 15% of SUSARs not reported to authorities within 7 calendar days (fatal/life-threatening) or 15 calendar days (other) | CRITICAL |
| REG-T02 | IND Safety Report (21 CFR 312.32) | Any IND safety report not submitted within 15 calendar days of sponsor awareness | CRITICAL |
| REG-T03 | eCTD submission rejection | > 0 technical rejection (formatting, validation errors) per submission | CRITICAL |
| REG-T04 | Clinical hold issued | Any clinical hold notification from FDA or equivalent authority | CRITICAL |
| REG-T05 | 483 observations | ≥ 1 observation related to data integrity in FDA inspection | CRITICAL |
| REG-T06 | IRB/IEC protocol deviation reporting | > 5% of protocol deviations not reported to IRB/IEC within 30 days | WARNING |
| REG-T07 | Informed consent version mismatch | > 0 subjects consented with outdated [Entity:Protocol] consent form version | CRITICAL |
| REG-T08 | Annual report deadline | Annual safety report not submitted > 5 business days before regulatory deadline | WARNING |
| REG-T09 | Data integrity audit flag | > 2% of audit trail entries show unauthorized modification | CRITICAL |
| REG-T10 | CTMS-to-eTMF document gap | > 10% of required regulatory documents missing from [System:eTMF] | WARNING |

---

## Detection Method

### Data Sources

- [System:Safety] — SUSAR reports, ICSR submissions, expedited safety reports
- [System:RegSubmit] — eCTD submissions, validation results, submission status
- [System:eTMF] — regulatory document completeness, inspection readiness
- [System:EDC] — audit trail entries, consent form versions, protocol deviations
- [System:CTMS] — regulatory milestone tracking, deviation reporting logs

### Detection Algorithm

```
FOR EACH study IN active_studies:
    # SUSAR reporting timeliness
    total_susars = COUNT(adverse_events WHERE susar_flag = true
                         AND last_12_months)
    late_susars = COUNT(adverse_events WHERE susar_flag = true
                        AND report_date - awareness_date > reporting_deadline)
    late_pct = late_susars / total_susars * 100

    IF late_pct > 15:
        TRIGGER REG-T01

    # eCTD submission validation
    failed_submissions = COUNT(submissions WHERE validation_status = 'FAILED'
                               AND last_90_days)

    IF failed_submissions > 0:
        TRIGGER REG-T03

    # Informed consent version check
    current_version = protocol.consent_form_version
    outdated_consents = COUNT(subjects WHERE consent_version != current_version
                              AND consent_date > current_version.effective_date)

    IF outdated_consents > 0:
        TRIGGER REG-T07

    # Audit trail integrity
    total_audit_entries = COUNT(audit_trail WHERE last_30_days)
    unauthorized = COUNT(audit_trail WHERE user_role NOT IN ('authorized')
                         AND action = 'MODIFY'
                         AND last_30_days)
    integrity_pct = unauthorized / total_audit_entries * 100

    IF integrity_pct > 2:
        TRIGGER REG-T09

    # eTMF completeness
    required_docs = COUNT(required_documents WHERE study_id = study.study_id)
    present_docs = COUNT(etmf_documents WHERE study_id = study.study_id
                         AND status = 'FILED')
    gap_pct = (required_docs - present_docs) / required_docs * 100

    IF gap_pct > 10:
        TRIGGER REG-T10
```

### Monitoring Frequency

| Trigger | Frequency | System |
|---------|-----------|--------|
| REG-T01 | Per-event (event-driven) | [System:Safety] |
| REG-T02 | Per-event (event-driven) | [System:Safety] |
| REG-T03 | Per-submission (event-driven) | [System:RegSubmit] |
| REG-T04 | Per-event (event-driven) | [System:RegSubmit] |
| REG-T05 | Per-inspection (event-driven) | [System:eTMF], [System:EDC] |
| REG-T06 | Monthly | [System:CTMS] |
| REG-T07 | Per-enrollment (event-driven) | [System:EDC] |
| REG-T08 | Quarterly | [System:RegSubmit] |
| REG-T09 | Weekly | [System:EDC] |
| REG-T10 | Monthly | [System:eTMF] |

---

## Mitigation Strategy

### REG-T01: Late SUSAR Reporting

1. Implement automated SUSAR detection in [System:Safety] pipeline
2. Configure escalation alerts at day 5 and day 10 post-awareness
3. Pre-populate ICSR forms using [Entity:AdverseEvent] data from [System:EDC]
4. Maintain 24/7 safety physician on-call for expedited assessment
5. Conduct monthly SUSAR reporting compliance review

### REG-T02: Late IND Safety Reports

1. Implement automated 15-day clock starting at sponsor awareness date
2. Configure [System:Safety] to generate draft reports within 48 hours
3. Implement regulatory affairs review workflow with 72-hour SLA
4. Track all open reports on regulatory dashboard in [System:RegSubmit]

### REG-T03: eCTD Technical Rejection

1. Run pre-submission validation in [System:RegSubmit] with full eCTD validator
2. Implement two-person review of submission package before dispatch
3. Maintain submission checklist per health authority requirements
4. Conduct root cause analysis for each rejection and update procedures

### REG-T04: Clinical Hold

1. Immediately halt all dosing and enrollment activities
2. Notify all sites via [System:CTMS] emergency notification
3. Engage regulatory counsel within 24 hours
4. Prepare clinical hold response within 30 calendar days (FDA requirement)
5. Implement corrective measures and submit to authority
6. Track lift status in [System:RegSubmit]

### REG-T05: FDA 483 Data Integrity Observations

1. Engage data integrity experts for immediate assessment
2. Conduct comprehensive audit trail review in [System:EDC]
3. Implement CAPA within 15 business days
4. Prepare written response to FDA within 15 business days
5. Document all corrective actions in [System:eTMF]

### REG-T07: Informed Consent Version Mismatch

1. Immediately identify all affected subjects
2. Obtain re-consent with current version at next visit
3. Document protocol deviation and report to IRB/IEC
4. Block further data collection until re-consent obtained
5. Update consent version tracking in [System:EDC]

### REG-T09: Audit Trail Integrity Issues

1. Immediately restrict access to affected [System:EDC] modules
2. Conduct forensic analysis of audit trail entries
3. Determine if unauthorized modifications affected clinical data
4. If data affected, assess impact on primary endpoint analysis
5. Report findings to Quality Assurance and Regulatory Affairs

---

## Impact on Data Models

| Affected Entity | Impact | Action |
|-----------------|--------|--------|
| [Entity:AdverseEvent] | SUSAR flag, reporting dates must be accurate | Validate seriousness and expectedness |
| [Entity:Protocol] | Consent form version tracking required | Add consent_version attribute |
| [Entity:Subject] | Consent status may need update | Track consent_version per subject |
| [Entity:Submission] | eCTD lifecycle management | Track validation_status |
| [Entity:Study] | Clinical hold status must be reflected | Add hold_status attribute |
| [Entity:CRFPage] | Audit trail integrity is critical | Ensure 21 CFR Part 11 compliance |

### Affected Transforms

- [Transform:EDC→SDTM] — AE domain SUSAR coding affects safety signal detection
- SDTM CO (Comments) domain may need supplemental information for regulatory queries
- Consent data flows through to DM domain (consent date tracking)
- [Transform:Safety→ICSR] — ICSR generation depends on accurate AE severity/seriousness

### CDISC Impact

| Variable | Domain | Risk Impact |
|----------|--------|-------------|
| AESER, AESCAN | AE | Seriousness criteria drive SUSAR classification |
| AESTDTC | AE | Onset date drives reporting clock |
| DMRFSTDTC | DM | Reference start date affected by clinical hold |
| DSTERM, DSDECOD | DS | Hold and withdrawal dispositions |
| SUPPQUAL | Various | Supplemental regulatory information |

---

## Escalation Matrix

| Severity | Escalation To | SLA |
|----------|--------------|-----|
| WARNING | Regulatory Affairs Manager | Review within 5 business days |
| CRITICAL | VP Regulatory Affairs | Review within 24 hours |
| CRITICAL (clinical hold) | Chief Medical Officer + CEO | Immediate notification |
| CRITICAL (483 observation) | VP Quality + VP Regulatory | Within 24 hours |
| CRITICAL (SUSAR late) | Chief Medical Officer + Safety Officer | Within 24 hours |

---

## Cross-References

- Related: [Risk:DataQuality] (REG-T05, REG-T09 driven by data quality)
- Related: [Risk:Site] (REG-T06 deviations reported per site)
- Related: [Risk:SupplyChain] (REG-T04 clinical hold halts drug supply)
- Data source: [System:Safety], [System:RegSubmit], [System:eTMF],
  [System:EDC], [System:CTMS]
- Entities: [Entity:AdverseEvent], [Entity:Protocol], [Entity:Subject],
  [Entity:Submission], [Entity:Study], [Entity:CRFPage]
