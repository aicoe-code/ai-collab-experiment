# GxP Validation

## Overview

This document defines the Computer System Validation (CSV) approach for the
CDOS platform, following GAMP 5 (ISPE, 2nd Edition) and ICH E6(R2) GCP
requirements. Every system that supports GxP-regulated activities must be
validated before production use and maintained in a validated state
throughout its lifecycle.

Reference: ISPE GAMP 5, ICH E6(R2), FDA Guidance on Computerized Systems
in Clinical Investigations (2007), EU Annex 11

---

## 1. GAMP 5 Categories

### System Classification

Each system is classified by its GAMP 5 category, which determines the
rigor and depth of validation activities.

| System | GAMP 5 Category | Rationale | Validation Approach |
|--------|----------------|-----------|---------------------|
| [System:EDC] | Cat 4 — Configured Product | Commercial EDC with study-specific configuration (CRFs, edit checks, workflows) | Full CSV: IQ + OQ + PQ; configuration-specific test scripts |
| [System:CTMS] | Cat 4 — Configured Product | Commercial CTMS with customized dashboards, workflows, and reports | Full CSV: IQ + OQ + PQ |
| [System:LIMS] | Cat 4 — Configured Product | Commercial LIMS with configured panels, reference ranges, and result workflows | Full CSV: IQ + OQ + PQ |
| [System:Safety] | Cat 4 — Configured Product | Commercial safety database with configured MedDRA coding and report generation | Full CSV: IQ + OQ + PQ |
| [System:IWRS] | Cat 4 — Configured Product | Commercial IWRS with study-specific randomization and supply algorithms | Full CSV: IQ + OQ + PQ |
| [System:eCOA] | Cat 4 — Configured Product | Commercial eCOA platform with configured instruments and visit schedules | Full CSV: IQ + OQ + PQ |
| [System:eTMF] | Cat 4 — Configured Product | Commercial eTMF with configured filing structures and retention rules | Full CSV: IQ + OQ + PQ |
| [System:Imaging] | Cat 4 — Configured Product | Commercial imaging platform with configured read paradigms | Full CSV: IQ + OQ + PQ |
| [System:Wearables] | Cat 5 — Custom Application | Bespoke firmware/software for wearable devices; custom data pipelines | Full CSV: IQ + OQ + PQ + code review + unit tests |
| [System:RegSubmit] | Cat 4 — Configured Product | Commercial regulatory submission platform with configured eCTD templates | Full CSV: IQ + OQ + PQ |

### Validation Depth by Category

| Activity | Cat 3 (Standard) | Cat 4 (Configured) | Cat 5 (Custom) |
|----------|-----------------|-------------------|----------------|
| Vendor assessment | Required | Required | Required |
| Functional requirements | — | Required | Required |
| Design specifications | — | Configuration spec | Full design spec |
| IQ | Infrastructure only | Full IQ | Full IQ |
| OQ | Vendor OQ sufficient | Config-specific OQ | Full OQ |
| PQ | Simplified PQ | Business-process PQ | Full PQ |
| Code review | — | — | Required |
| Unit/integration tests | — | — | Required |

---

## 2. CSV Lifecycle

### Phases

```
Phase 1: Planning
  ├── Validation Master Plan (VMP)
  ├── Risk Assessment (GAMP 5 risk-based approach)
  ├── System classification (see §1)
  └── Validation plan per system

Phase 2: Specification
  ├── User Requirements Specification (URS)
  ├── Functional Requirements Specification (FRS) — Cat 4/5
  ├── Configuration Specification — Cat 4
  ├── Design Specification — Cat 5
  └── Traceability Matrix (URS → FRS → Test Cases)

Phase 3: Verification (IQ/OQ/PQ)
  ├── Installation Qualification (IQ)
  ├── Operational Qualification (OQ)
  ├── Performance Qualification (PQ)
  └── Test execution with documented results

Phase 4: Reporting
  ├── Validation Summary Report (VSR)
  ├── Traceability Matrix (final)
  ├── Exception/deviation log
  └── Go-Live approval (QA sign-off via e-signature)

Phase 5: Maintenance
  ├── Periodic review (see §5)
  ├── Change control (see §4)
  ├── Re-validation triggers
  └── Retirement/decommission
```

---

## 3. IQ / OQ / PQ Specifications

### 3.1 Installation Qualification (IQ)

IQ verifies that the system is installed correctly per vendor specifications
and infrastructure requirements.

| IQ Checkpoint | Specification | Systems |
|--------------|--------------|---------|
| Software version | Verify installed version matches vendor release notes | All [System:*] |
| Infrastructure | Verify server OS, database version, middleware versions match specifications | All [System:*] |
| Network configuration | Verify firewall rules, DNS, load balancer, SSL/TLS certificates | All [System:*] |
| Integration endpoints | Verify connectivity to all defined API endpoints per adapter contracts | All [System:*] |
| Encryption modules | Verify encryption libraries (AES-256, TLS 1.3) installed and operational | All [System:*] |
| Audit trail mechanism | Verify audit trail database/tables created and configured | [System:EDC], [System:Safety], [System:CTMS] |
| Backup/recovery | Verify backup agents installed and tested | All [System:*] |

### 3.2 Operational Qualification (OQ)

OQ verifies that the system operates as intended across its configured
functionality under normal and boundary conditions.

| OQ Test Area | Specification | Systems |
|-------------|--------------|---------|
| User access controls | Verify RBAC enforcement: authorized access granted, unauthorized access denied | All [System:*] |
| Audit trail integrity | Verify all CRUD operations generate audit entries with correct timestamps and user IDs | [System:EDC], [System:Safety], [System:CTMS] |
| E-signature workflow | Verify signature creation, display of meaning/identity, and tamper detection | [System:EDC], [System:Safety] |
| Data validation rules | Verify edit checks, range checks, and cross-field validations per CRF design | [System:EDC] |
| Report generation | Verify predefined reports produce correct output against known test data | [System:CTMS], [System:LIMS] |
| Integration data flow | Verify end-to-end data transfer between connected systems | [System:EDC] → [System:CTMS], [System:LIMS] → [System:EDC] |
| Error handling | Verify system handles invalid inputs, timeouts, and partial failures gracefully | All [System:*] |
| Pseudonymization | Verify subject identity separation and pseudonym integrity | [System:EDC] |

### 3.3 Performance Qualification (PQ)

PQ verifies that the system performs reliably under real-world conditions
using actual study data and workflows.

| PQ Scenario | Acceptance Criteria | Systems |
|------------|-------------------|---------|
| Multi-site data entry | 50 concurrent users entering CRF data with <2s response time (p95) | [System:EDC] |
| Concurrent query resolution | 100 concurrent query operations with no data loss | [System:EDC] |
| Safety case processing | Process 500 SAE reports in 8 hours without errors | [System:Safety] |
| Lab data import | Import 10,000 lab results in batch with zero data integrity errors | [System:LIMS] |
| IWRS randomization | Randomize 200 subjects in 1 hour with correct stratification balance | [System:IWRS] |
| eTMF document upload | Upload 1,000 documents (avg 5MB) with correct metadata and filing | [System:eTMF] |
| End-to-end pipeline | Subject enrollment → CRF entry → query → lab import → safety report → SDTM export | All systems |

---

## 4. Change Control

### Requirement

All changes to validated systems must go through a formal change control
process to maintain the validated state.

### Change Control Process

```
Step 1: Change Request
  ├── Requestor submits Change Request Form (CRF)
  ├── Description of change, justification, affected systems
  └── Risk classification: Minor / Major / Critical

Step 2: Impact Assessment
  ├── QA assesses impact on validated state
  ├── Determine re-validation scope
  └── Assess impact on connected systems (integration chain)

Step 3: Approval
  ├── Minor: Data Manager + QA approval
  ├── Major: Data Manager + QA + Medical Monitor approval
  └── Critical: Validation Board approval

Step 4: Implementation
  ├── Implement per approved plan
  ├── Execute test scripts (OQ re-test minimum; PQ if major)
  └── Document results

Step 5: Closure
  ├── QA reviews and approves implementation
  ├── Update validation documentation (traceability matrix, VSR)
  ├── E-signature on change approval
  └── Update system inventory
```

### Change Classification

| Classification | Examples | Re-Validation Required |
|---------------|---------|----------------------|
| Minor | Cosmetic UI change, non-GxP report update | OQ subset re-test |
| Major | New CRF field, new edit check, new integration endpoint | Full OQ + targeted PQ |
| Critical | Database migration, major version upgrade, security patch | Full IQ/OQ/PQ |
| Emergency | Production hotfix for data integrity issue | Expedited: full OQ within 5 business days |

### System-Specific Change Control

| System | Change Control Authority | Vendor Update Cadence |
|--------|------------------------|----------------------|
| [System:EDC] | Sponsor QA + Data Management | Quarterly vendor releases |
| [System:CTMS] | Sponsor QA + Clinical Operations | Semi-annual vendor releases |
| [System:LIMS] | Sponsor QA + Lab Director | Annual vendor releases |
| [System:Safety] | Sponsor QA + Pharmacovigilance | Quarterly vendor releases |
| [System:IWRS] | Sponsor QA + Clinical Supply | As-needed vendor releases |
| [System:eCOA] | Sponsor QA + Clinical Operations | Semi-annual vendor releases |
| [System:Wearables] | Sponsor QA + Engineering | Continuous (CI/CD with validation gates) |

---

## 5. Periodic Review

### Requirement

Validated systems must undergo periodic review to confirm they remain in
a validated state.

### Review Schedule

| System | Review Frequency | Review Scope |
|--------|-----------------|-------------|
| [System:EDC] | Annual | Audit trail integrity, access controls, performance metrics, change log review |
| [System:CTMS] | Annual | Configuration drift check, access controls, reporting accuracy |
| [System:LIMS] | Annual | Interface validation, reference range accuracy, calibration records |
| [System:Safety] | Annual | Case processing accuracy, MedDRA version alignment, submission compliance |
| [System:IWRS] | Annual | Randomization integrity, supply chain accuracy |
| [System:eCOA] | Annual | Instrument configuration, data capture integrity |
| [System:eTMF] | Annual | Filing completeness, retention compliance, access controls |
| [System:Imaging] | Annual | Image integrity, de-identification verification |
| [System:Wearables] | Semi-annual | Firmware version control, data pipeline integrity, security patches |
| [System:RegSubmit] | Annual | Template accuracy, submission traceability |

### Periodic Review Checklist

```
□ All change requests since last review are closed and documented
□ No unauthorized changes detected (configuration drift scan)
□ Audit trail integrity verified (hash chain intact)
□ User access review (terminated users removed, role changes applied)
□ Backup and recovery tested successfully
□ Performance metrics within acceptable range
□ Vendor security patches applied and re-validated
□ Training records up to date for all system users
□ SOP compliance verified (no open deviations)
□ Results documented in Periodic Review Report (QA e-signature)
```

---

## 6. Vendor Qualification

### Requirement

Third-party system vendors must be qualified before their products are
deployed in a GxP environment.

### Vendor Assessment Areas

| Area | Assessment Criteria | Documentation |
|------|-------------------|---------------|
| Quality management | ISO 9001 or equivalent certification | Certificate copy on file |
| Security practices | SOC 2 Type II or ISO 27001 | Audit report review |
| Data privacy | GDPR compliance program | DPA executed |
| Business continuity | DR plan, RTO/RPO commitments | DR test results |
| Regulatory track record | FDA warning letters, consent decrees | Regulatory history check |
| Release management | Patch cadence, deprecation policy | Vendor SLA |
| Support model | Response times, escalation paths | Support agreement |

### Vendor Assessment Schedule

- Initial qualification: Before contract execution
- Re-qualification: Every 3 years or upon material vendor change
- Triggered re-qualification: FDA warning letter, data breach, service failure

---

## Cross-Reference Map

| GxP Control | Systems | Entities |
|-------------|---------|----------|
| GAMP 5 classification | All [System:*] | — |
| IQ/OQ/PQ | All [System:*] | [Entity:Subject], [Entity:AdverseEvent], [Entity:LabResult], [Entity:CRFPage], [Entity:Query] |
| Change control | All [System:*] | All [Entity:*] |
| Periodic review | All [System:*] | All [Entity:*] |
| Vendor qualification | All [System:*] | — |
| Traceability | All [System:*] | All [Entity:*] |
