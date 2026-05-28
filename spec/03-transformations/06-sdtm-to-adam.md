# Transform: SDTM → ADaM

## Overview

- Source: CDISC SDTM datasets (DM, AE, LB, EX, CM)
- Target: CDISC ADaM datasets (ADSL, ADAE, ADLB, ADPC)
- Trigger: Analysis request or statistical analysis plan (SAP) finalization
- Frequency: On-demand (pre-analysis batch)

---

## Field Mapping

### SDTM DM → ADaM ADSL

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| DM.USUBJID | ADSL.USUBJID | none | direct copy |
| DM.SUBJID | ADSL.SUBJID | none | direct copy |
| DM.SITEID | ADSL.SITEID | none | direct copy |
| DM.SEX | ADSL.SEX | none | direct copy |
| DM.AGE | ADSL.AGE | none | direct copy |
| DM.RACE | ADSL.RACE | none | direct copy |
| DM.ETHNIC | ADSL.ETHNIC | none | direct copy |
| DM.STDTC (first dose date) | ADSL.TRTSDT | string → numeric date | SAS date |
| DM.ENDTC (last visit date) | ADSL.TRTEDT | string → numeric date | SAS date |
| DM.STDTC | ADSL.TRTSDTM | string → datetime | ISO 8601 → SAS datetime |
| derived | ADSL.TRTDURD | computed | TRTEDT - TRTSDT + 1 |
| derived | ADSL.ITTFL | computed | RULE-001 |
| derived | ADSL.SAFETYFL | computed | RULE-002 |
| derived | ADSL.COMPLFL | computed | RULE-003 |
| DM.ACTARM | ADSL.TRTP | none | planned treatment |
| DM.ARM | ADSL.TRT01P | none | assigned treatment |
| derived | ADSL.EFFFL | computed | RULE-005 |

### SDTM AE → ADaM ADAE

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| AE.USUBJID | ADAE.USUBJID | none | direct copy |
| AE.AESEQ | ADAE.AESEQ | none | direct copy |
| AE.AETERM | ADAE.AETERM | none | direct copy |
| AE.AESEV | ADAE.AESEV | none | direct copy |
| AE.AESER | ADAE.AESER | none | direct copy |
| AE.AEREL | ADAE.AEREL | none | direct copy |
| AE.AESTDTC | ADAE.AESTDT | string → numeric date | SAS date |
| AE.AEENDTC | ADAE.AEENDT | string → numeric date | SAS date |
| derived | ADAE.ASTDY | computed | SHARED-002 |
| derived | ADAE.AENDY | computed | SHARED-002 |
| derived | ADAE.AEDURD | computed | AEENDT - AESTDT + 1 |
| derived | ADAE.TRTEMFL | computed | RULE-004 |
| ADSL.TRTP | ADAE.TRTP | join | link via USUBJID |

### SDTM LB → ADaM ADLB

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| LB.USUBJID | ADLB.USUBJID | none | direct copy |
| LB.LBTESTCD | ADLB.PARAMCD | none | direct copy |
| LB.LBTEST | ADLB.PARAM | none | direct copy |
| LB.LBSTRESN | ADLB.AVAL | decimal | analysis value |
| LB.LBSTRESC | ADLB.AVALC | none | character analysis value |
| LB.LBNRIND | ADLB.ABNFL | computed | "Y" if ABNORMAL |
| derived | ADLB.BASE | computed | RULE-006 |
| derived | ADLB.CHG | computed | AVAL - BASE |
| derived | ADLB.PCHG | computed | (CHG / BASE) * 100 |
| derived | ADLB.AVISIT | computed | from visit schedule |
| derived | ADLB.AVISITN | computed | numeric visit |

---

## Business Rules

```
RULE-001: ITT FLAG (ADSL.ITTFL):
          IF Subject has at least one post-baseline efficacy assessment
          THEN ADSL.ITTFL = "Y"
          ELSE ADSL.ITTFL = ""

RULE-002: SAFETY FLAG (ADSL.SAFETYFL):
          IF Subject received at least one dose of study drug (EX records exist)
          THEN ADSL.SAFETYFL = "Y"
          ELSE ADSL.SAFETYFL = ""

RULE-003: COMPLETION FLAG (ADSL.COMPLFL):
          IF Subject completed all required visits per protocol
          THEN ADSL.COMPLFL = "Y"
          ELSE ADSL.COMPLFL = ""

RULE-004: TREATMENT EMERGENT FLAG (ADAE.TRTEMFL):
          IF AE onset date >= first dose date AND AE onset date <= last dose date + 30
          THEN ADAE.TRTEMFL = "Y"
          ELSE ADAE.TRTEMFL = ""

RULE-005: EFFICACY FLAG (ADSL.EFFFL):
          IF Subject in ITT population AND has no major protocol deviations
          THEN ADSL.EFFFL = "Y"
          ELSE ADSL.EFFFL = ""

RULE-006: BASELINE VALUE (ADLB.BASE):
          baseline = SELECT L.STBRESN FROM LB L
                     WHERE L.USUBJID = current.USUBJID
                       AND L.LBTESTCD = current.LBTESTCD
                       AND L.VISIT = "BASELINE"
          ADLB.BASE = baseline

RULE-007: ANALYSIS VISIT ASSIGNMENT (ADLB.AVISIT):
          MAP LB.VISIT to ADSL visit schedule
          IF visit is post-baseline THEN ADAVISIT = visit_name
          ELSE ADAVISIT = "Baseline"

RULE-008: STAMP_AUDIT(record, "T06", system_user)  // SHARED-009
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-001 | ADSL.USUBJID matches DM.USUBJID | REJECT |
| VAL-002 | ADSL has exactly one row per USUBJID | REJECT |
| VAL-003 | ADAE.USUBJID exists in ADSL | REJECT |
| VAL-004 | ADLB.BASE NOT NULL for post-baseline records | QUARANTINE |
| VAL-005 | ADLB.CHG = AVAL - BASE (consistent) | REJECT |
| VAL-006 | ADSL.TRTSDT <= ADSL.TRTEDT | REJECT |
| VAL-007 | All ADaM datasets have DEFINE-XML companion | REJECT |

---

## Error Handling

- Missing SDTM source record → REJECT, log to `dlq.sdtm-to-adam`
- No baseline value → set BASE = NULL, flag CHG as NULL, log warning
- Multiple baseline records → use earliest, QUARANTINE duplicate
- Date derivation failure → QUARANTINE, manual review
- Define-XML generation failure → REJECT with error "define_xml_error"
