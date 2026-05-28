# CDOS Answer — Objective Function v2

This document defines the PASS/FAIL criteria for the Clinical Development Operating System answer.
The answer PASSES only when ALL criteria in Sections A, B, and C are satisfied.

---

## SECTION A: SYSTEM DESIGN

| ID | Criterion | How to Verify |
|----|-----------|---------------|
| A1 | Architecture diagram with named layers and components | ASCII diagram present, ≥4 layers, each with ≥2 components |
| A2 | 10+ named clinical systems with integration details | Real vendor products cited (Medidata Rave, Oracle InForm, Veeva Vault, etc.) |
| A3 | Data standards cited correctly | CDISC SDTM, ADaM, ODM, CDASH, Define-XML all named; HL7 FHIR R4 referenced |
| A4 | Security/compliance addressed | 21 CFR Part 11, GDPR, GxP each have dedicated content |
| A5 | 5+ challenges with solutions | Each challenge has a concrete solution, not vague platitudes |
| A6 | Implementation roadmap | Named phases with month ranges and deliverables |
| A7 | Technology stack | ≥10 real tools named in a structured table |

---

## SECTION B: EXECUTABLE SPECIFICATION

### B1. Business Process Coverage

The answer MUST define data flow for ALL of these processes:

1. Trial design / protocol authoring
2. Site selection & activation
3. Subject screening & enrollment
4. Randomization & treatment assignment
5. Data collection (CRF, labs, eCOA, imaging, wearables)
6. Safety reporting (AE, SAE, SUSAR)
7. Data cleaning & query management
8. Medical coding (MedDRA, WHO Drug)
9. Statistical analysis & reporting
10. Regulatory submission (eCTD assembly)

Each process has: description, trigger, inputs, outputs, systems involved.

### B2. Data Model Specification

#### B2a. Schema Formats

Each data model MUST be defined in ALL of these formats:
- **Entity-relationship tables**: entity name, attributes, data types, constraints, relationships
- **JSON Schema**: machine-readable schema definition (Draft 2020-12 or later)
- **CDISC domain style**: domain code, variables, controlled terminology, role (Identifier/Topic/Qualifier/Rule/RecordQualifier)

#### B2b. Transformation Specification

For EACH business process step, define:
- **Source data model**: input schema reference
- **Target data model**: output schema reference
- **Field-level mapping table**: source.entity.field → target.entity.field
- **Data type conversions**: explicit conversion rules (e.g., ISO 8601 string → datetime)
- **Business rules**: derivation logic in pseudocode or rule-engine notation
- **Aggregation / splitting / merging**: when data volume changes between input and output
- **Validation rules**: what constitutes valid output (constraints, range checks, referential integrity)
- **Error handling**: behavior on transform failure (reject, quarantine, default, alert)

#### B2c. Transformation Chain

- Full pipeline from raw source → canonical → submission-ready
- Each hop is a named transformation with defined input/output
- No dead ends: every output has a downstream consumer or is a terminal artifact
- Terminal artifacts are: submission datasets, analysis datasets, regulatory documents, dashboards

### B3. Trial Design Accommodation

The specification MUST handle at minimum:

| Trial Design | What Changes |
|-------------|--------------|
| Fixed sample parallel group | Baseline (default) |
| Adaptive design | Decision points in transformation chain, interim analysis data models |
| Multi-arm / platform trial | Arm-specific data models, shared control arm logic |
| Crossover design | Period-specific data models, carryover effect transforms |
| Real-world evidence | EHR/FHIR source adapters, unstructured data ingestion |

For each: explicit description of what changes in data models and/or transformations.

### B4. Operational Risk & Uncertainty

Define risk models for:

| Risk Category | Required Content |
|--------------|-----------------|
| Enrollment risk | Trigger conditions, detection method, mitigation, impact on data models |
| Data quality risk | Trigger conditions, detection method, mitigation, impact on data models |
| Supply chain risk | Trigger conditions, detection method, mitigation, impact on data models |
| Site risk | Trigger conditions, detection method, mitigation, impact on data models |
| Regulatory risk | Trigger conditions, detection method, mitigation, impact on data models |

Each risk model must include quantified parameters (e.g., "enrollment rate < 2 subjects/site/month triggers alert").

### B5. Interoperability Contracts

Each system integration MUST define:
- API contract: endpoint, HTTP method, request schema, response schema, auth method
- OR event contract: topic/queue name, message schema, producer, consumer
- Error handling: retry policy, dead-letter queue, circuit breaker thresholds
- SLA: expected latency, availability target

---

## SECTION C: CROSS-REFERENTIAL INTEGRITY

| ID | Criterion | How to Verify |
|----|-----------|---------------|
| C1 | Every entity in B2 appears in the architecture (A1) | Cross-reference entity names against architecture diagram components |
| C2 | Every transformation in B2 maps to a system in A2 | Cross-reference transform names against system list |
| C3 | No orphan data models | Every input schema has at least one consuming transformation |
| C4 | No dead-end transformations | Every output schema either feeds downstream or is a terminal artifact |
| C5 | Section cross-references consistent | No contradictions between sections (names, versions, counts match) |

---

## SCORING

```
PASS:  A1-A7 ALL PASS  AND  B1-B5 ALL PASS  AND  C1-C5 ALL PASS
FAIL:  Any single criterion fails

On FAIL:
  1. List each failing criterion with specific evidence
  2. Prioritize B-section failures (executable spec gaps) over A-section (design doc gaps)
  3. Agent 2 addresses gaps, Agent 3 re-evaluates
  
ITERATION LIMIT: 5 rounds
```

---

## ACCEPTANCE

When all criteria pass, the answer is merged to main with a summary of what was verified.
