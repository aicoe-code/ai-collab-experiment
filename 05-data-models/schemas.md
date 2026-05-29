# CDOS Canonical Data Model — Entity-Relationship Schema

## Overview

This document defines the canonical entity-relationship model for the Clinical Data Orchestration System (CDOS). All entities, attributes, and relationships are defined here with their corresponding CDISC mappings. JSON Schema definitions in `canonical/` are the authoritative source; this document provides the ER view.

---

## Entity-Relationship Diagram

```
+------------+       +-----------+       +---------+
|   Study    |1----N*|  Subject  |N*----1|  Site   |
+------------+       +-----------+       +---------+
| study_id   |       | subject_id|       | site_id |
| study_name |       | study_id  |       | site_num|
| protocol # |       | site_id   |       | site_nm|
| status     |       | status    |       | country |
| phase      |       | sex       |       | status  |
+------------+       +-----------+       +---------+
      |1                  |1                  |1
      |                   |                   |
      |N                  |N                  |
+------------+       +-----------+       +----------+
|  Protocol  |       |   Visit   |       |Inves-    |
+------------+       +-----------+       |tigator   |
| protocol_id|       | visit_id  |       +----------+
| study_id   |       | study_id  |       |inv_id    |
| version    |       | subj_id   |       |site_id   |
| status     |       | visit_name|       |name      |
| design     |       | status    |       |role      |
+------------+       +-----------+       +----------+
                         |1
              +----------+----------+
              |N          |N         |N
        +-----------+ +---------+ +-----------+
        |AdverseEv.| |LabResult| |Medication |
        +-----------+ +---------+ +-----------+
        | ae_id     | | lab_id  | | med_id    |
        | study_id  | | study_id| | study_id  |
        | subj_id   | | subj_id | | subj_id   |
        | visit_id  | | visit_id| | visit_id  |
        | term      | |test_name| |med_name   |
        | severity  | | result  | | dose      |
        +-----------+ +---------+ +-----------+
```

---

## Entity Definitions with CDISC Mappings

### 1. Study (study)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| study_id | UUID | PK, NOT NULL | DM: STUDYID (mapped) | Unique study identifier |
| study_name | VARCHAR(200) | NOT NULL | TS: TITLE | Official study name |
| protocol_number | VARCHAR(50) | NOT NULL, UNIQUE | TS: PROTOCOL | Protocol identification number |
| short_title | VARCHAR(100) | | TS: BRIEF TITLE | Brief study title |
| phase | VARCHAR(20) | NOT NULL | TS: PHASE | Study phase (I-IV) |
| status | VARCHAR(30) | NOT NULL | TS: STATUS | Current study status |
| sponsor_id | UUID | | TS: SPONSID | Sponsoring organization |
| therapeutic_area | VARCHAR(100) | | | Disease/therapeutic area |
| indication | VARCHAR(200) | | TS: INDIC | Specific disease indication |
| study_start_date | DATE | | TS: SSTDTC | First subject first visit |
| study_end_date | DATE | | TS: SENDTC | Planned/actual completion |
| protocol_version | VARCHAR(20) | | | Current protocol version |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** DM (Demographics — STUDYID), TS (Trial Summary)
**CDISC Role:** Identifier

---

### 2. Subject (subj)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| subject_id | UUID | PK, NOT NULL | DM: USUBJID (mapped) | Unique subject identifier |
| study_id | UUID | FK→Study, NOT NULL | DM: STUDYID | Parent study |
| site_id | UUID | FK→Site, NOT NULL | DM: SITEID (mapped) | Enrollment site |
| subject_number | VARCHAR(20) | | DM: SUBJID | Site-specific subject number |
| screening_number | VARCHAR(20) | | | Screening ID |
| status | VARCHAR(30) | NOT NULL | DM: ARM (derived) | Enrollment status |
| enrollment_date | DATE | | DM: RFICDTC | Informed consent date |
| date_of_birth | DATE | | DM: BRTHDTC | Date of birth |
| sex | VARCHAR(1) | | DM: SEX | Biological sex (M/F/U) |
| race | VARCHAR(100) | | DM: RACE | Race |
| ethnicity | VARCHAR(100) | | DM: ETHNIC | Ethnicity |
| treatment_arm | VARCHAR(50) | | DM: ARMCD | Assigned treatment arm |
| randomization_date | DATE | | | Date of randomization |
| withdrawal_date | DATE | | | Date of withdrawal |
| withdrawal_reason | VARCHAR(200) | | | Withdrawal reason |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** DM (Demographics)
**CDISC Role:** Identifier / Record Qualifier

---

### 3. Site (site)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| site_id | UUID | PK, NOT NULL | DM: SITEID (mapped) | Unique site identifier |
| site_number | VARCHAR(20) | NOT NULL, UNIQUE | DM: SITEID | Site number |
| site_name | VARCHAR(200) | NOT NULL | | Institution name |
| investigator_id | UUID | FK→Investigator | DM: INVNAME (mapped) | Principal investigator |
| address_line1 | VARCHAR(200) | | | Street address |
| address_line2 | VARCHAR(200) | | | Additional address |
| city | VARCHAR(100) | | | City |
| state_province | VARCHAR(100) | | | State/Province |
| postal_code | VARCHAR(20) | | | Postal code |
| country | VARCHAR(3) | NOT NULL | DM: COUNTRY | ISO country code |
| phone | VARCHAR(30) | | | Contact phone |
| email | VARCHAR(255) | | | Contact email |
| status | VARCHAR(20) | NOT NULL | | Activation status |
| activation_date | DATE | | | Site activation date |
| irb_approval_date | DATE | | | IRB/IEC approval date |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** DM (Demographics — SITEID, COUNTRY)
**CDISC Role:** Identifier

---

### 4. Visit (visit)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| visit_id | UUID | PK, NOT NULL | SV: VISITID (mapped) | Unique visit identifier |
| study_id | UUID | FK→Study, NOT NULL | SV: STUDYID | Parent study |
| subject_id | UUID | FK→Subject, NOT NULL | SV: USUBJID | Parent subject |
| site_id | UUID | FK→Site | SV: SITEID | Site of visit |
| visit_name | VARCHAR(50) | NOT NULL | SV: VISIT | Protocol-defined visit name |
| visit_number | INTEGER | NOT NULL, ≥1 | SV: VISITNUM | Sequential visit number |
| visit_scheduled_date | DATE | | | Scheduled date |
| visit_actual_date | DATE | | SV: SVSTDTC | Actual visit date |
| visit_window_start | DATE | | | Window start |
| visit_window_end | DATE | | | Window end |
| status | VARCHAR(20) | NOT NULL | SV: SVSTAT | Visit status |
| visit_type | VARCHAR(20) | | | Visit category |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** SV (Subject Visits)
**CDISC Role:** Timing

---

### 5. AdverseEvent (ae)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| ae_id | UUID | PK, NOT NULL | AE: AEID (mapped) | Unique AE identifier |
| study_id | UUID | FK→Study, NOT NULL | AE: STUDYID | Parent study |
| subject_id | UUID | FK→Subject, NOT NULL | AE: USUBJID | Parent subject |
| visit_id | UUID | FK→Visit | | Associated visit |
| ae_sequence | INTEGER | ≥1 | AE: AESEQ | Sequence number per subject |
| term | VARCHAR(200) | NOT NULL | AE: AETERM | Verbatim AE term |
| meddra_code | VARCHAR(20) | | AE: AEDECOD | MedDRA code |
| meddra_llt | VARCHAR(100) | | | MedDRA LLT |
| meddra_pt | VARCHAR(100) | | AE: AEDECOD | MedDRA Preferred Term |
| meddra_soc | VARCHAR(100) | | AE: AEBODSYS | MedDRA SOC |
| severity | VARCHAR(20) | NOT NULL | AE: AESEV | Severity grade |
| seriousness | VARCHAR(20) | | AE: AESER | SAE indicator |
| causality | VARCHAR(30) | | AE: AEREL | Relationship to study drug |
| outcome | VARCHAR(20) | | AE: AEOUT | AE outcome |
| action_taken | VARCHAR(30) | | AE: AEACN | Action taken with study drug |
| start_date | DATE | NOT NULL | AE: AESTDTC | Onset date |
| end_date | DATE | | AE: AEENDTC | Resolution date |
| is_ongoing | BOOLEAN | | | Ongoing indicator |
| reported_by | VARCHAR(100) | | | Reporter |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** AE (Adverse Events)
**CDISC Role:** Event

---

### 6. LabResult (lab)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| lab_id | UUID | PK, NOT NULL | LB: LBID (mapped) | Unique lab result identifier |
| study_id | UUID | FK→Study, NOT NULL | LB: STUDYID | Parent study |
| subject_id | UUID | FK→Subject, NOT NULL | LB: USUBJID | Parent subject |
| visit_id | UUID | FK→Visit, NOT NULL | LB: VISITNUM (mapped) | Visit |
| lab_sequence | INTEGER | ≥1 | LB: LBSEQ | Sequence number |
| test_name | VARCHAR(100) | NOT NULL | LB: LBTEST | Test name |
| test_code | VARCHAR(20) | NOT NULL | LB: LBTESTCD | Test code |
| category | VARCHAR(20) | | LB: LBCAT | Test category |
| result | VARCHAR(200) | NOT NULL | LB: LBORRES | Result value |
| result_numeric | DECIMAL | | LB: LBSTRESN | Standardized numeric result |
| unit | VARCHAR(20) | | LB: LBORRESU | Unit of measurement |
| reference_range_low | DECIMAL | | LB: LBSTNRLO | Normal range lower limit |
| reference_range_high | DECIMAL | | LB: LBSTNRHI | Normal range upper limit |
| normal_flag | VARCHAR(20) | | LB: LBNRIND | Normal/abnormal flag |
| specimen_type | VARCHAR(50) | | LB: LBSPEC | Specimen type |
| collection_date | DATE | | LB: LBDTC | Collection date |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** LB (Laboratory Test Results)
**CDISC Role:** Finding

---

### 7. Medication (med)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| med_id | UUID | PK, NOT NULL | CM: CMID (mapped) | Unique medication ID |
| study_id | UUID | FK→Study, NOT NULL | CM: STUDYID | Parent study |
| subject_id | UUID | FK→Subject, NOT NULL | CM: USUBJID | Parent subject |
| visit_id | UUID | FK→Visit | | Associated visit |
| med_sequence | INTEGER | ≥1 | CM: CMSEQ | Sequence number |
| medication_name | VARCHAR(200) | NOT NULL | CM: CMTRT | Medication name |
| who_drug_code | VARCHAR(20) | | WHO Drug Dictionary | WHO drug code |
| medication_type | VARCHAR(20) | | | Concomitant/Study/Prior |
| dose | VARCHAR(50) | | CM: CMDOSTXT | Dose amount |
| dose_unit | VARCHAR(20) | | CM: CMDOSU | Dose unit |
| route | VARCHAR(50) | | CM: CMROUTE | Route of administration |
| frequency | VARCHAR(50) | | CM: CMFREQ | Dosing frequency |
| indication | VARCHAR(200) | | CM: CMINDC | Reason for medication |
| start_date | DATE | NOT NULL | CM: CMSTDTC | Start date |
| end_date | DATE | | CM: CMENDTC | End date |
| is_ongoing | BOOLEAN | | | Ongoing indicator |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** CM (Concomitant Medications) / EX (Exposure)
**CDISC Role:** Intervention

---

### 8. Protocol (proto)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| protocol_id | UUID | PK, NOT NULL | | Unique protocol version ID |
| study_id | UUID | FK→Study, NOT NULL | TS: STUDYID | Parent study |
| version | VARCHAR(20) | NOT NULL | | Protocol version |
| effective_date | DATE | | | Effective date |
| status | VARCHAR(20) | NOT NULL | | Version status |
| title | VARCHAR(500) | | TS: TITLE | Full protocol title |
| objective_primary | TEXT | | TS: OBJPRIN | Primary objective |
| objective_secondary | TEXT[] | | TS: OBJSEC | Secondary objectives |
| study_design | VARCHAR(30) | | TS: STUDYDES | Study design type |
| is_blinded | BOOLEAN | | TS: BINDSC | Blinding indicator |
| blinding_procedure | VARCHAR(200) | | | Blinding description |
| number_of_arms | INTEGER | ≥1 | TS: ARMSN | Number of arms |
| inclusion_criteria | TEXT[] | | TI: IETEST (incl) | Inclusion criteria |
| exclusion_criteria | TEXT[] | | TI: IETEST (excl) | Exclusion criteria |
| endpoints_primary | TEXT[] | | | Primary endpoints |
| endpoints_secondary | TEXT[] | | | Secondary endpoints |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** TS (Trial Summary), TI (Trial Inclusion/Exclusion)
**CDISC Role:** Trial Design

---

## Relationships Summary

| From | To | Cardinality | FK Column | Description |
|------|----|------------|-----------|-------------|
| Study | Subject | 1:N | subject.study_id | Subjects enrolled in study |
| Study | Site | M:N | (study_site junction) | Sites participating in study |
| Study | Protocol | 1:N | protocol.study_id | Protocol versions for study |
| Site | Subject | 1:N | subject.site_id | Subjects at a site |
| Subject | Visit | 1:N | visit.subject_id | Subject's scheduled visits |
| Subject | AdverseEvent | 1:N | ae.subject_id | Subject's adverse events |
| Subject | LabResult | 1:N | lab.subject_id | Subject's lab results |
| Subject | Medication | 1:N | med.subject_id | Subject's medications |
| Visit | AdverseEvent | 1:N | ae.visit_id | AEs reported at visit |
| Visit | LabResult | 1:N | lab.visit_id | Labs collected at visit |
| Visit | Medication | 1:N | med.visit_id | Medications at visit |

---

## CDISC Standards Reference

| Standard | Version | Usage |
|----------|---------|-------|
| SDTM v3.4 | Study Data Tabulation Model | Domain mapping (DM, AE, LB, CM, SV, TS, TI) |
| ADaM v2.1 | Analysis Data Model | Analysis dataset derivation |
| ODM v2.0 | Operational Data Model | Metadata exchange |
| CDASH v2.1 | Clinical Data Acquisition Standards | CRF field mapping |
| Define-XML v2.1 | Metadata specification | Dataset definitions |

---

## Controlled Terminology Sources

| Source | Version | Application |
|--------|---------|-------------|
| MedDRA | Latest | Adverse event coding (AE domain) |
| WHO Drug Dictionary | Latest | Medication coding (CM domain) |
| CDISC CT | Latest | SDTM variables (SEX, RACE, AESEV, etc.) |
| ISO 3166-1 | Latest | Country codes (DM: COUNTRY) |
| UCUM | Latest | Units of measurement (LB: LBORRESU) |
