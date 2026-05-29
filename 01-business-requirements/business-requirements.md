# CDOS Business Requirements

This document defines the business requirements for the Clinical Development Operating System (CDOS). Each requirement is uniquely identified and traced to one or more stakeholder needs defined in `stakeholder-needs.md`.

**Priority Legend:**
- **P0 — Critical**: Must be in the initial release; trial operations cannot function without it.
- **P1 — High**: Required for core value proposition; targeted for initial release.
- **P2 — Medium**: Important for full adoption; planned for release 2.
- **P3 — Low**: Nice-to-have; future roadmap.

---

## Data Integration and Connectivity

| BR ID | Title | Description | Priority | Source Need(s) |
|-------|-------|-------------|----------|----------------|
| BR-001 | Unified Data Ingestion from EDC Systems | CDOS shall ingest clinical data from multiple EDC systems (Medidata Rave, Oracle InForm, Veeva Vault CDMS, Castor) via standardized adapters, normalizing all data into a canonical Subject-Visit-CRFPage model. | P0 | SN-001, SN-006, SN-007 |
| BR-002 | Laboratory Data Integration | CDOS shall integrate with laboratory information management systems (LIMS) to receive LabResult data mapped to SDTM LB domain standards, including reference ranges and specimen tracking. | P0 | SN-007, SN-023 |
| BR-003 | IWRS/RTMS Integration | CDOS shall connect to Interactive Web Response Systems (IWRS) for real-time randomization, drug assignment, and kit management data, ensuring Subject assignment is synchronized across all systems. | P0 | SN-007, SN-001 |
| BR-004 | Safety System Integration | CDOS shall integrate with pharmacovigilance systems (Argus Safety, ArisGlobal) to receive and transmit AdverseEvent data, including SAE and SUSAR notifications with MedDRA coding. | P0 | SN-017, SN-001 |
| BR-005 | eCOA and Wearable Data Ingestion | CDOS shall ingest electronic clinical outcome assessment (eCOA) data and wearable/IoT sensor data, mapping patient-reported outcomes and device measurements to the canonical data model. | P1 | SN-020, SN-023 |
| BR-006 | CTMS Synchronization | CDOS shall bidirectionally synchronize study metadata, site activation status, enrollment milestones, and visit schedules with CTMS platforms (Veeva Vault CTMS, Oracle Siebel CTMS). | P1 | SN-003, SN-008 |

---

## Data Standards and Compliance

| BR ID | Title | Description | Priority | Source Need(s) |
|-------|-------|-------------|----------|----------------|
| BR-007 | CDISC SDTM Mapping Engine | CDOS shall provide a configurable transformation engine that maps canonical clinical data to CDISC SDTM v3.4 domain models (DM, AE, LB, EX, CM, etc.) with Define-XML v2.1 metadata generation. | P0 | SN-002, SN-015, SN-023 |
| BR-008 | ADaM Dataset Generation | CDOS shall generate CDISC ADaM v2.1 analysis-ready datasets from SDTM-mapped data, supporting standard ADaM structures (ADSL, ADAE, ADLB, etc.) with traceability to source SDTM domains. | P1 | SN-002, SN-015, SN-024 |
| BR-009 | 21 CFR Part 11 Compliance | CDOS shall comply with 21 CFR Part 11 requirements including: (a) immutable audit trails for all data changes, (b) electronic signatures with signer identity, meaning, and timestamp, (c) system access controls with unique user IDs and passwords. | P0 | SN-009, SN-016, SN-018 |
| BR-010 | GDPR and Data Privacy Compliance | CDOS shall implement data privacy controls compliant with GDPR and HIPAA, including pseudonymization of Subject identifiers, data subject rights management (access, rectification, erasure), consent management, and data residency controls. | P0 | SN-021, SN-018 |
| BR-011 | GxP Computer System Validation Support | CDOS shall support GxP computer system validation by providing automated documentation of requirements-to-test traceability, version-controlled configuration, and validation-ready audit reports. | P1 | SN-026, SN-027, SN-018 |

---

## Operational Visibility and Analytics

| BR ID | Title | Description | Priority | Source Need(s) |
|-------|-------|-------------|----------|----------------|
| BR-012 | Cross-Study Dashboard | CDOS shall provide a configurable dashboard showing real-time metrics across all studies: enrollment progress, data entry timeliness, query rates, adverse event counts, and milestone status. | P0 | SN-001, SN-003, SN-008 |
| BR-013 | Risk-Based Monitoring Indicators | CDOS shall compute and display site-level risk indicators (enrollment velocity, data completeness, query resolution time, protocol deviation rate) to support risk-based monitoring strategies. | P1 | SN-005, SN-008 |
| BR-014 | Enrollment Forecasting | CDOS shall generate enrollment forecasts based on historical site performance, current screening pipelines, and seasonal patterns, providing sponsors with cost and timeline predictions. | P1 | SN-003, SN-008 |
| BR-015 | Regulatory Submission Package Assembly | CDOS shall assemble regulatory submission packages by combining SDTM/ADaM datasets, Define-XML, analysis reports, and study documentation into eCTD-compatible structures for RegSubmit system integration. | P1 | SN-002, SN-015 |

---

## Study Management and Workflow

| BR ID | Title | Description | Priority | Source Need(s) |
|-------|-------|-------------|----------|----------------|
| BR-016 | Metadata-Driven Study Configuration | CDOS shall support metadata-driven study setup where protocol parameters (visits, forms, edit checks, code lists) are defined in configuration rather than custom code, enabling rapid study provisioning. | P0 | SN-010, SN-006 |
| BR-017 | Automated Query Generation | CDOS shall generate data clarification queries automatically based on configurable edit checks, cross-field validations, and out-of-range detection, attaching full context (visit, form, field, expected vs. actual) to each query. | P0 | SN-013, SN-025 |
| BR-018 | Visit Scheduling and Calendar Management | CDOS shall provide integrated visit scheduling with protocol-defined visit windows, automated reminders to sites, tracking of missed/early/late visits, and protocol deviation flagging. | P1 | SN-012, SN-008 |
| BR-019 | Role-Based Access Control | CDOS shall implement role-based access control (RBAC) with predefined roles (Sponsor Admin, CRA, Data Manager, Investigator, Coordinator, Monitor, Biostatistician, QA Auditor) and configurable permissions per study, site, and data domain. | P0 | SN-014, SN-009, SN-028 |
| BR-020 | eTMF Document Integration | CDOS shall integrate with electronic Trial Master File (eTMF) systems to synchronize essential trial documents, linking protocol amendments, IRB approvals, and investigator CVs to their associated studies and sites. | P2 | SN-027, SN-018 |

---

## Patient and Site Experience

| BR ID | Title | Description | Priority | Source Need(s) |
|-------|-------|-------------|----------|----------------|
| BR-021 | Electronic Informed Consent (eConsent) | CDOS shall support electronic informed consent workflows where subjects can review consent documents digitally, ask questions, and sign electronically, with full version tracking and audit trail per 21 CFR Part 11. | P1 | SN-019, SN-009 |
| BR-022 | Subject Data Portability | CDOS shall enable sponsors to export all Subject-level data in open, standards-based formats (CDISC ODM v2.0, CSV, JSON) at any time, ensuring no vendor lock-in and facilitating CRO transitions. | P1 | SN-004, SN-006 |
| BR-023 | Adverse Event Reporting Interface | CDOS shall provide a streamlined interface for sites to report AdverseEvents with structured data entry (onset, severity, causality, outcome) and automated MedDRA coding suggestions, with immediate escalation for SAEs and SUSARs. | P0 | SN-017, SN-020 |
| BR-024 | Cross-Study Data Harmonization | CDOS shall maintain a central data dictionary with consistent variable definitions, code lists, and mapping rules across studies, enabling pooled analyses and integrated summaries of safety and efficacy data. | P2 | SN-024, SN-023 |
| BR-025 | Audit Trail and Compliance Reporting | CDOS shall provide on-demand audit trail reports showing every data change (who, what, when, why) for any data point, with filtering by study, site, subject, date range, and change type, exportable for regulatory inspection. | P0 | SN-009, SN-016, SN-018, SN-027 |
| BR-026 | Periodic Access Review Automation | CDOS shall automate periodic access reviews by generating reports of active user accounts, last login dates, role assignments, and flagged dormant or over-privileged accounts for QA review. | P2 | SN-028, SN-014 |

---

## Traceability Summary

Each BR above traces to at least one stakeholder need (SN-xxx) as documented in the Source Need(s) column. This ensures full traceability from stakeholder needs through business requirements to downstream functional and technical specifications.
