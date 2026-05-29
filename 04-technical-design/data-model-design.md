# CDOS — Data Model Design

## 1. Overview

This document defines the canonical data model for CDOS. The model serves as the single source of truth for all clinical data flowing through the platform. It satisfies:
- **04-B**: ≥8 canonical entities with ER diagram, relationships, design rationale
- Canonical entity names match ALIGNMENT_RULES.md exactly (case-sensitive)

---

## 2. Design Principles

| Principle | Description |
|-----------|-------------|
| Canonical Form | All source data is normalized to these entities before any downstream processing |
| UUID Primary Keys | All entities use UUID v4 for globally unique identification |
| Immutable Events | Domain events are append-only for auditability (21 CFR Part 11) |
| Soft Deletes | No data is physically deleted; `deleted_at` timestamp marks logical deletion |
| Temporal Tracking | `created_at`, `updated_at` on every entity; `effective_start`, `effective_end` on time-varying data |
| CDISC Alignment | Canonical attributes map directly to SDTM/ADaM variables |

---

## 3. Entity Catalog (14 Entities)

| # | Entity | Abbrev | Description | Primary Key |
|---|--------|--------|-------------|-------------|
| 1 | Study | study | A clinical trial | study_id (UUID) |
| 2 | Subject | subj | A participant enrolled in a study | subject_id (UUID) |
| 3 | Site | site | A clinical investigation site | site_id (UUID) |
| 4 | Investigator | inv | A principal/sub-investigator | investigator_id (UUID) |
| 5 | Visit | visit | A scheduled study visit | visit_id (UUID) |
| 6 | AdverseEvent | ae | An adverse event | adverse_event_id (UUID) |
| 7 | LabResult | lab | A laboratory test result | lab_result_id (UUID) |
| 8 | Medication | med | A concomitant/study medication | medication_id (UUID) |
| 9 | Protocol | proto | Study protocol metadata | protocol_id (UUID) |
| 10 | Dose | dose | A dose of study drug | dose_id (UUID) |
| 11 | Query | query | A data clarification request | query_id (UUID) |
| 12 | CRFPage | crf | A case report form page | crf_page_id (UUID) |
| 13 | Sample | sample | A biological specimen | sample_id (UUID) |
| 14 | Submission | subm | A regulatory submission artifact | submission_id (UUID) |

---

## 4. Entity-Relationship Diagram

```
                                    ┌──────────────┐
                                    │   Protocol    │
                                    │──────────────│
                                    │ protocol_id   │
                                    │ study_id (FK) │
                                    │ version       │
                                    │ effective_date│
                                    └──────┬───────┘
                                           │ 1
                                           │
                                           │ N
┌──────────┐    1    N ┌──────────┐    N   ┌──────────┐
│   Site   │◀─────────│  Study   │───────▶│   Visit  │
│──────────│           │──────────│        │──────────│
│ site_id  │           │ study_id │        │ visit_id │
│ name     │           │ title    │        │ study_id │
│ country  │           │ phase    │        │ subject_id│
│ status   │           │ status   │        │ visit_num│
└────┬─────┘           └────┬─────┘        │ scheduled│
     │                      │              └──────────┘
     │ 1                    │ 1
     │                      │
     │ N                    │ N
┌────┴──────────┐     ┌────┴──────────┐
│ Investigator  │     │   Subject     │
│───────────────│     │───────────────│
│investigator_id│     │ subject_id    │
│ site_id (FK)  │     │ study_id (FK) │
│ name          │     │ site_id (FK)  │
│ role          │     │ status        │
│ specialty     │     │ enrolled_date │
└───────────────┘     └───────┬───────┘
                              │ 1
                ┌─────────────┼─────────────┐
                │ N           │ N           │ N
          ┌─────┴──────┐ ┌───┴────────┐ ┌──┴──────────┐
          │AdverseEvent│ │ LabResult  │ │ Medication  │
          │────────────│ │────────────│ │─────────────│
          │ae_id       │ │lab_result_id││medication_id│
          │subject_id  │ │subject_id  │ │subject_id   │
          │visit_id(FK)│ │visit_id(FK)│ │visit_id(FK) │
          │term        │ │test_name   │ │ drug_name   │
          │severity    │ │result_value│ │ dose_amount │
          │seriousness │ │unit        │ │ start_date  │
          │onset_date  │ │normal_low  │ └─────────────┘
          └────────────┘ │normal_high │
                         └────────────┘

          ┌───────────┐
          │   Dose    │
          │───────────│
          │ dose_id   │
          │subject_id │
          │ drug_name │
          │ amount    │
          │ route     │
          │ datetime  │
          └───────────┘

┌──────────┐         ┌──────────┐         ┌──────────────┐
│ CRFPage  │ 1    N  │  Query   │         │   Sample     │
│──────────│────────▶│──────────│         │──────────────│
│crf_page_id│        │ query_id │         │ sample_id    │
│subject_id│         │crf_page_id(FK)     │ subject_id   │
│ form_name│         │ question │         │ visit_id(FK) │
│ status   │         │ status   │         │ specimen_type│
│ data_json│         │ response │         │ collected_dt │
└──────────┘         └──────────┘         └──────────────┘

                    ┌──────────────┐
                    │  Submission  │
                    │──────────────│
                    │submission_id │
                    │ study_id (FK)│
                    │ type         │
                    │ status       │
                    │ package_path │
                    │ submitted_at │
                    │ agency       │
                    └──────────────┘
```

---

## 5. Entity Definitions

### 5.1 Study

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| study_id | UUID | PK, NOT NULL | Unique study identifier | STUDYID |
| title | VARCHAR(500) | NOT NULL | Full study title | — |
| protocol_number | VARCHAR(50) | UNIQUE, NOT NULL | Protocol identifier | — |
| phase | ENUM | NOT NULL | Phase I/II/III/IV | — |
| status | ENUM | NOT NULL | PLANNED, ACTIVE, COMPLETED, TERMINATED | — |
| sponsor_id | UUID | FK → Organization | Sponsoring organization | — |
| therapeutic_area | VARCHAR(100) | | Therapeutic area | — |
| indication | VARCHAR(500) | | Disease/condition being studied | — |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() | Creation timestamp | — |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp | — |
| deleted_at | TIMESTAMP | NULL | Soft delete marker | — |

**Design Rationale**: Study is the top-level aggregate root. All other entities have a direct or transitive foreign key to Study, enabling row-level security and data partitioning.

### 5.2 Subject

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| subject_id | UUID | PK, NOT NULL | Unique subject identifier | USUBJID |
| study_id | UUID | FK → Study, NOT NULL | Parent study | STUDYID |
| site_id | UUID | FK → Site, NOT NULL | Enrolling site | SITEID |
| subject_number | VARCHAR(20) | NOT NULL | Subject number within study | SUBJID |
| status | ENUM | NOT NULL | SCREENED, ENROLLED, COMPLETED, WITHDRAWN | — |
| enrolled_date | DATE | | Date of enrollment | RFSTDTC |
| withdrawal_date | DATE | | Date of withdrawal | RFENDTC |
| demographics | JSONB | | Age, sex, race, ethnicity | AGE, SEX, RACE, ETHNIC |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |
| deleted_at | TIMESTAMP | NULL | | — |

**Design Rationale**: Subject is the central entity linking to almost all clinical data. The `demographics` JSONB field allows flexible storage of CDISC DM domain variables without schema changes.

### 5.3 Site

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| site_id | UUID | PK, NOT NULL | Unique site identifier | SITEID |
| study_id | UUID | FK → Study, NOT NULL | Parent study | STUDYID |
| name | VARCHAR(200) | NOT NULL | Site name | — |
| site_number | VARCHAR(20) | NOT NULL | Site number within study | SITEID |
| country | CHAR(3) | NOT NULL | ISO 3166-1 alpha-3 | COUNTRY |
| status | ENUM | NOT NULL | PENDING, ACTIVE, CLOSED | — |
| address | JSONB | | Full address | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.4 Investigator

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| investigator_id | UUID | PK, NOT NULL | Unique investigator identifier | — |
| site_id | UUID | FK → Site, NOT NULL | Assigned site | SITEID |
| name | VARCHAR(200) | NOT NULL | Full name | INVNAM |
| role | ENUM | NOT NULL | PI, SUB_INVESTIGATOR | — |
| specialty | VARCHAR(100) | | Medical specialty | — |
| email | VARCHAR(255) | | Contact email | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.5 Visit

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| visit_id | UUID | PK, NOT NULL | Unique visit identifier | VISITNUM |
| study_id | UUID | FK → Study, NOT NULL | Parent study | STUDYID |
| subject_id | UUID | FK → Subject, NOT NULL | Subject being visited | USUBJID |
| visit_number | INTEGER | NOT NULL | Sequential visit number | VISITNUM |
| visit_name | VARCHAR(50) | NOT NULL | Visit label | VISIT |
| scheduled_date | DATE | NOT NULL | Planned visit date | VISITDTC |
| actual_date | DATE | | Actual visit date | — |
| status | ENUM | NOT NULL | SCHEDULED, COMPLETED, MISSED | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.6 AdverseEvent

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
|| ae_id | UUID | PK, NOT NULL | Unique AE identifier | AESEQ |
| subject_id | UUID | FK → Subject, NOT NULL | Affected subject | USUBJID |
| visit_id | UUID | FK → Visit | Visit when reported | VISITNUM |
| term | VARCHAR(200) | NOT NULL | Reported AE term | AETERM |
| meddra_code | VARCHAR(20) | | MedDRA code | AEDECOD |
| severity | ENUM | NOT NULL | MILD, MODERATE, SEVERE | AESEV |
| seriousness | ENUM | NOT NULL | NOT_SERIOUS, SERIOUS | AESER |
| causality | ENUM | | RELATED, NOT_RELATED, POSSIBLE | AEREL |
| outcome | ENUM | | RECOVERING, RECOVERED, NOT_RECOVERED, FATAL | AEOUT |
| onset_date | DATE | NOT NULL | Date of onset | AESTDTC |
| resolution_date | DATE | | Date of resolution | AEENDTC |
| is_sae | BOOLEAN | DEFAULT false | Serious adverse event flag | — |
| is_susar | BOOLEAN | DEFAULT false | SUSAR flag | — |
| narrative | TEXT | | Event narrative | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.7 LabResult

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| lab_result_id | UUID | PK, NOT NULL | Unique lab result identifier | LBSEQ |
| subject_id | UUID | FK → Subject, NOT NULL | Subject | USUBJID |
| visit_id | UUID | FK → Visit | Visit when collected | VISITNUM |
| test_name | VARCHAR(200) | NOT NULL | Lab test name | LBTESTCD |
| test_code | VARCHAR(20) | NOT NULL | Standardized test code | LBTESTCD |
| result_value | VARCHAR(100) | NOT NULL | Result (numeric or text) | LBORRES |
| result_unit | VARCHAR(20) | | Unit of measure | LBORRESU |
| normal_low | VARCHAR(50) | | Lower limit of normal | LBSTNRLO |
| normal_high | VARCHAR(50) | | Upper limit of normal | LBSTNRHI |
| abnormal_flag | ENUM | | NORMAL, ABNORMAL_LOW, ABNORMAL_HIGH | LBNRIND |
| specimen_type | VARCHAR(50) | | Blood, urine, etc. | LBSPEC |
| collection_date | DATE | NOT NULL | Date collected | LBDTC |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.8 Medication

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| medication_id | UUID | PK, NOT NULL | Unique medication identifier | CMSEQ |
| subject_id | UUID | FK → Subject, NOT NULL | Subject | USUBJID |
| visit_id | UUID | FK → Visit | Visit | VISITNUM |
| drug_name | VARCHAR(200) | NOT NULL | Medication name | CMTRT |
| drug_code | VARCHAR(20) | | WHO Drug code | CMDECOD |
| type | ENUM | NOT NULL | CONCOMITANT, STUDY | CMCAT |
| dose_amount | VARCHAR(50) | | Dose administered | CMDOSTXT |
| dose_unit | VARCHAR(20) | | Unit of dose | CMDOSU |
| route | VARCHAR(50) | | Route of administration | CMROUTE |
| frequency | VARCHAR(50) | | Dosing frequency | CMFREQ |
| start_date | DATE | NOT NULL | Start date | CMSTDTC |
| end_date | DATE | | End date | CMENDTC |
| indication | VARCHAR(200) | | Reason for use | CMINDC |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.9 Protocol

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| protocol_id | UUID | PK, NOT NULL | Unique protocol identifier | — |
| study_id | UUID | FK → Study, NOT NULL | Parent study | STUDYID |
| version | VARCHAR(20) | NOT NULL | Protocol version | — |
| effective_date | DATE | NOT NULL | Version effective date | — |
| status | ENUM | NOT NULL | DRAFT, APPROVED, AMENDED | — |
| summary | TEXT | | Protocol synopsis | — |
| amendments | JSONB | | List of amendments | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.10 Dose

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| dose_id | UUID | PK, NOT NULL | Unique dose identifier | EXSEQ |
| subject_id | UUID | FK → Subject, NOT NULL | Subject | USUBJID |
| visit_id | UUID | FK → Visit | Visit | VISITNUM |
| drug_name | VARCHAR(200) | NOT NULL | Study drug name | EXTRT |
| dose_amount | DECIMAL(10,2) | NOT NULL | Numeric dose | EXDOSE |
| dose_unit | VARCHAR(20) | NOT NULL | Unit | EXDOSU |
| route | VARCHAR(50) | NOT NULL | Route of administration | EXROUTE |
| datetime_administered | TIMESTAMP | NOT NULL | When dose was given | EXDTC |
| lot_number | VARCHAR(50) | | Drug lot number | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.11 Query

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| query_id | UUID | PK, NOT NULL | Unique query identifier | — |
| crf_page_id | UUID | FK → CRFPage, NOT NULL | Source CRF page | — |
| raised_by | UUID | NOT NULL | User who raised query | — |
| assigned_to | UUID | | User responsible for response | — |
| question | TEXT | NOT NULL | Query text | — |
| response | TEXT | | Response text | — |
| status | ENUM | NOT NULL | OPEN, ANSWERED, CLOSED, CANCELLED | — |
| priority | ENUM | NOT NULL | LOW, MEDIUM, HIGH, URGENT | — |
| raised_at | TIMESTAMP | NOT NULL | When query was raised | — |
| responded_at | TIMESTAMP | | When response was provided | — |
| closed_at | TIMESTAMP | | When query was closed | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.12 CRFPage

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| crf_page_id | UUID | PK, NOT NULL | Unique CRF page identifier | — |
| subject_id | UUID | FK → Subject, NOT NULL | Subject | USUBJID |
| visit_id | UUID | FK → Visit | Visit | VISITNUM |
| form_name | VARCHAR(100) | NOT NULL | CRF form name | — |
| form_version | VARCHAR(20) | NOT NULL | Form version | — |
| status | ENUM | NOT NULL | DRAFT, COMPLETE, LOCKED, QUERIED | — |
| data_json | JSONB | NOT NULL | Raw form data | — |
| source_system | VARCHAR(50) | NOT NULL | Originating EDC system | — |
| submitted_at | TIMESTAMP | | When CRF was submitted | — |
| locked_at | TIMESTAMP | | When CRF was locked | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.13 Sample

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| sample_id | UUID | PK, NOT NULL | Unique sample identifier | — |
| subject_id | UUID | FK → Subject, NOT NULL | Subject | USUBJID |
| visit_id | UUID | FK → Visit | Visit when collected | VISITNUM |
| specimen_type | VARCHAR(50) | NOT NULL | Blood, urine, tissue, etc. | — |
| collection_datetime | TIMESTAMP | NOT NULL | When collected | — |
| barcode | VARCHAR(50) | UNIQUE | Sample barcode | — |
| status | ENUM | NOT NULL | COLLECTED, SHIPPED, RECEIVED, ANALYZED | — |
| shipped_to | VARCHAR(200) | | Destination lab | — |
| notes | TEXT | | Any notes | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

### 5.14 Submission

| Attribute | Type | Constraint | Description | SDTM Mapping |
|-----------|------|------------|-------------|--------------|
| submission_id | UUID | PK, NOT NULL | Unique submission identifier | — |
| study_id | UUID | FK → Study, NOT NULL | Study being submitted | STUDYID |
| type | ENUM | NOT NULL | IND, NDA, BLA, CTA, CSR | — |
| status | ENUM | NOT NULL | DRAFT, PACKAGED, SUBMITTED, ACKNOWLEDGED | — |
| agency | VARCHAR(100) | NOT NULL | Regulatory agency (FDA, EMA, PMDA) | — |
| package_path | VARCHAR(500) | | S3 path to submission package | — |
| define_xml_path | VARCHAR(500) | | Path to Define-XML | — |
| submitted_at | TIMESTAMP | | When submitted to agency | — |
| acknowledgment_date | DATE | | Date of acknowledgment | — |
| notes | TEXT | | Submission notes | — |
| created_at | TIMESTAMP | NOT NULL | | — |
| updated_at | TIMESTAMP | NOT NULL | | — |

---

## 6. Relationship Summary

| Relationship | Type | FK Column | Description |
|-------------|------|-----------|-------------|
| Study → Site | 1:N | site.study_id | A study has multiple sites |
| Study → Subject | 1:N | subject.study_id | A study has multiple subjects |
| Study → Visit | 1:N | visit.study_id | A study defines visit schedule |
| Study → Protocol | 1:N | protocol.study_id | A study has protocol versions |
| Study → Submission | 1:N | submission.study_id | A study has submissions |
| Site → Investigator | 1:N | investigator.site_id | A site has investigators |
| Site → Subject | 1:N | subject.site_id | A site enrolls subjects |
| Subject → Visit | 1:N | visit.subject_id | A subject has visits |
| Subject → AdverseEvent | 1:N | ae.subject_id | A subject has AEs |
| Subject → LabResult | 1:N | lab.subject_id | A subject has lab results |
| Subject → Medication | 1:N | med.subject_id | A subject has medications |
| Subject → Dose | 1:N | dose.subject_id | A subject receives doses |
| Subject → CRFPage | 1:N | crf.subject_id | A subject has CRF pages |
| Subject → Sample | 1:N | sample.subject_id | A subject has samples |
| Visit → AdverseEvent | 1:N | ae.visit_id | AEs occur at visits |
| Visit → LabResult | 1:N | lab.visit_id | Labs collected at visits |
| Visit → Medication | 1:N | med.visit_id | Meds recorded at visits |
| Visit → Dose | 1:N | dose.visit_id | Doses given at visits |
| Visit → CRFPage | 1:N | crf.visit_id | CRF pages at visits |
| Visit → Sample | 1:N | sample.visit_id | Samples at visits |
| CRFPage → Query | 1:N | query.crf_page_id | A CRF page has queries |

---

## 7. CDISC Domain Mapping Summary

| Canonical Entity | SDTM Domain | Key SDTM Variables |
|-----------------|-------------|-------------------|
| Study | TS (Trial Summary) | STUDYID, TSPARM, TSVAL |
| Subject | DM (Demographics) | STUDYID, USUBJID, SUBJID, AGE, SEX, RACE, ETHNIC, COUNTRY |
| Site | DM (Sites) | SITEID, INVID, COUNTRY |
| Investigator | CO (Comments) | INVNAM, INVROLE |
| Visit | SV (Subject Visits) | VISITNUM, VISIT, VISITDTC |
| AdverseEvent | AE (Adverse Events) | AESEQ, AETERM, AEDECOD, AESEV, AESER, AEREL, AEOUT |
| LabResult | LB (Lab Results) | LBSEQ, LBTESTCD, LBORRES, LBORRESU, LBSTNRLO, LBSTNRHI |
| Medication | CM (Concomitant Meds) | CMSEQ, CMTRT, CMDECOD, CMDOSTXT, CMDOSU, CMROUTE |
| Dose | EX (Exposure) | EXSEQ, EXTRT, EXDOSE, EXDOSU, EXROUTE, EXDTC |
| Query | — (no direct SDTM domain) | — |
| CRFPage | — (no direct SDTM domain) | — |
| Sample | — (no direct SDTM domain) | — |
| Protocol | TS (Trial Summary) | — |
| Submission | — (regulatory artifact) | — |

---

## 8. Indexing Strategy

| Entity | Index | Columns | Purpose |
|--------|-------|---------|---------|
| Subject | idx_subject_study_site | study_id, site_id | Subject listing by study/site |
| AdverseEvent | idx_ae_subject | subject_id | AE lookup by subject |
| AdverseEvent | idx_ae_study_serious | study_id, is_sae | SAE listing by study |
| LabResult | idx_lab_subject_visit | subject_id, visit_id | Lab results by subject/visit |
| CRFPage | idx_crf_subject_status | subject_id, status | CRF pages by status |
| Query | idx_query_status | status | Open queries listing |
| Submission | idx_submission_study | study_id | Submissions by study |
