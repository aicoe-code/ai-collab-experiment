# CDOS Alignment Report

**Reviewed by:** Agent-Align
**Date:** 2026-05-28
**Branch:** alignment/fixes
**Base:** main

---

## Summary

| Metric | Value |
|--------|-------|
| Total checks performed | 7 criteria + supplemental link checks |
| Misalignments found | 2 (1 vocabulary violation, 1 broken cross-references) |
| Fixes applied | 4 files modified |
| Overall assessment | **PASS with fixes** |

---

## Criterion Results

### X1: Entity Name Consistency
**Status: PASS**

All [Entity:*] references across modules 03, 04, 05, 06 match the canonical
entity names defined in ALIGNMENT_RULES.md. Exact case-sensitive matching verified.

Entities referenced (14 total):
Study, Subject, Site, Investigator, Visit, AdverseEvent, LabResult, Medication,
Protocol, Dose, Query, CRFPage, Sample, Submission

Note: 02-data-models/schemas.md formally defines 8 entities (Study, Subject,
Site, Visit, AdverseEvent, LabResult, Medication, Protocol). The remaining 6
(Dose, Query, CRFPage, Sample, Submission, Investigator) are referenced by
adapters and risk models but lack formal ER/JSON Schema/CDISC definitions.
This is a completeness gap, not a naming misalignment.

### X2: System Name Consistency
**Status: PASS**

All [System:*] references across modules 03, 05, 06 match the canonical system
names in ALIGNMENT_RULES.md and the adapter files in 04-integrations/.

Systems verified (10 total):
EDC, CTMS, LIMS, eTMF, Safety, IWRS, eCOA, Imaging, Wearables, RegSubmit

### X3: Transform Name Consistency
**Status: PASS**

All [Transform:*] references across modules 05, 06 match actual transform
files in 03-transformations/.

Transforms verified (3 referenced cross-module):
- [Transform:Protocol→EDC] → 01-protocol-to-edc.md
- [Transform:EDC→SDTM] → 02-edc-to-sdtm.md
- [Transform:SDTM→ADaM] → 06-sdtm-to-adam.md
- [Transform:Safety→ICSR] → 04-safety-to-icsr.md

### X4: CDISC Terminology Consistency
**Status: PASS**

SDTM domain codes (DM, AE, LB, CM, EX, SV) used in 03-transformations/
match those defined in 02-data-models/schemas.md CDISC mappings and
controlled-terminology.md.

CDISC CT codelists referenced in transforms (SEX, RACE, SEVERITY, RELATIONSHIP,
OUTCOME, ROUTE, UNIT, LBNRIND) match those catalogued in controlled-terminology.md.

### X5: Technology Stack Consistency
**Status: PASS**

All tools referenced in modules 03, 04, 07 appear in technology-stack.md
(23 tools total). Verified:
- Module 03: SAS, R, admiral, Pinnacle 21, Airflow
- Module 04: Medidata Rave, Argus Safety, Kafka, NiFi, Redis
- Module 07: Vault, Keycloak, PostgreSQL, OpenTelemetry, Grafana

### X6: No Contradictions
**Status: PASS**

No conflicting facts, counts, names, or claims found between any two modules.
Entity counts, system counts, and transform counts are consistent across all
references.

### X7: Shared Vocabulary
**Status: FAIL → FIXED**

**Misalignment found:** The Safety-to-ICSR transform (04-safety-to-icsr.md)
used `icsr.patient.*` as target field names. Per ALIGNMENT_RULES.md, CDOS
uses "Subject" not "Patient" as the canonical entity name.

**Fix applied:** Renamed all 4 field mappings from `icsr.patient.*` to
`icsr.subject.*`:
- `icsr.patient.id` → `icsr.subject.id`
- `icsr.patient.sex` → `icsr.subject.sex`
- `icsr.patient.age` → `icsr.subject.age`
- `icsr.patient.dob` → `icsr.subject.dob`

**Note:** Other uses of "patient" in the spec (e.g., "patient-reported outcomes",
"LPLV", "EHR patient demographics") are industry-standard terms referring to
external systems/concepts, not CDOS canonical entity names. These do not violate
the vocabulary rules.

---

## Supplemental: Cross-Reference Link Integrity

**Status: FAIL → FIXED**

3 files in 08-implementation/ referenced `../07-compliance/21-cfr-part-11.md`
but the actual filename is `21-cfr-part11.md` (no hyphen between "part" and "11").

Fixed in:
- roadmap.md
- cost-model.md
- success-metrics.md

---

## Completeness Observations (Not Alignment Violations)

1. **6 entities referenced but not formally defined in schemas.md:**
   Dose, Query, CRFPage, Sample, Submission, Investigator
   - Referenced by: EDC adapter, CTMS adapter, LIMS adapter, Safety adapter,
     IWRS adapter, risk models, compliance modules
   - Impact: Adapters and risk models assume these entities exist but they
     lack ER tables, JSON Schemas, and CDISC mappings
   - Recommendation: Add formal definitions in a future iteration

2. **Container Orchestration component in architecture overview** has no
   corresponding tool in technology-stack.md (Kubernetes covers this, but
   the component name doesn't appear in the tool table)

---

## Files Modified

| File | Change |
|------|--------|
| spec/03-transformations/04-safety-to-icsr.md | X7 fix: patient→subject in field mapping |
| spec/08-implementation/roadmap.md | Fixed broken link to 21-cfr-part11.md |
| spec/08-implementation/cost-model.md | Fixed broken link to 21-cfr-part11.md |
| spec/08-implementation/success-metrics.md | Fixed broken link to 21-cfr-part11.md |

---

## Assessment

The CDOS specification achieves strong cross-module alignment. Of 7 alignment
criteria, 5 passed without issues. 2 misalignments were found and fixed:
one vocabulary violation (X7) and one set of broken cross-reference links.
The spec is now aligned and ready for merge.
