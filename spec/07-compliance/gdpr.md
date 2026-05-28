# GDPR Compliance

## Overview

This document defines how the CDOS platform satisfies the requirements of
the EU General Data Protection Regulation (Regulation (EU) 2016/679).
Clinical trial data processing involves special category (health) data
under Article 9 and requires explicit legal bases under Article 6.

Reference: EU GDPR 2016/679, EMA Reflection Paper on GCP & GDPR

---

## 1. Data Minimization

### Principle

Only personal data that is adequate, relevant, and limited to what is
necessary for the clinical trial purpose shall be collected and processed.

### Implementation

| Control | Specification | Systems Affected |
|---------|--------------|-----------------|
| Field-level justification | Every personal data field in a [Entity:CRFPage] must have a documented purpose linked to the [Entity:Protocol] objectives | [System:EDC] |
| Collection audit | Periodic review (quarterly) to identify and remove unused or unnecessary personal data fields from CRF designs | [System:EDC] |
| Metadata tagging | Every personal data field is tagged with `pii: true/false`, `special_category: true/false`, `legal_basis` | [System:EDC], [System:CTMS] |
| Pseudonymization by default | All subject identifiers in analytical datasets are pseudonymized before release | [System:EDC] → [System:CTMS] |
| No over-collection | Site staff cannot add free-text fields that capture unstructured PII beyond the approved CRF design | [System:EDC] |

### Data Inventory

| Data Category | Examples | Legal Basis | Retention |
|--------------|----------|-------------|-----------|
| Subject identification | Name, DOB, medical record number | Art. 6(1)(c) legal obligation + Art. 9(2)(i) public health | Duration of trial + 25 years |
| Health data | [Entity:AdverseEvent], [Entity:LabResult], [Entity:Dose], [Entity:Medication] | Art. 9(2)(i) public health | Duration of trial + 25 years |
| Site staff data | [Entity:Investigator] credentials, training records | Art. 6(1)(b) contract | Employment + 5 years |
| Genetic data | Genomic samples linked to [Entity:Sample] | Art. 9(2)(j) research (with safeguards) | Per biobank consent |

---

## 2. Pseudonymization

### Requirement

Personal data used for clinical trial analysis must be pseudonymized —
replacing directly identifying information with a coded identifier such
that the data can no longer be attributed to a specific subject without
additional information.

### Implementation

| Control | Specification | Systems Affected |
|---------|--------------|-----------------|
| Subject ID pseudonymization | All [Entity:Subject] records use a `subject_id` (UUID) as the primary key; real identity stored separately in a restricted identity table | [System:EDC], [System:CTMS] |
| Key separation | The mapping table (subject_id ↔ real identity) is stored in a separate, access-controlled database instance with its own encryption keys | [System:EDC] |
| Analytical datasets | All SDTM/ADaM datasets (DM, AE, LB, etc.) reference `USUBJID` (pseudonym); no direct identifiers present | [System:EDC] → [System:CTMS] |
| Medical imaging | DICOM headers for [Entity:Subject] are de-identified (tags 0010,0010 and 0010,0020 removed or replaced) | [System:Imaging] |
| Wearable data | Device identifiers decoupled from subject identity; data transmitted with pseudonymized subject tag | [System:Wearables] |
| eCOA data | Patient-reported outcomes collected under pseudonym; no name or email stored in eCOA device | [System:eCOA] |

### Pseudonymization Technical Specification

```
ALGORITHM: AES-256-GCM pseudonymization
KEY_DERIVATION: HKDF-SHA256(study_id, random_salt)
IDENTITY_STORE: Separate PostgreSQL database, column-level encryption
REVERSIBILITY: Authorized via key custodian role only (2-person rule)
```

---

## 3. Right to Erasure (Right to Be Forgotten)

### Requirement

Subjects have the right to request erasure of their personal data under
GDPR Article 17, subject to exemptions for legal obligations and public
interest in the area of public health (Art. 17(3)(b) and (c)).

### Clinical Trial Exemptions

| Data Type | Erasure Permitted? | Justification |
|-----------|-------------------|---------------|
| Subject identity data | Yes (after trial completion + mandatory retention) | Art. 17(3)(b) legal obligation exemption during trial |
| Health data in regulatory submissions | No | Art. 17(3)(b) — FDA/EMA legal obligations |
| Safety data ([Entity:AdverseEvent]) | No | Art. 17(3)(c) — public health interest |
| Anonymized analytical data | N/A (no longer personal data) | Once fully anonymized, GDPR no longer applies |
| Site staff training records | Yes (after employment + retention) | Art. 6(1)(b) contract fulfillment |

### Implementation

| Control | Specification | Systems Affected |
|---------|--------------|-----------------|
| Erasure request workflow | Subject withdrawal triggers a workflow: (1) mark subject as withdrawn, (2) cease data collection, (3) retain data per legal obligation, (4) erase identity mapping after retention period | [System:EDC], [System:CTMS] |
| Identity erasure | After mandatory retention expires, destroy the identity mapping table entry; pseudonymized data becomes effectively anonymized | [System:EDC] |
| Cascade erasure | Erasure request propagated to all systems holding subject PII: EDC, eCOA, Wearables, Imaging | [System:EDC], [System:eCOA], [System:Wearables], [System:Imaging] |
| Confirmation | Subject receives confirmation of erasure or explanation of exemption within 30 days | [System:CTMS] |
| Audit trail | Erasure action itself is logged (with the erasure confirmation, not the erased data) | All systems |

---

## 4. Cross-Border Data Transfers

### Requirement

Transfers of personal data outside the European Economic Area (EEA) must
comply with GDPR Chapter V (Articles 44-49).

### Implementation

| Transfer Mechanism | Specification | Applicable Transfers |
|-------------------|--------------|---------------------|
| Standard Contractual Clauses (SCCs) | EU Commission SCCs (2021/914) executed with each non-EEA data recipient | Sponsor ↔ CRO ↔ Central Lab ↔ EDC vendor |
| Adequacy decisions | Where recipient country has adequacy (e.g., UK, Canada, Japan, South Korea) | Direct transfer permitted |
| Binding Corporate Rules | For intra-group transfers within sponsor organization | Sponsor global entities |
| Transfer Impact Assessment (TIA) | Required for each new non-EEA data flow; documents legal framework of recipient country | All new integrations |

### System-Specific Transfer Controls

| System | Data Location | Transfer Path | Mechanism |
|--------|--------------|---------------|-----------|
| [System:EDC] | EU (Frankfurt) | → US sponsor analytics | SCCs + encryption in transit |
| [System:CTMS] | US (Virginia) | Receives from EU sites | SCCs |
| [System:LIMS] | EU (Dublin) | → US central lab HQ | SCCs |
| [System:Safety] | US (New Jersey) | Receives from EU sites | SCCs + Art. 49(1)(b) necessity |
| [System:eTMF] | EU (Frankfurt) | → US regulatory team | SCCs |
| [System:Imaging] | EU (Amsterdam) | → US reading center | SCCs |
| [System:Wearables] | EU (Frankfurt) | → US analytics | SCCs + pseudonymization |
| [System:eCOA] | EU (Dublin) | → US data management | SCCs |
| [System:IWRS] | EU (Frankfurt) | → US clinical supply | SCCs |

---

## 5. Data Residency

### Requirement

Certain data must remain within specific geographic boundaries due to
regulatory, contractual, or sponsor requirements.

### Residency Matrix

| Data Category | Residency Requirement | Implementation |
|--------------|----------------------|----------------|
| EU subject PII | Must remain in EEA unless SCC executed | Identity table stored in EU datacenter ([System:EDC]) |
| China subject PII | Must remain in mainland China (PIPL compliance) | Separate China-region deployment of [System:EDC] |
| Japan subject PII | Must remain in Japan (APPI compliance) | Separate Japan-region deployment |
| Health data (EU) | Primary copy in EEA; replicas outside EEA only with SCC | Geo-replication policy enforced at infrastructure level |
| Audit trails | Co-located with primary data region | [System:EDC], [System:Safety] |

### Technical Controls

| Control | Specification |
|---------|--------------|
| Geo-fencing | Database deployment restricted to approved regions; infrastructure-as-code enforces region tags |
| Data classification | All data records tagged with `residency_zone` (EU, US, CN, JP, GLOBAL) |
| Transfer logging | Every cross-region data movement logged with source region, destination region, legal basis, timestamp |
| Encryption at rest | Per-region encryption keys; keys generated and stored in-region (see [security-encryption.md](./security-encryption.md)) |

---

## 6. Data Protection Impact Assessment (DPIA)

### Trigger Conditions

A DPIA is required per GDPR Article 35 when:

- Processing involves special category data (health data) at scale
- Systematic monitoring of subjects (e.g., [System:Wearables] continuous monitoring)
- New technology deployment (e.g., [System:Imaging] AI-assisted reads)
- Cross-border transfer to a country without adequacy decision

### DPIA Scope for CDOS

| System | DPIA Required? | Rationale |
|--------|---------------|-----------|
| [System:EDC] | Yes | Large-scale processing of health data |
| [System:Safety] | Yes | Health data + cross-border transfer |
| [System:Wearables] | Yes | Systematic monitoring + health data |
| [System:Imaging] | Yes | Health data + potential AI processing |
| [System:eCOA] | Yes | Health data + mobile device processing |
| [System:CTMS] | Yes | Contains PII of investigators and subjects |
| [System:LIMS] | Yes | Health data (lab results linked to subjects) |
| [System:IWRS] | Moderate risk | Contains subject treatment assignments |
| [System:eTMF] | Moderate risk | Contains investigator PII, protocol PII |

---

## 7. Data Protection Officer (DPO) Requirements

- DPO contact information published in all subject-facing consent forms.
- DPO consulted before any new processing activity or system integration.
- DPO reviews all DPIAs and cross-border transfer assessments.
- DPO has direct reporting line to senior management (GDPR Art. 38(3)).

---

## Cross-Reference Map

| GDPR Control | Systems | Entities |
|-------------|---------|----------|
| Data minimization | [System:EDC], [System:CTMS] | [Entity:Subject], [Entity:CRFPage], [Entity:Protocol] |
| Pseudonymization | [System:EDC], [System:CTMS], [System:Imaging], [System:Wearables], [System:eCOA] | [Entity:Subject], [Entity:AdverseEvent], [Entity:LabResult], [Entity:Sample] |
| Right to erasure | [System:EDC], [System:CTMS], [System:eCOA], [System:Wearables], [System:Imaging] | [Entity:Subject] |
| Cross-border transfers | All [System:*] with non-EEA presence | [Entity:Subject], [Entity:AdverseEvent], [Entity:LabResult] |
| Data residency | [System:EDC], [System:Safety] | [Entity:Subject] |
| DPIA | All [System:*] | [Entity:Subject], [Entity:AdverseEvent], [Entity:Sample] |
