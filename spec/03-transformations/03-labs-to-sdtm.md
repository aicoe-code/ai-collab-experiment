# Transform: LIMS Lab Data → SDTM LB Domain

## Overview

- Source: LIMS (laboratory test results with reference ranges)
- Target: SDTM LB domain (LabResult entity)
- Trigger: Lab data import / batch upload from central lab
- Frequency: Batch (daily or per lab data transfer)

---

## Field Mapping

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| lims.USUBJID | LabResult.subject_id | string → UUID | SHARED-001 |
| lims.LBTESTCD | LabResult.test_code | none | direct copy (CDISC LBTESTCD) |
| lims.LBTEST | LabResult.test_name | none | direct copy |
| lims.LBORRES | LabResult.result_original | none | direct copy |
| lims.LBORRESU | LabResult.result_unit_original | none | direct copy |
| lims.LBSTRESN | LabResult.result_std_numeric | string → decimal | parse numeric |
| lims.LBSTRESC | LabResult.result_std_character | none | direct copy |
| lims.LBSTRESU | LabResult.result_unit_std | none | map to CDISC CT UNIT |
| lims.LBNRIND | LabResult.normal_flag | string → Enum | NORMAL/ABNORMAL/HIGH/LOW |
| lims.LBREFID | LabResult.lab_ref_id | none | direct copy |
| lims.LBDTC | LabResult.collection_date | string → Date | SHARED-003 |
| lims.LBFAST | LabResult.fasting | string → boolean | "Y"→true |
| lims.VISIT | LabResult.visit_name | none | direct copy |
| LabResult.* | LB.USUBJID | complex | SHARED-001 |
| LabResult.test_code | LB.LBTESTCD | none | direct copy |
| LabResult.result_std_numeric | LB.LBSTRESN | decimal → string | format per CDISC |
| LabResult.normal_flag | LB.LBNRIND | Enum → string | CDISC CT code |
| LabResult.collection_date | LB.LBDTC | Date → string | ISO 8601 |

---

## Business Rules

```
RULE-001: IF lims.LBORRES IS NUMERIC AND lims.LBORRESU IS NOT NULL
          THEN LabResult.result_std_numeric = convert_to_standard_unit(
                 lims.LBORRES, lims.LBORRESU, standard_unit_for_test(lims.LBTESTCD))
          ELSE LabResult.result_std_numeric = NULL

RULE-002: IF LabResult.result_std_numeric > LabResult.ref_range_high
          THEN LabResult.normal_flag = "HIGH"
          ELSE IF LabResult.result_std_numeric < LabResult.ref_range_low
          THEN LabResult.normal_flag = "LOW"
          ELSE LabResult.normal_flag = "NORMAL"

RULE-003: IF lims.LBSTRESN IS NOT NULL AND lims.LBSTRESN IS NOT NUMERIC
          THEN LabResult.result_std_character = lims.LBSTRESN
          AND LabResult.result_std_numeric = NULL

RULE-004: study_day = SHARED-002(LabResult.collection_date, Study.start_date)
          LabResult.study_day = study_day

RULE-005: STAMP_AUDIT(record, "T03", system_user)  // SHARED-009

RULE-006: IF LabResult.test_code IN panel_list("CHEMISTRY")
          THEN LabResult.category = "CHEMISTRY"
          ELSE IF LabResult.test_code IN panel_list("HEMATOLOGY")
          THEN LabResult.category = "HEMATOLOGY"
          ELSE LabResult.category = "OTHER"
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-001 | USUBJID NOT NULL | REJECT |
| VAL-002 | LBTESTCD IN CDISC LBTESTCD codelist | QUARANTINE |
| VAL-003 | LBDTC IS valid date | REJECT |
| VAL-004 | LBSTRESN IS numeric OR NULL | QUARANTINE |
| VAL-005 | LBORRESU IS valid unit | QUARANTINE |
| VAL-006 | collection_date <= TODAY | QUARANTINE |
| VAL-007 | LBNRIND IN (NORMAL, ABNORMAL, HIGH, LOW, ND) | QUARANTINE |

---

## Error Handling

- Missing subject reference → REJECT, log to `dlq.labs-to-sdtm`
- Unmapped test code → QUARANTINE, flag for CT mapping
- Numeric parse failure → set result_std_character, null numeric, log warning
- Duplicate lab record (SHARED-006) → MERGE (last-write-wins)
- Reference range not found → QUARANTINE with error "no_reference_range"
