# CDOS Functional Requirements

## Document Metadata

| Field | Value |
|-------|-------|
| Document ID | CDOS-FR-001 |
| Version | 1.1 |
| Author | Agent-FR |
| Date | 2026-05-29 |
| Status | Draft — Aligned |

---

## Categories

| Category | Description |
|----------|-------------|
| Study Management | Study lifecycle, protocol, and site configuration |
| Subject Management | Screening, enrollment, and subject tracking |
| Data Capture & Integration | EDC, CTMS, LIMS, Safety, IWRS integrations |
| Data Quality & Compliance | Validation, audit trails, regulatory compliance |
| Reporting & Analytics | Dashboards, metrics, data exports |
| Workflow & Orchestration | Cross-system event routing and process automation |

---

## Functional Requirements

### Study Management

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-001 | Study Creation | The system SHALL allow authorized users to create a new Study with metadata including protocol ID, title, phase, therapeutic area, and sponsor. | Implements BR-016 | High | Study Management |
| FR-002 | Study Versioning | The system SHALL maintain version-controlled copies of the Protocol. Each amendment SHALL produce a new version while preserving the prior version for audit. | Implements BR-016 | High | Study Management |
| FR-003 | Site Configuration | The system SHALL allow configuration of Sites for a Study, including Site number, address, principal Investigator, and activation status. | Implements BR-016 | High | Study Management |
| FR-004 | Study Milestone Tracking | The system SHALL track key Study milestones (first subject enrolled, last subject last visit, database lock) and report milestone status against planned dates. | Implements BR-012 | Medium | Study Management |
| FR-005 | Visit Schedule Definition | The system SHALL define the Visit schedule for a Study, including Visit name, window (early/late days), and required procedures per Visit. | Implements BR-018 | High | Study Management |

### Subject Management

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-006 | Subject Screening | The system SHALL record Subject screening data and assign a screening number upon initiation of the informed consent process. | Implements BR-016 | High | Subject Management |
| FR-007 | Subject Enrollment | The system SHALL transition a Subject from SCREENED to ENROLLED status upon confirmation of eligibility criteria and randomization via IWRS. | Implements BR-003 | High | Subject Management |
| FR-008 | Subject Withdrawal | The system SHALL allow recording of Subject withdrawal with reason, date, and investigator attribution, and SHALL cascade status to all linked Visit and Dose records. | Implements BR-001 | High | Subject Management |
| FR-009 | Eligibility Assessment | The system SHALL evaluate inclusion/exclusion criteria against Subject data and produce a pass/fail eligibility determination. | Implements BR-009 | High | Subject Management |
| FR-010 | Consent Tracking | The system SHALL capture informed consent version, date, and Site attestation for each Subject, linking consent to the applicable Protocol version. | Implements BR-010 | High | Subject Management |

### EDC Data Capture Integration

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-011 | EDC CRF Data Ingestion | The system SHALL receive CRFPage data from EDC via API, validate field-level data against CDASH conventions, and store it in the canonical data model. | Implements BR-001 | Critical | Data Capture & Integration |
| FR-012 | EDC Query Synchronization | The system SHALL synchronize Query records from EDC, track Query status (open, answered, closed), and route escalated Queries to the CTMS monitoring dashboard. | Implements BR-017 | High | Data Capture & Integration |
| FR-013 | EDC Data Reconciliation | The system SHALL reconcile Subject records between EDC and CDOS daily, flagging discrepancies in Subject count, Visit completion, or status for data management review. | Implements BR-001 | High | Data Capture & Integration |

### CTMS Site Management Integration

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-014 | CTMS Site Activation Sync | The system SHALL synchronize Site activation status from CTMS, including Site qualification, regulatory approval, and initiation visit completion dates. | Implements BR-006 | High | Data Capture & Integration |
| FR-015 | CTMS Monitoring Visit Reports | The system SHALL ingest monitoring visit reports from CTMS, extract issue counts and findings, and link them to the corresponding Site and Visit records. | Implements BR-006 | Medium | Data Capture & Integration |
| FR-016 | CTMS Investigator Profile Sync | The system SHALL pull Investigator profiles from CTMS, including CV expiry, financial disclosure status, and training completion, flagging non-compliant Investigators. | Implements BR-006 | Medium | Data Capture & Integration |

### LIMS Lab Data Integration

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-017 | LIMS Lab Result Ingestion | The system SHALL receive LabResult records from LIMS, map them to SDTM LB domain variables, and store them with specimen identifier, analyte, result, unit, and normal range. | Implements BR-002 | High | Data Capture & Integration |
| FR-018 | LIMS Sample Chain of Custody | The system SHALL track Sample records from collection through LIMS receipt, including collection date/time, shipping conditions, and LIMS accession number. | Implements BR-002 | Medium | Data Capture & Integration |
| FR-019 | LIMS Abnormal Value Flagging | The system SHALL flag LabResult values outside normal range or with clinically significant change from baseline, generating automatic Queries to EDC for investigator review. | Implements BR-002 | High | Data Capture & Integration |

### Safety & AE Reporting Integration

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-020 | Safety AE Case Intake | The system SHALL receive AdverseEvent case data from Safety system, classify severity, seriousness, and expectedness, and link to the Subject and Study. | Implements BR-004 | Critical | Data Capture & Integration |
| FR-021 | SAE Expedited Reporting | The system SHALL detect SAEs and SUSARs meeting regulatory reporting thresholds and generate ICSR payloads for submission to Safety within 24 hours of awareness. | Implements BR-004 | Critical | Data Capture & Integration |
| FR-022 | Safety Signal Aggregation | The system SHALL aggregate AdverseEvent data across Studies by MedDRA preferred term, compute proportional reporting ratios, and flag emerging safety signals for pharmacovigilance review. | Implements BR-004 | High | Data Capture & Integration |

### IWRS Randomization Integration

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-023 | IWRS Randomization Request | The system SHALL send a randomization request to IWRS upon Subject eligibility confirmation and receive the treatment assignment, kit number, and stratification factors. | Implements BR-003 | Critical | Data Capture & Integration |
| FR-024 | IWRS Drug Supply Reconciliation | The system SHALL reconcile Dose dispensing records from IWRS against EDC dosing data, flagging discrepancies for clinical supply management. | Implements BR-003 | High | Data Capture & Integration |
| FR-025 | IWRS Unblinding Request | The system SHALL support controlled unblinding requests to IWRS with investigator justification, generating an audit trail entry and notifying the medical monitor. | Implements BR-003 | High | Data Capture & Integration |

### Data Quality & Compliance

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-026 | Audit Trail | The system SHALL maintain a tamper-evident audit trail for every data change, recording the user, timestamp, old value, new value, and reason for change, compliant with 21 CFR Part 11. | Implements BR-009 | Critical | Data Quality & Compliance |
| FR-027 | Role-Based Access Control | The system SHALL enforce role-based access control with roles including Sponsor, CRA, Data Manager, Medical Monitor, and Site User, restricting data visibility and actions per role. | Implements BR-019 | High | Data Quality & Compliance |
| FR-028 | Electronic Signature | The system SHALL support 21 CFR Part 11 compliant electronic signatures for critical actions (data lock, protocol amendment approval, SAE sign-off) with meaning, date/time, and user identity. | Implements BR-009 | High | Data Quality & Compliance |
| FR-029 | Data Validation Rules | The system SHALL execute configurable edit-check rules on incoming data from EDC, LIMS, and Safety, generating Queries for out-of-range, missing, or inconsistent values. | Implements BR-017 | High | Data Quality & Compliance |
| FR-030 | SDTM Mapping and Export | The system SHALL transform canonical data to SDTM v3.4 domains (DM, AE, LB, EX, CM) and produce Define-XML v2.1 compliant submission packages for RegSubmit. | Implements BR-007 | High | Data Quality & Compliance |

### Reporting & Analytics

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-031 | Study Dashboard | The system SHALL provide a real-time dashboard showing enrollment progress, query rates, AE counts, and data completeness percentages per Site and Study. | Implements BR-012 | Medium | Reporting & Analytics |
| FR-032 | Enrollment Forecasting | The system SHALL forecast Subject enrollment completion dates based on historical Site enrollment rates, screen failure rates, and current pipeline of screened Subjects. | Implements BR-014 | Medium | Reporting & Analytics |
| FR-033 | Regulatory Submission Export | The system SHALL produce eCTD-compatible data packages from CDISC SDTM/ADaM datasets for submission to RegSubmit, including validation against FDA/EMA conformance rules. | Implements BR-015 | High | Reporting & Analytics |

### Workflow & Orchestration

| ID | Title | Description | BR Trace | Priority | Category |
|----|-------|-------------|----------|----------|----------|
| FR-034 | Event-Driven Orchestration | The system SHALL publish and consume domain events (e.g., subject.enrolled, ae.reported, visit.completed) via an event bus, enabling loose coupling between EDC, CTMS, LIMS, Safety, and IWRS. | Implements BR-025 | High | Workflow & Orchestration |
| FR-035 | Cross-System Data Reconciliation | The system SHALL perform nightly reconciliation across EDC, CTMS, LIMS, Safety, and IWRS, producing a discrepancy report for data management review. | Implements BR-006 | High | Workflow & Orchestration |

---

## Summary

| Metric | Count |
|--------|-------|
| Total FRs | 35 |
| Critical Priority | 7 |
| High Priority | 20 |
| Medium Priority | 8 |
| Categories | 6 |
| Integration FRs | 15 (FR-011 through FR-025) |
| External Systems Covered | EDC, CTMS, LIMS, Safety, IWRS |
