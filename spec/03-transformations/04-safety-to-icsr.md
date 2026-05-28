# Transform: AdverseEvent → ICSR XML

## Overview

- Source: CDOS Canonical AdverseEvent entity
- Target: ICSR (Individual Case Safety Report) XML per ICH E2B(R3)
- Trigger: SAE or SUSAR report event
- Frequency: Real-time (event-driven on ae.reported)

---

## Field Mapping

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| AdverseEvent.ae_id | icsr.case_id | UUID → string | ICSR format |
| AdverseEvent.subject_id | icsr.patient.id | UUID → string | SHARED-001 |
| Subject.sex | icsr.patient.sex | Enum → ICH code | M/F/U |
| Subject.age | icsr.patient.age | int | direct copy |
| Subject.birth_date | icsr.patient.dob | Date → string | ISO 8601 |
| AdverseEvent.term | icsr.reaction[].event_text | none | direct copy |
| AdverseEvent.meddra_code | icsr.reaction[].event_code | none | MedDRA PT code |
| AdverseEvent.onset_date | icsr.reaction[].event_onset | Date → string | ISO 8601 |
| AdverseEvent.resolution_date | icsr.reaction[].event_resolution | Date → string | ISO 8601 |
| AdverseEvent.severity | icsr.reaction[].severity | Enum → ICH code | 1=MILD,2=MOD,3=SEV |
| AdverseEvent.serious | icsr.seriousness | boolean → Enum | SERIOUS/NON_SERIOUS |
| AdverseEvent.causality | icsr.causality.assessment | Enum → ICH code | map |
| Medication.term | icsr.drug[].name | none | direct copy |
| Dose.treatment | icsr.drug[].name | none | direct copy |
| Study.study_id | icsr.study_id | none | direct copy |
| Site.site_id | icsr.reporter_site | none | direct copy |

---

## Business Rules

```
RULE-001: IF AdverseEvent.serious = false
          THEN SKIP (non-serious AEs do not generate ICSRs)

RULE-002: IF AdverseEvent.serious = true
          THEN icsr.report_type = "EXPEDITED"
          AND icsr.transmission_date = NOW_UTC()
          AND icsr.report_due_date = compute_due_date(AdverseEvent.onset_date, 15)

RULE-003: IF AdverseEvent.term matches SUSAR_criteria(meddra_code, expectedness)
          THEN icsr.report_type = "SUSAR"
          AND icsr.report_due_date = compute_due_date(AdverseEvent.onset_date, 7)
          AND NOTIFY [System:Safety] AND regulatory_authority

RULE-004: IF AdverseEvent.outcome = "DEATH"
          THEN icsr.seriousness_reason = "DEATH"
          AND icsr.report_priority = "URGENT"

RULE-005: IF AdverseEvent.outcome = "LIFE_THREATENING"
          THEN icsr.seriousness_reason = "LIFE_THREATENING"

RULE-006: FOR EACH Medication CONCOMITANT to AdverseEvent onset window:
          icsr.drug.APPEND({
            name: Medication.term,
            indication: Medication.indication,
            start_date: Medication.start_date,
            end_date: Medication.end_date,
            dosage: Medication.dose + " " + Medication.dose_unit
          })

RULE-007: STAMP_AUDIT(record, "T04", system_user)  // SHARED-009
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-001 | icsr.case_id NOT NULL | REJECT |
| VAL-002 | AdverseEvent.serious = true | SKIP (not error) |
| VAL-003 | meddra_code IS valid MedDRA PT | QUARANTINE |
| VAL-004 | onset_date NOT NULL | REJECT |
| VAL-005 | icsr.reaction COUNT >= 1 | REJECT |
| VAL-006 | icsr.drug COUNT >= 1 for causality | QUARANTINE |
| VAL-007 | ICSR XML validates against ICH E2B(R3) XSD | REJECT |

---

## Error Handling

- Missing serious flag → REJECT with error "serious_flag_required"
- Invalid MedDRA code → QUARANTINE, notify medical coding team
- XML validation failure → REJECT, log schema violations to `dlq.safety-to-icsr`
- Reporting deadline exceeded → ALERT to safety officer + log
- Duplicate ICSR for same AE → MERGE (version increment)
