# Transform: EDC CRF Data → CDOS Canonical / SDTM

## Overview

- Source: EDC (locked CRF pages with CDASH-aligned fields)
- Target: CDOS Canonical entities → SDTM domains (DM, AE, EX, CM)
- Trigger: CRF page lock event
- Frequency: Real-time (event-driven on page lock)

---

## Field Mapping

### Subject → DM Domain

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| edc.USUBJID | Subject.subject_id | string → UUID | generate deterministic UUID |
| edc.SUBJID | Subject.subject_number | none | direct copy |
| edc.SITEID | Subject.site_id | none | direct copy |
| edc.SEX | Subject.sex | string → Enum | map to CDISC CT SEX codelist |
| edc.RACE | Subject.race | string → Enum | map to CDISC CT RACE codelist |
| edc.ETHNIC | Subject.ethnicity | string → Enum | map to CDISC CT ETHNIC codelist |
| edc.BRTHDTc | Subject.birth_date | string → Date | ISO 8601 parse |
| edc.AGE | Subject.age | int | direct copy |
| edc.SITEID | DM.SITEID | none | direct copy |
| Subject.* | DM.USUBJID | complex | SHARED-001 |
| Subject.sex | DM.SEX | Enum → string | CDISC CT code |
| Subject.race | DM.RACE | Enum → string | CDISC CT code |

### AdverseEvent → AE Domain

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| edc.AETERM | AdverseEvent.term | none | direct copy |
| edc.AESEV | AdverseEvent.severity | string → Enum(MILD, MODERATE, SEVERE) | map to CTCAE grade |
| edc.AESTDTC | AdverseEvent.onset_date | string → Date | SHARED-003 |
| edc.AEENDTC | AdverseEvent.resolution_date | string → Date | SHARED-003 |
| edc.AESER | AdverseEvent.serious | string → boolean | "Y"→true, "N"→false |
| edc.AEREL | AdverseEvent.causality | string → Enum | map to REL codelist |
| edc.AEACN | AdverseEvent.action_taken | string → Enum | map to ACN codelist |
| AdverseEvent.term | AE.AETERM | none | direct copy |
| AdverseEvent.severity | AE.AESEV | Enum → string | CDISC CT code |
| AdverseEvent.onset_date | AE.AESTDTC | Date → string | ISO 8601 |
| AdverseEvent.serious | AE.AESER | boolean → string | "Y"/"N" |

### Dose → EX Domain

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| edc.EXTRT | Dose.treatment | none | direct copy |
| edc.EXDOSE | Dose.dose_amount | string → decimal | parse numeric |
| edc.EXDOSU | Dose.dose_unit | string → Enum | map to CDISC CT UNIT codelist |
| edc.EXSTDTC | Dose.start_date | string → Date | SHARED-003 |
| edc.EXENDTC | Dose.end_date | string → Date | SHARED-003 |
| edc.EXROUTE | Dose.route | string → Enum | map to ROUTE codelist |

### Medication → CM Domain

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| edc.CMTRT | Medication.term | none | direct copy |
| edc.CMDOSE | Medication.dose | string → decimal | parse numeric |
| edc.CMDOSU | Medication.dose_unit | string → Enum | map to UNIT codelist |
| edc.CMSTDTC | Medication.start_date | string → Date | SHARED-003 |
| edc.CMENDTC | Medication.end_date | string → Date | SHARED-003 |
| edc.CMINDC | Medication.indication | none | direct copy |
| edc.CMROUTE | Medication.route | string → Enum | map to ROUTE codelist |

---

## Business Rules

```
RULE-001: FOR EACH locked_crf_page IN edc:
          VALIDATE page against CDASH conformance
          IF non_conformant THEN QUARANTINE

RULE-002: IF AdverseEvent.serious = true AND AdverseEvent.severity = "SEVERE"
          THEN TRIGGER event("ae.reported", ae)
          AND NOTIFY [System:Safety]

RULE-003: IF AdverseEvent.onset_date > AdverseEvent.resolution_date
          THEN REJECT with error "onset_after_resolution"

RULE-004: IF AdverseEvent.resolution_date IS NOT NULL
          THEN AdverseEvent.status = "RESOLVED"
          ELSE AdverseEvent.status = "ONGOING"

RULE-005: Subject.study_day for first dose =
          SHARED-002(Dose.start_date, Study.start_date)

RULE-006: FOR EACH CRF page:
          STAMP_AUDIT(record, "T02", system_user)  // SHARED-009
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-001 | USUBJID NOT NULL | REJECT |
| VAL-002 | AE term NOT NULL | REJECT |
| VAL-003 | onset_date <= TODAY | QUARANTINE |
| VAL-004 | severity IN (MILD, MODERATE, SEVERE) | QUARANTINE |
| VAL-005 | visit IN defined_visits | REJECT |
| VAL-006 | sex IN CDISC CT SEX codelist | QUARANTINE |
| VAL-007 | race IN CDISC CT RACE codelist | QUARANTINE |
| VAL-008 | dose_amount > 0 when not NULL | QUARANTINE |

---

## Error Handling

- Missing USUBJID → REJECT, log to `dlq.edc-to-sdtm`
- Invalid CDISC CT value → QUARANTINE, flag for coding review
- Duplicate record (SHARED-006) → MERGE (last-write-wins)
- CRF page integrity failure → REJECT, alert data manager
