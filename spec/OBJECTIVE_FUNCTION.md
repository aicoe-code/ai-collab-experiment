# CDOS Executable Specification — Objective Function v3

Each module is scored independently. The full spec PASSES when ALL modules pass.

---

## Module 01: Architecture (01-architecture/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 01-A | overview.md has ≥5 named layers, each with ≥2 components | Count layers and components |
| 01-B | ASCII architecture diagram present and parseable | Diagram shows boxes, connections, labels |
| 01-C | technology-stack.md has ≥15 real tools in a structured table | Each row: tool name, category, rationale, URL |
| 01-D | Design principles documented (≥5 principles) | e.g., event-driven, canonical model, adapter pattern |
| 01-E | All tools referenced in other modules appear in tech stack table | Cross-reference check |

## Module 2: Data Models (02-data-models/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 02-A | ≥8 canonical entities defined | Study, Subject, Site, Visit, AE, LabResult, Medication, Protocol minimum |
| 02-B | Each entity has ER table (entity, attributes, types, constraints, relationships) | Structured table format |
| 02-C | Each entity has JSON Schema (Draft 2020-12) | Valid JSON, parseable, $schema field present |
| 02-D | Each entity has CDISC mapping (domain, variables, controlled terms, role) | SDTM/CDASH domain codes correct |
| 02-E | schemas.md cross-references all entities with relationships | No orphan entities |
| 02-F | controlled-terminology.md covers MedDRA, WHO Drug, CDISC CT | At least 3 terminology systems |
| 02-G | JSON Schemas are consistent with ER tables (same fields, same types) | Cross-check |

## Module 3: Transformations (03-transformations/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 03-A | pipeline-overview.md shows full chain: raw → canonical → submission-ready | End-to-end diagram/table |
| 03-B | ≥8 named transforms (one per file) | Each has source, target, mapping, rules |
| 03-C | Each transform has field-level mapping table | source.field → target.field with type conversion |
| 03-D | Each transform has business rules (pseudocode or rule notation) | Not just prose — structured logic |
| 03-E | Each transform has validation rules (what constitutes valid output) | Constraints, range checks, referential integrity |
| 03-F | Each transform has error handling (reject/quarantine/default/alert) | Explicit failure behavior |
| 03-G | transform-rules.md defines shared derivation logic | Common rules referenced by multiple transforms |
| 03-H | No dead ends — every output has a downstream consumer or is terminal | Trace through pipeline |
| 03-I | Transform chain covers all 10 business processes | Protocol → eCTD pipeline complete |

## Module 4: Integrations (04-integrations/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 04-A | ≥8 system adapters defined (one per file) | Real vendor products |
| 04-B | Each adapter has API contract (endpoint, method, request/response schema, auth) | Structured format |
| 04-C | Each adapter has event contract (topic, schema, producer, consumer) | Structured format |
| 04-D | Each adapter has error handling + retry policy | Dead-letter queue, circuit breaker |
| 04-E | Each adapter has SLA (latency, availability) | Quantified targets |
| 04-F | api-contracts.md provides unified view | Cross-references all adapters |
| 04-G | Adapter data models reference canonical entities from 02-data-models | Cross-check |

## Module 5: Trial Designs (05-trial-designs/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 05-A | ≥5 trial designs covered | Parallel, adaptive, platform, crossover, RWE |
| 05-B | Each design specifies what changes in data models | New/modified entities listed |
| 05-C | Each design specifies what changes in transforms | Modified/added transforms listed |
| 05-D | Each design references canonical entities from 02-data-models | Cross-check |
| 05-E | Adaptive design has decision point specification | Trigger conditions, interim analysis rules |

## Module 6: Risk Models (06-risk-models/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 06-A | ≥5 risk categories covered | Enrollment, data quality, supply chain, site, regulatory |
| 06-B | Each risk has trigger conditions | Quantified thresholds (not vague) |
| 06-C | Each risk has detection method | How the system identifies the risk |
| 06-D | Each risk has mitigation strategy | Concrete actions |
| 06-E | Each risk specifies impact on data models | Which entities/transforms affected |
| 06-F | Risk models reference systems from 04-integrations | Cross-check |

## Module 7: Compliance (07-compliance/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 07-A | 21 CFR Part 11 addressed (audit trails, e-signatures, validation) | Dedicated content |
| 07-B | GDPR addressed (data minimization, pseudonymization, erasure) | Dedicated content |
| 07-C | GxP validation addressed (GAMP 5, CSV, change control) | Dedicated content |
| 07-D | Security/encryption addressed (at rest, in transit, field-level) | Dedicated content |
| 07-E | Compliance requirements map to systems in 04-integrations | Cross-check |

## Module 8: Implementation (08-implementation/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 08-A | roadmap.md has ≥4 phases with month ranges and deliverables | Structured phases |
| 08-B | cost-model.md has build vs buy analysis | Numbers with assumptions |
| 08-C | cost-model.md has ROI calculation with methodology | Not just a number — show the math |
| 08-D | success-metrics.md has ≥5 quantified metrics | Targets with units (e.g., "50% reduction") |
| 08-E | Implementation phases reference modules (which modules ship in which phase) | Cross-check |

---

## Cross-Module Consistency (ALIGNMENT_RULES.md)

These are checked by the Alignment Agent:

| ID | Criterion |
|----|-----------|
| X1 | Entity names in 02 match references in 03, 04, 05, 06 |
| X2 | System names in 04 match references in 03, 05, 06 |
| X3 | Transform names in 03 match references in 05, 06 |
| X4 | Controlled terms in 02 match usage in 03 transforms |
| X5 | Tech stack in 01 matches tools referenced in 03, 04, 07 |
| X6 | No contradictions between any two modules (facts, counts, names) |
| X7 | Shared vocabulary used consistently (see ALIGNMENT_RULES.md) |

---

## Scoring

```
PASS:  ALL criteria for ALL modules pass  AND  X1-X7 all pass
FAIL:  Any single criterion fails

On FAIL: Only the failing module is reworked (targeted iteration)
ITERATION LIMIT: 5 rounds per module
```
