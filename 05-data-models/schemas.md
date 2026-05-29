# CDOS Canonical Data Model — Entity-Relationship Schema

## Overview

This document defines the canonical entity-relationship model for the Clinical Data Orchestration System (CDOS). The Pydantic models in `08-software/shared/models/` are the authoritative source of truth. This document provides the ER view aligned with those models.

---

## Entity-Relationship Diagram

```
+------------+       +-----------+       +---------+
|   Study    |1----N*|  Subject  |N*----1|  Site   |
+------------+       +-----------+       +---------+
| study_id   |       | subject_id|       | site_id |
| title      |       | study_id  |       | site_num|
| protocol # |       | site_id   |       | site_nm|
| status     |       | status    |       | country |
| phase      |       | sex       |       | status  |
+------------+       +-----------+---------+------+
      |1                  |1
      |                   |
      |N                  |N
+------------+       +-----------+       +----------+
|  Protocol  |       |   Visit   |       |  Query   |
+------------+       +-----------+       +----------+
| protocol_id|       | visit_id  |       | query_id |
| study_id   |       | study_id  |       | study_id |
| version    |       | subj_id   |       | subj_id  |
| status     |       | visit_name|       | site_id  |
| design     |       | status    |       | status   |
+------------+       +-----------+       +----------+
                         |1
              +----------+----------+
              |N          |N         |N
        +-----------+ +---------+ +-----------+
        |AdverseEv.| |LabResult| |Medication |
        +-----------+ +---------+ +-----------+
        | ae_id     | | lab_res.| | med_id    |
        | study_id  | | _id     | | study_id  |
        | subj_id   | | study_id| | subj_id   |
        | site_id   | | subj_id | | visit_id  |
        | term      | | site_id | |med_name   |
        | severity  | | result_ | | dose      |
        +-----------+ | value   | +-----------+
                      +---------+
```

---

## Entity Definitions with CDISC Mappings

### 1. Study (study)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| study_id | UUID | PK, NOT NULL | DM: STUDYID (mapped) | Unique study identifier |
| protocol_number | VARCHAR(50) | NOT NULL, UNIQUE | TS: PROTOCOL | Protocol identification number |
| title | VARCHAR(500) | NOT NULL | TS: TITLE | Full study title |
| short_title | VARCHAR(200) | NOT NULL | TS: BRIEF TITLE | Abbreviated study title |
| phase | VARCHAR(20) | NOT NULL, pattern | TS: PHASE | Study phase (I-IV, I/II, II/III, NA) |
| status | VARCHAR(30) | NOT NULL, DEFAULT 'draft' | TS: STATUS | Current study lifecycle status |
| sponsor_id | UUID | NOT NULL | TS: SPONSID | Sponsoring organization |
| indication | VARCHAR(300) | NOT NULL | TS: INDIC | Specific disease indication |
| therapeutic_area | VARCHAR(200) | | | Disease/therapeutic area |
| target_enrollment | INTEGER | NOT NULL, >=0 | | Planned number of subjects |
| actual_enrollment | INTEGER | DEFAULT 0, >=0 | | Current enrolled subject count |
| start_date | DATE | | TS: SSTDTC | Study start date |
| end_date | DATE | | TS: SENDTC | Study end date |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** DM (Demographics — STUDYID), TS (Trial Summary)
**CDISC Role:** Identifier

---

### 2. Subject (subject)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| subject_id | UUID | PK, NOT NULL | DM: USUBJID (mapped) | Unique subject identifier |
| study_id | UUID | FK→Study, NOT NULL | DM: STUDYID | Parent study |
| site_id | UUID | FK→Site, NOT NULL | DM: SITEID (mapped) | Enrollment site |
| subject_number | VARCHAR(20) | NOT NULL | DM: SUBJID | Subject number within study |
| status | VARCHAR(30) | NOT NULL, DEFAULT 'screening' | DM: ARM (derived) | Current subject status |
| screening_date | DATE | | | Date of screening visit |
| enrollment_date | DATE | | DM: RFICDTC | Date of formal enrollment |
| date_of_birth | DATE | | DM: BRTHDTC | Subject date of birth |
| sex | VARCHAR(1) | pattern (M/F/U) | DM: SEX | Biological sex |
| ethnicity | VARCHAR(100) | | DM: ETHNIC | Ethnicity |
| race | VARCHAR(100) | | DM: RACE | Race |
| consent_date | DATE | | | Date informed consent was signed |
| discontinuation_reason | VARCHAR(500) | | | Reason for discontinuation |
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

### 5. AdverseEvent (adverse_event)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| ae_id | UUID | PK, NOT NULL | AE: AEID (mapped) | Unique AE identifier |
| subject_id | UUID | FK→Subject, NOT NULL | AE: USUBJID | Parent subject |
| study_id | UUID | FK→Study, NOT NULL | AE: STUDYID | Parent study |
| site_id | UUID | FK→Site, NOT NULL | | Site where event was reported |
| term | VARCHAR(200) | NOT NULL | AE: AETERM | Reported adverse event term |
| meddra_code | VARCHAR(20) | | AE: AEDECOD | MedDRA preferred term code |
| severity | VARCHAR(20) | NOT NULL | AE: AESEV | CTCAE severity grade |
| seriousness | VARCHAR(20) | DEFAULT 'non_serious' | AE: AESER | ICH seriousness classification |
| onset_date | DATE | NOT NULL | AE: AESTDTC | Date of AE onset |
| resolution_date | DATE | | AE: AEENDTC | Date of AE resolution |
| outcome | VARCHAR(100) | | AE: AEOUT | Outcome |
| causality | VARCHAR(100) | | AE: AEREL | Causality assessment |
| is_sae | BOOLEAN | DEFAULT false | | Whether event meets SAE criteria |
| is_susar | BOOLEAN | DEFAULT false | | Whether event is a SUSAR |
| reported_to_regulator | BOOLEAN | DEFAULT false | | Whether reported to regulatory authority |
| narrative | VARCHAR(5000) | | | Event narrative |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** AE (Adverse Events)
**CDISC Role:** Event

---

### 6. LabResult (lab_result)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| lab_result_id | UUID | PK, NOT NULL | LB: LBID (mapped) | Unique lab result identifier |
| subject_id | UUID | FK→Subject, NOT NULL | LB: USUBJID | Reference to Subject |
| study_id | UUID | FK→Study, NOT NULL | LB: STUDYID | Reference to parent Study |
| site_id | UUID | FK→Site, NOT NULL | LB: SITEID | Collection site identifier |
| visit_name | VARCHAR(50) | NOT NULL | LB: VISITNUM (mapped) | Study visit when sample was collected |
| specimen_type | VARCHAR(100) | NOT NULL | LB: LBSPEC | Type of specimen |
| test_name | VARCHAR(200) | NOT NULL | LB: LBTEST | Laboratory test name |
| test_code | VARCHAR(50) | NOT NULL | LB: LBTESTCD | Laboratory test code |
| result_value | VARCHAR(100) | NOT NULL | LB: LBORRES | Result value (numeric or text) |
| unit | VARCHAR(50) | | LB: LBORRESU | Unit of measurement |
| reference_range_low | VARCHAR(50) | | LB: LBSTNRLO | Lower limit of normal range |
| reference_range_high | VARCHAR(50) | | LB: LBSTNRHI | Upper limit of normal range |
| normal_flag | VARCHAR(20) | pattern | LB: LBNRIND | Normal range flag |
| collection_date | DATE | NOT NULL | LB: LBDTC | Date specimen was collected |
| collection_time | VARCHAR(20) | | | Time specimen was collected |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | | Result verification status |
| lab_name | VARCHAR(200) | | | Performing laboratory name |
| comments | VARCHAR(1000) | | | Result comments |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**SDTM Domain:** LB (Laboratory Test Results)
**CDISC Role:** Finding

---

### 7. Query (query)

| Attribute | Type | Constraint | CDISC Mapping | Description |
|-----------|------|------------|---------------|-------------|
| query_id | UUID | PK, NOT NULL | | Unique query identifier |
| study_id | UUID | FK→Study, NOT NULL | | Reference to parent Study |
| subject_id | UUID | FK→Subject, NOT NULL | | Reference to Subject |
| site_id | UUID | FK→Site, NOT NULL | | Site associated with the query |
| crf_page | VARCHAR(100) | NOT NULL | | CRF page or form identifier |
| field_name | VARCHAR(200) | NOT NULL | | Data field triggering the query |
| query_text | VARCHAR(2000) | NOT NULL | | Query description |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'open' | | Current query status |
| priority | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | | Query priority |
| raised_by | VARCHAR(200) | NOT NULL | | Person or system that raised the query |
| assigned_to | VARCHAR(200) | | | Person assigned to resolve |
| response | VARCHAR(2000) | | | Response to the query |
| responded_by | VARCHAR(200) | | | Person who responded |
| responded_at | TIMESTAMP | | | Timestamp of response |
| auto_generated | BOOLEAN | DEFAULT false | | Whether query was auto-generated |
| created_at | TIMESTAMP | NOT NULL | | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | | Record last update time |

**Domain:** Data Management — Query/DCR
**Role:** Data Quality

---

### 8. Medication (medication)

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

### 9. Protocol (protocol)

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
| Subject | AdverseEvent | 1:N | adverse_event.subject_id | Subject's adverse events |
| Subject | LabResult | 1:N | lab_result.subject_id | Subject's lab results |
| Subject | Query | 1:N | query.subject_id | Subject's data queries |
| Subject | Medication | 1:N | medication.subject_id | Subject's medications |
| Visit | AdverseEvent | 1:N | adverse_event.visit_id | AEs reported at visit |
| Visit | LabResult | 1:N | lab_result.visit_id | Labs collected at visit |
| Visit | Medication | 1:N | medication.visit_id | Medications at visit |

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
