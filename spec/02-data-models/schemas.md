# CDOS Canonical Data Models — Entity-Relationship Schemas

This document defines the canonical entities for the CDOS platform. Each entity includes an ER table, JSON Schema reference, and CDISC SDTM/CDASH mapping.

---

## Entity-Relationship Overview

```
Study ──┬── Subject ──┬── Visit ──── AdverseEvent
        │             │              LabResult
        │             │              Medication
        ├── Site
        └── Protocol
```

| Relationship | Type | Description |
|-------------|------|-------------|
| Study → Subject | 1:N | A study enrolls many subjects |
| Study → Site | 1:N | A study has many investigation sites |
| Study → Protocol | 1:1 | A study has one protocol document |
| Subject → Visit | 1:N | A subject has many scheduled visits |
| Subject → AdverseEvent | 1:N | A subject may report many AEs |
| Subject → LabResult | 1:N | A subject has many lab results |
| Subject → Medication | 1:N | A subject may take many medications |

---

## 1. Study

**Canonical Name:** `study` | **Abbreviation:** `study` | **SDTM Domain:** DM (as STUDYID)

### ER Table

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| study_id | UUID | PK, NOT NULL | Unique study identifier |
| protocol_number | String(50) | NOT NULL, UNIQUE | Protocol number (e.g., CDOS-2024-001) |
| title | String(500) | NOT NULL | Full study title |
| phase | Enum(Phase1, Phase2, Phase3, Phase4) | NOT NULL | Clinical trial phase |
| status | Enum(PLANNING, ENROLLING, ACTIVE, COMPLETED, TERMINATED) | NOT NULL | Current study status |
| sponsor | String(200) | NOT NULL | Sponsor organization name |
| therapeutic_area | String(100) | NOT NULL | Therapeutic area (e.g., Oncology, Cardiology) |
| start_date | Date | — | Study start date |
| target_enrollment | Integer | > 0 | Planned number of subjects |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

### CDISC Mapping

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| study_id | STUDYID | DM | Identifier | — |
| protocol_number | STUDYID | DM | Identifier | — |
| title | — | — | — | — |
| phase | — | — | — | — |
| status | — | — | — | — |
| sponsor | SPONSOR | DM | Qualifier | — |
| therapeutic_area | — | — | — | — |
| start_date | — | — | — | — |
| target_enrollment | — | — | — | — |

---

## 2. Subject

**Canonical Name:** `Subject` | **Abbreviation:** `subj` | **SDTM Domain:** DM

### ER Table

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| subject_id | UUID | PK, NOT NULL | Unique subject identifier |
| study_id | UUID | FK → Study, NOT NULL | Study the subject is enrolled in |
| site_id | UUID | FK → Site, NOT NULL | Site where the subject is enrolled |
| subject_key | String(50) | NOT NULL, UNIQUE | Subject identifier (e.g., CDOS-001-001) |
| screening_date | Date | NOT NULL | Date of screening |
| enrollment_date | Date | — | Date of enrollment (NULL if screen failed) |
| status | Enum(SCREENING, ENROLLED, COMPLETED, WITHDRAWN, SCREEN_FAILED) | NOT NULL | Subject status |
| sex | Enum(MALE, FEMALE, UNKNOWN) | NOT NULL | Biological sex |
| date_of_birth | Date | NOT NULL | Date of birth |
| race | String(50) | — | Race (CDISC CT) |
| ethnicity | String(50) | — | Ethnicity (CDISC CT) |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

### CDISC Mapping

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| subject_id | USUBJID | DM | Identifier | — |
| study_id | STUDYID | DM | Identifier | — |
| site_id | SITEID | DM | Identifier | — |
| subject_key | SUBJID | DM | Identifier | — |
| screening_date | RFSTDTC | DM | Timing | — |
| enrollment_date | RFENRLDTC | DM | Timing | — |
| status | ACTARM | DM | Record Qualifier | — |
| sex | SEX | DM | Record Qualifier | CDISC CT: SEX |
| date_of_birth | BRTHDTC | DM | Record Qualifier | — |
| race | RACE | DM | Record Qualifier | CDISC CT: RACE |
| ethnicity | ETHNIC | DM | Record Qualifier | CDISC CT: ETHNIC |

---

## 3. Site

**Canonical Name:** `Site` | **Abbreviation:** `site` | **SDTM Domain:** DM (as SITEID)

### ER Table

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| site_id | UUID | PK, NOT NULL | Unique site identifier |
| study_id | UUID | FK → Study, NOT NULL | Study this site belongs to |
| site_number | String(20) | NOT NULL, UNIQUE | Site identifier (e.g., 001, 002) |
| name | String(200) | NOT NULL | Institution name |
| address | String(500) | NOT NULL | Physical address |
| country | String(3) | NOT NULL | ISO 3166-1 alpha-3 country code |
| region | String(100) | — | Geographic region |
| status | Enum(PENDING, ACTIVE, CLOSED) | NOT NULL | Site activation status |
| pi_name | String(200) | NOT NULL | Principal investigator name |
| pi_email | String(200) | — | Principal investigator email |
| target_enrollment | Integer | > 0 | Planned enrollment for this site |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

### CDISC Mapping

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| site_id | SITEID | DM | Identifier | — |
| study_id | STUDYID | DM | Identifier | — |
| site_number | SITEID | DM | Identifier | — |
| name | — | — | — | — |
| address | — | — | — | — |
| country | COUNTRY | DM | Record Qualifier | ISO 3166-1 |
| region | — | — | — | — |
| status | — | — | — | — |
| pi_name | INVID | DM | Identifier | — |

---

## 4. Visit

**Canonical Name:** `Visit` | **Abbreviation:** `visit` | **SDTM Domain:** SV

### ER Table

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| visit_id | UUID | PK, NOT NULL | Unique visit identifier |
| subject_id | UUID | FK → Subject, NOT NULL | Subject this visit is for |
| study_id | UUID | FK → Study, NOT NULL | Study context |
| visit_name | String(50) | NOT NULL | Visit label (e.g., V1, V2, Week 4) |
| visit_number | Integer | NOT NULL | Sequential visit number |
| scheduled_date | Date | NOT NULL | Scheduled visit date |
| actual_date | Date | — | Actual visit date (NULL if not yet occurred) |
| status | Enum(SCHEDULED, COMPLETED, MISSED, CANCELLED) | NOT NULL | Visit status |
| visit_type | Enum(SCREENING, BASELINE, TREATMENT, FOLLOW_UP, END_OF_STUDY) | NOT NULL | Type of visit |
| window_start | Date | — | Earliest acceptable visit date |
| window_end | Date | — | Latest acceptable visit date |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

### CDISC Mapping

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| visit_id | VISITNUM | SV | Identifier | — |
| subject_id | USUBJID | SV | Identifier | — |
| study_id | STUDYID | SV | Identifier | — |
| visit_name | VISIT | SV | Record Qualifier | — |
| visit_number | VISITNUM | SV | Record Qualifier | — |
| scheduled_date | SVSTDTC | SV | Timing | — |
| actual_date | SVENDTC | SV | Timing | — |
| status | SVSTATUS | SV | Record Qualifier | — |
| visit_type | VISIT | SV | Record Qualifier | CDISC CT: VISIT |

---

## 5. AdverseEvent

**Canonical Name:** `AdverseEvent` | **Abbreviation:** `ae` | **SDTM Domain:** AE

### ER Table

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| ae_id | UUID | PK, NOT NULL | Unique adverse event identifier |
| subject_id | UUID | FK → Subject, NOT NULL | Subject who experienced the AE |
| study_id | UUID | FK → Study, NOT NULL | Study context |
| term | String(200) | NOT NULL | Reported AE term |
| meddra_code | String(20) | FK → MedDRA | Coded MedDRA PT code |
| meddra_llt | String(200) | — | MedDRA Lowest Level Term |
| severity | Enum(MILD, MODERATE, SEVERE) | NOT NULL | CTCAE grade |
| serious | Boolean | NOT NULL, DEFAULT false | Whether the AE is serious (SAE) |
| serious_criteria | Set(DEATH, LIFE_THREATENING, HOSPITALIZATION, DISABILITY, CONGENITAL_ANOMALY, IMPORTANT_MEDICAL_EVENT) | — | Seriousness criteria (required if serious=true) |
| causality | Enum(RELATED, NOT_RELATED, POSSIBLY_RELATED) | NOT NULL | Relatedness to study drug |
| outcome | Enum(RECOVERED, RECOVERING, NOT_RECOVERED, FATAL, UNKNOWN) | NOT NULL | AE outcome |
| onset_date | Date | NOT NULL | Date of AE onset |
| resolution_date | Date | — | Date of AE resolution (NULL if ongoing) |
| description | String(2000) | — | Narrative description |
| reported_by | String(100) | NOT NULL | Who reported the AE |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

### CDISC Mapping

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| ae_id | AESEQ | AE | Identifier | — |
| subject_id | USUBJID | AE | Identifier | — |
| study_id | STUDYID | AE | Identifier | — |
| term | AETERM | AE | Topic | — |
| meddra_code | AEPTCD | AE | Qualifier | MedDRA PT |
| meddra_llt | AELLTCD | AE | Qualifier | MedDRA LLT |
| severity | AESEV | AE | Qualifier | CDISC CT: SEVERITY |
| serious | AESER | AE | Qualifier | CDISC CT: NY |
| serious_criteria | AESCAN | AE | Qualifier | CDISC CT: AESCAN |
| causality | AEREL | AE | Qualifier | CDISC CT: RELATIONSHIP |
| outcome | AEOUT | AE | Qualifier | CDISC CT: OUTCOME |
| onset_date | AESTDTC | AE | Timing | — |
| resolution_date | AEENDTC | AE | Timing | — |
| description | AEDSC | AE | Synonym Qualifier | — |

---

## 6. LabResult

**Canonical Name:** `LabResult` | **Abbreviation:** `lab` | **SDTM Domain:** LB

### ER Table

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| lab_id | UUID | PK, NOT NULL | Unique lab result identifier |
| subject_id | UUID | FK → Subject, NOT NULL | Subject this result belongs to |
| visit_id | UUID | FK → Visit, NOT NULL | Visit at which sample was collected |
| study_id | UUID | FK → Study, NOT NULL | Study context |
| test_name | String(100) | NOT NULL | Name of the lab test |
| test_code | String(20) | NOT NULL | Lab test code |
| category | Enum(CHEMISTRY, HEMATOLOGY, URINALYSIS, IMMUNOLOGY, OTHER) | NOT NULL | Lab category |
| result_value | Float | — | Numeric result value |
| result_text | String(100) | — | Text result (for non-numeric) |
| unit | String(20) | NOT NULL | Unit of measurement |
| reference_range_low | Float | — | Lower limit of normal range |
| reference_range_high | Float | — | Upper limit of normal range |
| abnormal_flag | Enum(NORMAL, LOW, HIGH, ABNORMAL) | — | Normal/abnormal indicator |
| collection_date | DateTime | NOT NULL | Date/time of sample collection |
| specimen_type | String(50) | NOT NULL | Type of specimen (blood, urine, etc.) |
| lab_name | String(200) | — | Performing laboratory name |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

### CDISC Mapping

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| lab_id | LBSEQ | LB | Identifier | — |
| subject_id | USUBJID | LB | Identifier | — |
| visit_id | VISITNUM | LB | Identifier | — |
| study_id | STUDYID | LB | Identifier | — |
| test_name | LBTEST | LB | Topic | — |
| test_code | LBTESTCD | LB | Topic | — |
| category | LBCAT | LB | Grouping Qualifier | — |
| result_value | LBSTRESN | LB | Result Qualifier | — |
| result_text | LBSTRESC | LB | Result Qualifier | — |
| unit | LBSTRESU | LB | Variable Qualifier | CDISC CT: UNIT |
| reference_range_low | LBSTNRLO | LB | Variable Qualifier | — |
| reference_range_high | LBSTNRHI | LB | Variable Qualifier | — |
| abnormal_flag | LBNRIND | LB | Variable Qualifier | CDISC CT: LBNRIND |
| collection_date | LBDTC | LB | Timing | — |
| specimen_type | LBSPEC | LB | Specimen Qualifier | CDISC CT: SPECIMEN |
| lab_name | LBLOC | LB | Record Qualifier | — |

---

## 7. Medication

**Canonical Name:** `Medication` | **Abbreviation:** `med` | **SDTM Domain:** CM

### ER Table

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| medication_id | UUID | PK, NOT NULL | Unique medication identifier |
| subject_id | UUID | FK → Subject, NOT NULL | Subject taking the medication |
| study_id | UUID | FK → Study, NOT NULL | Study context |
| drug_name | String(200) | NOT NULL | Name of the medication |
| generic_name | String(200) | — | Generic/INN name |
| who_drug_code | String(20) | FK → WHO Drug | WHO Drug ATC code |
| category | Enum(CONCOMITANT, STUDY_MEDICATION, PRIOR_MEDICATION) | NOT NULL | Medication category |
| dose | String(50) | — | Dose amount and unit |
| frequency | String(50) | — | Dosing frequency |
| route | Enum(ORAL, IV, IM, SC, TOPICAL, INHALED, OTHER) | — | Route of administration |
| indication | String(200) | — | Reason for taking the medication |
| start_date | Date | NOT NULL | Medication start date |
| end_date | Date | — | Medication end date (NULL if ongoing) |
| ongoing | Boolean | NOT NULL, DEFAULT true | Whether medication is ongoing |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

### CDISC Mapping

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| medication_id | CMSEQ | CM | Identifier | — |
| subject_id | USUBJID | CM | Identifier | — |
| study_id | STUDYID | CM | Identifier | — |
| drug_name | CMTRT | CM | Topic | — |
| generic_name | CMMODIFY | CM | Synonym Qualifier | — |
| who_drug_code | CMDECOD | CM | Qualifier | WHO Drug ATC |
| category | CMCAT | CM | Grouping Qualifier | CDISC CT: CMCAT |
| dose | CMDOSTXT | CM | Record Qualifier | — |
| frequency | CMDOSFRQ | CM | Record Qualifier | CDISC CT: DOSFRQ |
| route | CMROUTE | CM | Record Qualifier | CDISC CT: ROUTE |
| indication | CMINDC | CM | Record Qualifier | — |
| start_date | CMSTDTC | CM | Timing | — |
| end_date | CMENDTC | CM | Timing | — |
| ongoing | — | — | — | — |

---

## 8. Protocol

**Canonical Name:** `Protocol` | **Abbreviation:** `proto` | **SDTM Domain:** — (metadata entity)

### ER Table

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| protocol_id | UUID | PK, NOT NULL | Unique protocol identifier |
| study_id | UUID | FK → Study, NOT NULL, UNIQUE | Study this protocol belongs to |
| protocol_number | String(50) | NOT NULL | Protocol number |
| version | String(20) | NOT NULL | Protocol version |
| amendment_number | Integer | DEFAULT 0 | Amendment sequence number |
| title | String(500) | NOT NULL | Protocol title |
| status | Enum(DRAFT, APPROVED, AMENDED, SUPERSEDED) | NOT NULL | Protocol status |
| effective_date | Date | NOT NULL | Date protocol became effective |
| summary | String(2000) | — | Protocol summary |
| inclusion_criteria | Array[String] | NOT NULL | List of inclusion criteria |
| exclusion_criteria | Array[String] | NOT NULL | List of exclusion criteria |
| primary_endpoints | Array[String] | NOT NULL | Primary study endpoints |
| secondary_endpoints | Array[String] | — | Secondary study endpoints |
| file_url | String(500) | — | Link to full protocol document |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

### CDISC Mapping

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| protocol_id | — | — | — | — |
| study_id | STUDYID | DM | Identifier | — |
| protocol_number | PROTOCOL | DM | Record Qualifier | — |
| version | — | — | — | — |
| amendment_number | — | — | — | — |
| title | — | — | — | — |
| status | — | — | — | — |
| effective_date | — | — | — | — |
| inclusion_criteria | — | — | — | — |
| exclusion_criteria | — | — | — | — |
| primary_endpoints | — | — | — | — |
| secondary_endpoints | — | — | — | — |

---

## Cross-Reference Summary

| Entity | FK References | Referenced By |
|--------|--------------|---------------|
| Study | — | Subject, Site, Visit, AdverseEvent, LabResult, Medication, Protocol |
| Subject | Study, Site | Visit, AdverseEvent, LabResult, Medication |
| Site | Study | Subject |
| Visit | Subject, Study | LabResult |
| AdverseEvent | Subject, Study | — |
| LabResult | Subject, Visit, Study | — |
| Medication | Subject, Study | — |
| Protocol | Study | — |
