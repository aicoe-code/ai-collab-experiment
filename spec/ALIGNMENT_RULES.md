# CDOS Alignment Rules

Every module author MUST read this file first. These rules ensure cross-module consistency.

---

## 1. Canonical Entity Names

Use EXACTLY these names (case-sensitive) when referring to data entities:

| Canonical Name | Abbreviation | Description |
|---------------|-------------|-------------|
| Study | study | A clinical trial (protocol, amendments, sites) |
| Subject | subj | A participant enrolled in a study |
| Site | site | A clinical investigation site |
| Investigator | inv | A principal investigator or sub-investigator |
| Visit | visit | A scheduled study visit for a subject |
| AdverseEvent | ae | An adverse event reported for a subject |
| LabResult | lab | A laboratory test result |
| Medication | med | A concomitant or study medication |
| Protocol | proto | The study protocol document and its metadata |
| Dose | dose | A dose of study drug administered |
| Query | query | A data clarification request |
| CRFPage | crf | A case report form page |
| Sample | sample | A biological specimen |
| Submission | subm | A regulatory submission artifact |

Do NOT use synonyms. "Patient" → Subject. "Facility" → Site. "AE" → AdverseEvent.

---

## 2. Canonical System Names

Use EXACTLY these names when referring to clinical systems:

| Canonical Name | Category | Real Products |
|---------------|----------|--------------|
| EDC | Data Capture | Medidata Rave, Oracle InForm, Veeva Vault CDMS, Castor |
| CTMS | Trial Management | Oracle Siebel CTMS, Medidata CTMS, Veeva Vault CTMS |
| LIMS | Laboratory | Medidata Rave Lab, Covance LIMS, ICON LIMS |
| eTMF | Document Mgmt | Veeva Vault eTMF, Montrium, Florence eBinders |
| Safety | Pharmacovigilance | Argus Safety, ArisGlobal, Oracle AERS |
| IWRS | Randomization | Signant Health, 4G Clinical, Medidata RTSM |
| eCOA | Outcomes | ERT, Clario, Medidata Patient Cloud |
| Imaging | Medical Imaging | BioClinica, Parexel Imaging, Medidata Imaging |
| Wearables | IoT/Sensors | ActiGraph, Verily, Apple HealthKit |
| RegSubmit | Regulatory | Veeva Vault RIM, Lorenz docuBridge, Extedo |

When naming a specific product, always prefix with the category:
"EDC: Medidata Rave" not just "Rave".

---

## 3. CDISC Terminology

| Term | Definition | Standard |
|------|-----------|----------|
| SDTM | Study Data Tabulation Model | CDISC SDTM v3.4 |
| ADaM | Analysis Data Model | CDISC ADaM v2.1 |
| ODM | Operational Data Model | CDISC ODM v2.0 |
| CDASH | Clinical Data Acquisition Standards Harmonization | CDISC CDASH v2.1 |
| Define-XML | Metadata specification for datasets | CDISC Define-XML v2.1 |
| CT | Controlled Terminology | CDISC CT (current quarterly release) |

SDTM domain codes: 2-character uppercase (DM, AE, LB, EX, CM, etc.)
ADaM dataset names: uppercase (ADSL, ADAE, ADLB, etc.)

---

## 4. File Naming Conventions

- Module files: lowercase, hyphen-separated (e.g., `edc-adapter.md`)
- JSON Schema files: lowercase, dot-separated (e.g., `adverse-event.json`)
- No spaces in filenames
- One topic per file (no mega-files)

---

## 5. Data Model Format

Each entity definition MUST include three representations:

### 5a. ER Table Format

```markdown
## AdverseEvent

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| ae_id | UUID | PK, NOT NULL | Unique adverse event identifier |
| subject_id | UUID | FK → Subject, NOT NULL | Subject who experienced the AE |
| study_id | UUID | FK → Study, NOT NULL | Study context |
| term | String(200) | NOT NULL | Reported AE term |
| meddra_code | String(20) | FK → MedDRA | Coded MedDRA PT code |
| severity | Enum(MILD, MODERATE, SEVERE) | NOT NULL | CTCAE grade |
| ... | ... | ... | ... |
```

### 5b. JSON Schema Format

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://cdos.io/schemas/adverse-event.json",
  "title": "AdverseEvent",
  "type": "object",
  "required": ["ae_id", "subject_id", "study_id", "term", "severity"],
  "properties": {
    "ae_id": { "type": "string", "format": "uuid" },
    "subject_id": { "type": "string", "format": "uuid" },
    ...
  }
}
```

### 5c. CDISC Mapping Format

```markdown
| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| ae_id | AESEQ | AE | Identifier | — |
| subject_id | USUBJID | AE | Identifier | — |
| term | AETERM | AE | Topic | — |
| meddra_code | AEPTCD | AE | Qualifier | MedDRA PT |
| severity | AESEV | AE | Qualifier | SEVERITY codelist |
```

---

## 6. Transformation Format

Each transformation file MUST follow this structure:

```markdown
# Transform: [Source] → [Target]

## Overview
- Source: [source entity/system]
- Target: [target entity/system]
- Trigger: [what initiates the transform]
- Frequency: [real-time / batch / on-demand]

## Field Mapping

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| edc.AETERM | ae.term | none | direct copy |
| edc.AESEV | ae.severity | string → Enum | map to CTCAE grade |
| ... | ... | ... | ... |

## Business Rules

```
RULE-001: IF ae.severity = "SEVERE" AND ae.serious = true
          THEN trigger_safety_report(ae)
          
RULE-002: IF ae.onset_date > ae.resolution_date
          THEN REJECT with error "onset_after_resolution"
```

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-001 | ae.term NOT NULL | REJECT |
| VAL-002 | ae.onset_date ≤ TODAY | QUARANTINE |
| ... | ... | ... |

## Error Handling

- Missing required field → REJECT, log to error queue
- Invalid value → QUARANTINE for manual review
- Duplicate → MERGE with existing (last-write-wins by audit timestamp)
```

---

## 7. Interoperability Contract Format

Each adapter file MUST follow this structure:

```markdown
# Adapter: [System Name]

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /studies/{id}/subjects | GET | path: study_id | Subject[] | OAuth2 Bearer |
| /subjects | POST | Subject (JSON) | Subject (with id) | OAuth2 Bearer |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| subject.enrolled | SubjectEnrolledEvent | EDC | CTMS, IWRS |
| ae.reported | AeReportedEvent | EDC | Safety, Monitor |

## Error Handling
- Retry: 3 attempts with exponential backoff (1s, 5s, 25s)
- Dead letter queue: dlq.[system-name]
- Circuit breaker: 5 failures in 60s → open for 30s

## SLA
- Latency: p99 < 500ms (API), < 5s (event delivery)
- Availability: 99.9% uptime
```

---

## 8. Cross-Reference Convention

When a module references an entity, system, or transform from another module, use:

- Entity: `[Entity:AdverseEvent]` → links to 02-data-models/canonical/adverse-event.json
- System: `[System:EDC]` → links to 04-integrations/edc-adapter.md
- Transform: `[Transform:EDC→SDTM]` → links to 03-transformations/02-edc-to-sdtm.md
- Risk: `[Risk:Enrollment]` → links to 06-risk-models/enrollment-risk.md

The Alignment Agent verifies all cross-references resolve to actual files.

---

## 9. Shared Abbreviations

| Abbreviation | Full Form |
|-------------|-----------|
| CRF | Case Report Form |
| SAE | Serious Adverse Event |
| SUSAR | Suspected Unexpected Serious Adverse Reaction |
| eCTD | Electronic Common Technical Document |
| ICSR | Individual Case Safety Report |
| PQRS | Pharmacovigilance-Query-Response-Safety |
| GCP | Good Clinical Practice |
| CSV | Computer System Validation |
| RWD | Real-World Data |
| RWE | Real-World Evidence |
| EHR | Electronic Health Record |
