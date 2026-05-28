# Shared Transform Rules

## Overview

This document defines derivation logic shared across multiple transforms.
Individual transform files reference these rules by ID (e.g., SHARED-001).

---

## SHARED-001: USUBJID Derivation

**Used by:** T02, T03, T04, T05, T06

```
DERIVE USUBJID:
  usubjid = study_id || "-" || subject_number
  WHERE study_id = Study.study_id (uppercase, alphanumeric only)
    AND subject_number = Subject.subject_number (zero-padded to 4 digits)
  EXAMPLE: "CDOS2024-0001"
  VALIDATION: LENGTH(usubjid) <= 40
  ON FAILURE: REJECT with error "usubjid_too_long"
```

---

## SHARED-002: Study Day Derivation (STDY)

**Used by:** T02, T03, T06

```
DERIVE STUDY_DAY(visit_date, study_start_date):
  IF visit_date IS NULL THEN RETURN NULL
  IF visit_date < study_start_date THEN
    study_day = (visit_date - study_start_date)    // negative, no Day 0
  ELSE
    study_day = (visit_date - study_start_date) + 1  // Day 1 = first dose day
  VALIDATION: study_day BETWEEN -9999 AND 9999
  ON FAILURE: QUARANTINE with error "invalid_study_day"
```

---

## SHARED-003: ISO Date Normalization

**Used by:** T01, T02, T03, T04, T06

```
NORMALIZE_DATE(raw_date, format_hint):
  TRY:
    parsed = parse_date(raw_date, format_hint)
    RETURN format(parsed, "yyyy-MM-dd")
  CATCH AmbiguousDateError:
    IF format_hint = "US" THEN
      RETURN format(parse_date(raw_date, "MM/dd/yyyy"), "yyyy-MM-dd")
    ELSE IF format_hint = "EU" THEN
      RETURN format(parse_date(raw_date, "dd/MM/yyyy"), "yyyy-MM-dd")
    ELSE
      QUARANTINE with error "ambiguous_date"
  CATCH InvalidDateError:
    REJECT with error "unparseable_date"
```

---

## SHARED-004: CDISC Controlled Terminology Lookup

**Used by:** T02, T03, T05

```
LOOKUP_CT(codelist_name, input_value):
  match = SELECT term_code FROM cdisc_ct
          WHERE codelist = codelist_name
            AND (term_value = input_value
                 OR term_code = input_value
                 OR synonyms CONTAINS input_value)
  IF match.count = 1 THEN RETURN match.term_code
  IF match.count > 1 THEN QUARANTINE with error "ambiguous_ct_term"
  IF match.count = 0 THEN QUARANTINE with error "unmapped_ct_term"
```

---

## SHARED-005: Visit Window Validation

**Used by:** T02, T03

```
VALIDATE_VISIT_WINDOW(actual_date, planned_date, window_days):
  IF actual_date IS NULL THEN RETURN "MISSING"
  deviation = ABS(actual_date - planned_date)
  IF deviation <= window_days THEN RETURN "IN_WINDOW"
  IF deviation <= window_days * 2 THEN RETURN "OUT_OF_WINDOW"
  RETURN "VIOLATION"
```

---

## SHARED-006: Duplicate Detection

**Used by:** T02, T03, T05

```
CHECK_DUPLICATE(record, target_dataset, match_keys):
  existing = SELECT * FROM target_dataset
             WHERE ALL(key = record[key] FOR key IN match_keys)
  IF existing IS NULL THEN RETURN "NEW"
  IF existing.audit_timestamp < record.audit_timestamp THEN
    RETURN "UPDATE"     // last-write-wins
  ELSE
    RETURN "STALE"      // incoming is older, discard
```

---

## SHARED-007: Record Sequence Number Derivation

**Used by:** T02, T06

```
DERIVE_SEQ(domain, subject_id):
  max_seq = SELECT MAX(seq) FROM domain WHERE usubjid = subject_id
  IF max_seq IS NULL THEN RETURN 1
  RETURN max_seq + 1
```

---

## SHARED-008: Imputation Flag

**Used by:** T02, T03, T06

```
SET_IMPUTED_FLAG(field, was_imputed):
  IF was_imputed THEN RETURN "Y"
  RETURN ""
```

---

## SHARED-009: Audit Trail Stamp

**Used by:** ALL transforms

```
STAMP_AUDIT(record, transform_id, user_id):
  record.dtc_transform = NOW_UTC()
  record.transform_id = transform_id
  record.transform_user = user_id
  record.transform_version = config.version
  RETURN record
```

---

## SHARED-010: Null Handling Convention

**Used by:** ALL transforms

```
HANDLE_NULL(value, action):
  IF action = "BLANK" THEN
    IF value IS NULL THEN RETURN ""
  ELSE IF action = "MISSING_CODE" THEN
    IF value IS NULL THEN RETURN "ND"  // or domain-specific code
  ELSE IF action = "REJECT" THEN
    IF value IS NULL THEN RAISE NullValueError
  ELSE IF action = "DEFAULT" THEN
    IF value IS NULL THEN RETURN default_value
  RETURN value
```

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-05-28 | Agent-Transform | Initial shared rules |
