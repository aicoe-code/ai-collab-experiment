# CDOS Stakeholder Needs

This document identifies the key stakeholder groups for the Clinical Development Operating System (CDOS) and their primary needs. Each need is assigned a unique ID for traceability to business requirements.

---

## 1. Sponsor (Pharmaceutical / Biotech Company)

| Need ID | Need | Description |
|---------|------|-------------|
| SN-001 | Unified Trial Visibility | Sponsors need a single-pane-of-glass view across all ongoing clinical trials, regardless of which CRO or site is executing them. |
| SN-002 | Regulatory Submission Readiness | Sponsors need trial data continuously formatted to CDISC standards (SDTM, ADaM) so regulatory submissions can be prepared rapidly without last-minute data transformation. |
| SN-003 | Cost and Timeline Predictability | Sponsors need real-time enrollment, data quality, and milestone metrics to forecast trial costs and timelines accurately. |
| SN-004 | Data Ownership and Portability | Sponsors must retain full ownership of all trial data and be able to port it between CROs or systems without lock-in. |
| SN-005 | Risk-Based Monitoring Insights | Sponsors need centralized risk indicators and anomaly detection to support risk-based monitoring strategies across sites. |

---

## 2. Contract Research Organization (CRO)

| Need ID | Need | Description |
|---------|------|-------------|
| SN-006 | Multi-Sponsor Interoperability | CROs manage trials for multiple sponsors and need a platform that connects to each sponsor's systems without custom integrations per engagement. |
| SN-007 | Standardized Data Ingestion | CROs need automated ingestion pipelines that pull data from heterogeneous EDC, LIMS, and IWRS systems into a canonical model. |
| SN-008 | Operational Dashboards | CROs need real-time operational dashboards showing site activation, subject enrollment, query resolution, and data cleaning progress across all studies. |
| SN-009 | Audit Trail and Compliance | CROs need complete, immutable audit trails for every data change to satisfy GCP and 21 CFR Part 11 requirements during sponsor and regulatory audits. |
| SN-010 | Scalable Study Provisioning | CROs need to onboard new studies rapidly with configurable workflows, metadata-driven study setup, and reusable templates. |

---

## 3. Clinical Investigation Site

| Need ID | Need | Description |
|---------|------|-------------|
| SN-011 | Simplified Data Entry | Sites need intuitive, single-point-of-entry interfaces that reduce duplicate data entry across EDC, eCOA, and lab systems. |
| SN-012 | Visit Scheduling and Subject Tracking | Sites need integrated visit calendars, subject status tracking, and automated reminders to reduce missed visits and protocol deviations. |
| SN-013 | Query Resolution Efficiency | Sites need centralized query management with clear context, auto-suggestions, and batch resolution capabilities to reduce query cycle time. |
| SN-014 | Training and Access Management | Sites need role-based access control with integrated training verification so only qualified, trained personnel can enter or review data. |

---

## 4. Regulatory Authority (FDA, EMA, PMDA, etc.)

| Need ID | Need | Description |
|---------|------|-------------|
| SN-015 | Standards-Compliant Submissions | Regulators require submissions in CDISC SDTM/ADaM format with Define-XML metadata to enable automated review and cross-study analysis. |
| SN-016 | Data Integrity Assurance | Regulators need confidence that clinical data has not been altered without traceability; immutable audit trails and electronic signatures are essential. |
| SN-017 | Safety Signal Transparency | Regulators need timely, structured safety data (ICSR, SUSAR) with clear causality assessments and MedDRA coding to evaluate safety signals. |
| SN-018 | Inspection Readiness | Regulators expect sponsors and CROs to demonstrate system validation (CSV), data provenance, and 21 CFR Part 11 compliance at any point during or after a trial. |

---

## 5. Patient / Subject

| Need ID | Need | Description |
|---------|------|-------------|
| SN-019 | Informed Consent Transparency | Patients need clear, accessible informed consent processes with the ability to review what data is collected and how it is used. |
| SN-020 | Safety Reporting Accessibility | Patients need easy mechanisms to report adverse events and symptoms, including via mobile and wearable devices. |
| SN-021 | Data Privacy and Rights | Patients need assurance that their personal health data is protected per GDPR, HIPAA, and local regulations, with clear data subject rights (access, rectification, erasure). |
| SN-022 | Trial Access and Matching | Patients need visibility into available trials matching their condition, with streamlined pre-screening and eligibility workflows. |

---

## 6. Data Management / Biostatistics Team

| Need ID | Need | Description |
|---------|------|-------------|
| SN-023 | Clean, Analysis-Ready Data | Data managers and biostatisticians need continuously cleaned, CDISC-mapped data that is ready for statistical analysis without manual rework. |
| SN-024 | Cross-Study Data Harmonization | Teams need consistent data definitions, code lists, and mappings across studies to enable pooled analyses and integrated summaries. |
| SN-025 | Query and Edit-Check Automation | Data managers need configurable edit checks and auto-query generation to catch data inconsistencies at the point of entry. |

---

## 7. Quality Assurance / Compliance

| Need ID | Need | Description |
|---------|------|-------------|
| SN-026 | Validation Documentation | QA teams need automated generation of validation documentation (IQ, OQ, PQ) for GxP-regulated systems. |
| SN-027 | Change Control Traceability | QA needs end-to-end traceability from business requirements through functional specs, code, and test results for every system change. |
| SN-028 | Periodic Access Reviews | QA needs automated periodic reviews of user access rights to ensure least-privilege compliance. |

---

## Traceability Note

Every business requirement (BR-001 through BR-025+) in `business-requirements.md` traces back to one or more of these stakeholder needs (SN-001 through SN-028). This traceability is documented in the `Source Need` column of each BR.
