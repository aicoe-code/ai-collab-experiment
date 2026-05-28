# Transform: Protocol → EDC Metadata

## Overview

- Source: Protocol (study protocol document and metadata)
- Target: EDC system configuration (CDASH-aligned CRF definitions)
- Trigger: Protocol finalization or amendment approval
- Frequency: On-demand (protocol version change)

---

## Field Mapping

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| proto.study_id | edc.study_id | none | direct copy |
| proto.study_title | edc.study_name | none | direct copy |
| proto.phase | edc.study_phase | string → Enum | map to EDC phase codes |
| proto.indication | edc.therapeutic_area | none | direct copy |
| proto.amendment_number | edc.version | int → string | "v" + str(amendment) |
| proto.sites[].site_id | edc.site_config[].site_oid | none | generate OID |
| proto.visits[].visit_name | edc.visit_def[].visit_name | none | direct copy |
| proto.visits[].visit_window | edc.visit_def[].visit_window_days | string → int | parse days |
| proto.schedule[].crf_pages | edc.form_def[] | complex | build CRF definitions |
| proto.eligibility_criteria | edc.ie_criteria[] | complex | split into individual items |
| proto.endpoints | edc.endpoint_forms[] | complex | map to ePRO/CRF fields |

---

## Business Rules

```
RULE-001: IF proto.status != "FINALIZED"
          THEN REJECT with error "protocol_not_finalized"

RULE-002: IF proto.amendment_number > 0
          THEN edc.version = "v" + str(proto.amendment_number)
          ELSE edc.version = "v1"

RULE-003: FOR EACH visit IN proto.visits:
          edc.visit_def.APPEND({
            visit_name: visit.visit_name,
            visit_number: visit.visit_number,
            visit_window_days: parse_window(visit.visit_window),
            forms: map_crf_pages(visit.crf_pages)
          })

RULE-004: IF proto.phase IN ("I", "II")
          THEN edc.monitoring_level = "ENHANCED"
          ELSE edc.monitoring_level = "STANDARD"

RULE-005: FOR EACH criterion IN proto.eligibility_criteria:
          edc.ie_criteria.APPEND({
            criterion_id: generate_id("IE"),
            criterion_text: criterion.text,
            criterion_type: criterion.type,  // "INCLUSION" or "EXCLUSION"
            response_type: infer_response_type(criterion.text)
          })
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-001 | proto.study_id NOT NULL | REJECT |
| VAL-002 | proto.study_title NOT NULL | REJECT |
| VAL-003 | proto.phase IN valid_phases | QUARANTINE |
| VAL-004 | proto.visits COUNT > 0 | REJECT |
| VAL-005 | Each visit has unique visit_number | REJECT |
| VAL-006 | CRF page count per visit <= 50 | QUARANTINE |

---

## Error Handling

- Missing required protocol field → REJECT, log to `dlq.protocol-to-edc`
- Invalid phase value → QUARANTINE for manual mapping
- Duplicate visit numbers → REJECT with error "duplicate_visit_number"
- Protocol amendment conflict → MERGE using amendment chain
