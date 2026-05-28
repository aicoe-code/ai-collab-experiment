# 21 CFR Part 11 Compliance

## Overview

This document defines how the CDOS platform satisfies the requirements of
21 CFR Part 11 — the FDA regulation governing electronic records and
electronic signatures in clinical trials. Every [System:*] that creates,
modifies, maintains, archives, retrieves, or transmits electronic records
must comply with the controls specified herein.

Reference: FDA 21 CFR Part 11 (March 1997, current enforcement guidance)

---

## 1. Audit Trails

### Requirement

All electronic records must include computer-generated, time-stamped audit
trails that capture the who, what, when, and why of every record creation,
modification, or deletion.

### Implementation

| Control | Specification | Systems Affected |
|---------|--------------|-----------------|
| Immutable audit log | Append-only audit trail per record; no user can delete or modify past entries | All systems |
| Captured fields | `user_id`, `timestamp` (UTC, ms precision), `action` (CREATE/UPDATE/DELETE), `old_value`, `new_value`, `reason_for_change` | All systems |
| Retention | Audit trails retained for the lifetime of the record + 15 years (per ICH E6(R2) §5.5.3) | All systems |
| Tamper detection | Cryptographic hash chain (SHA-256) linking consecutive audit entries; break in chain = integrity violation | [System:EDC], [System:Safety] |
| Regulatory scope | Audit trail on every field change to [Entity:Subject], [Entity:AdverseEvent], [Entity:LabResult], [Entity:CRFPage], [Entity:Query], [Entity:Dose] | [System:EDC], [System:CTMS], [System:LIMS], [System:IWRS], [System:eCOA] |

### System-Specific Requirements

#### [System:EDC]

- Every CRF data entry, edit, and query resolution must be audited.
- Audit trail must capture the [Entity:Query] lifecycle (issued → answered → closed).
- Reason-for-change is MANDATORY on any modification to [Entity:CRFPage] data after initial save.

#### [System:Safety]

- Every [Entity:AdverseEvent] report, seriousness update, and causality assessment must be audited.
- ICSR submission events must include regulatory submission timestamp and destination authority.

#### [System:IWRS]

- Randomization and drug assignment changes must be audited with unblind disclosure records (if applicable).

---

## 2. Electronic Signatures

### Requirement

Electronic signatures must be legally binding equivalents of handwritten
signatures, applied to electronic records or signing events.

### Implementation

| Control | Specification |
|---------|--------------|
| Signature manifest | Each e-signature produces a signed record containing: `signer_id`, `meaning` (e.g., "authored", "approved", "rejected"), `timestamp`, `signature_hash` |
| Attestation | Signature includes the printed name, date/time, and meaning of the signature — displayed whenever the signed record is viewed |
| Signature-Record Linking | The e-signature is cryptographically bound to the signed data; modifying the data invalidates the signature |
| Identity verification | Multi-factor authentication required before signing: password + OTP or biometric |
| Non-repudiation | Signing event is logged in the immutable audit trail with a unique `signature_id` |

### Scope of E-Signatures

| Signing Event | Entity | System | SOP Reference |
|--------------|--------|--------|---------------|
| Data entry verification | [Entity:CRFPage] | [System:EDC] | SOP-DM-001 |
| Query resolution sign-off | [Entity:Query] | [System:EDC] | SOP-DM-002 |
| SAE causality assessment | [Entity:AdverseEvent] | [System:Safety] | SOP-SAF-001 |
| Laboratory result review | [Entity:LabResult] | [System:LIMS] | SOP-LAB-001 |
| Protocol approval | [Entity:Protocol] | [System:CTMS] | SOP-PROT-001 |
| Regulatory submission | [Entity:Submission] | [System:eTMF] | SOP-REG-001 |
| Medical monitoring sign-off | [Entity:AdverseEvent] | [System:Safety] | SOP-MM-001 |

---

## 3. System Validation (CSV)

### Requirement

Systems used to create, maintain, or transmit electronic records must be
validated to ensure accuracy, reliability, and consistent intended
performance. See also [gxp-validation.md](./gxp-validation.md) for full
CSV lifecycle details.

### Validation Checklist per System

| System | GAMP 5 Category | Validation Status Required | Periodic Review |
|--------|----------------|---------------------------|-----------------|
| [System:EDC] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |
| [System:CTMS] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |
| [System:LIMS] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |
| [System:Safety] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |
| [System:IWRS] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |
| [System:eCOA] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |
| [System:eTMF] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |
| [System:Imaging] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |
| [System:Wearables] | Cat 5 (Custom) | Full CSV (IQ/OQ/PQ) + code review | Semi-annual |
| [System:RegSubmit] | Cat 4 (Configured) | Full CSV (IQ/OQ/PQ) | Annual |

---

## 4. Access Controls

### Requirement

System access must be limited to authorized individuals with a defined role
and scope. The system must enforce separation of duties.

### RBAC Model

| Role | Description | Systems | Permissions |
|------|------------|---------|-------------|
| Data Entry | Site staff entering CRF data | [System:EDC], [System:eCOA] | CREATE, READ own-site records |
| CRA / Monitor | Clinical research associate | [System:EDC], [System:CTMS] | READ, issue queries, verify data |
| Data Manager | Central data management | [System:EDC], [System:CTMS], [System:LIMS] | CREATE, READ, UPDATE, close queries |
| Medical Monitor | Safety oversight | [System:Safety], [System:EDC] | READ, assess causality, approve reports |
| Biostatistician | Statistical analysis | [System:EDC] | READ (blinded/unblinded per role) |
| System Admin | Platform administration | All systems | User provisioning, config (no data CRUD) |
| Auditor | QA / regulatory inspection | All systems | READ-only to all records + audit trails |
| Sponsor | Study oversight | [System:CTMS], [System:eTMF] | READ aggregated dashboards |

### Separation of Duties

- No user may hold both "Data Entry" and "CRA / Monitor" roles for the same [Entity:Study].
- No user may hold both "System Admin" and any data-access role.
- E-signature meaning "approved" requires a different user than the one who created the record.

### Authentication Controls

| Control | Specification |
|---------|--------------|
| Password policy | Minimum 12 characters, complexity rules, 90-day rotation |
| Multi-factor authentication | Required for all e-signature actions and admin access |
| Session timeout | 30 minutes of inactivity → auto-logout |
| Failed login lockout | 5 failed attempts → account locked for 30 minutes |
| Unique user IDs | Shared accounts are PROHIBITED; every user has a unique ID |

---

## 5. SOP Requirements

### Standard Operating Procedures Required

| SOP ID | Title | Scope | Review Cycle |
|--------|-------|-------|-------------|
| SOP-CSV-001 | Computer System Validation Lifecycle | All [System:*] | Biennial |
| SOP-CSV-002 | Change Control for Validated Systems | All [System:*] | Biennial |
| SOP-DM-001 | Electronic Data Capture Procedures | [System:EDC] | Biennial |
| SOP-DM-002 | Data Query Management | [System:EDC] | Biennial |
| SOP-DM-003 | Data Transfer and Reconciliation | [System:EDC] → [System:CTMS] | Biennial |
| SOP-SAF-001 | Adverse Event Reporting and Safety Surveillance | [System:Safety] | Biennial |
| SOP-LAB-001 | Laboratory Data Management | [System:LIMS] | Biennial |
| SOP-PROT-001 | Protocol Document Control | [System:CTMS], [System:eTMF] | Biennial |
| SOP-REG-001 | Regulatory Submission Procedures | [System:RegSubmit] | Biennial |
| SOP-SEC-001 | User Access Management and Provisioning | All systems | Annual |
| SOP-SEC-002 | Audit Trail Review and Monitoring | All systems | Annual |
| SOP-SEC-003 | Electronic Signature Policy | All systems | Annual |

### SOP Compliance Requirements

- All SOPs must be version-controlled in [System:eTMF].
- SOP training must be completed and attested (via e-signature) before a user is granted system access.
- SOP deviations must be logged, investigated, and CAPA applied within 30 days.

---

## Cross-Reference Map

This table maps Part 11 controls to the systems in the CDOS integration layer
(`04-integrations/`) and entities in the data model (`02-data-models/`).

| Part 11 Control | Systems | Entities |
|-----------------|---------|----------|
| Audit trails | [System:EDC], [System:CTMS], [System:LIMS], [System:Safety], [System:IWRS], [System:eCOA], [System:eTMF], [System:RegSubmit] | [Entity:Subject], [Entity:AdverseEvent], [Entity:LabResult], [Entity:CRFPage], [Entity:Query], [Entity:Dose], [Entity:Protocol], [Entity:Submission] |
| E-signatures | [System:EDC], [System:CTMS], [System:LIMS], [System:Safety], [System:eTMF] | [Entity:CRFPage], [Entity:Query], [Entity:AdverseEvent], [Entity:LabResult], [Entity:Protocol], [Entity:Submission] |
| System validation | All [System:*] | All [Entity:*] |
| Access controls | All [System:*] | All [Entity:*] |
| SOP compliance | All [System:*] | [Entity:Protocol], [Entity:Submission] |
