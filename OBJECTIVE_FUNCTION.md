# CDOS Full SDLC — Objective Function v4

Each artifact set is scored independently. The full SDLC PASSES when ALL artifact sets pass.

---

## Artifact 01: Business Requirements (01-business-requirements/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 01-A | stakeholder-needs.md identifies ≥5 stakeholder groups with needs | Named groups (Sponsor, CRO, Site, Regulator, Patient) |
| 01-B | business-requirements.md has ≥20 numbered requirements (BR-001..) | Each has ID, description, priority, source stakeholder |
| 01-C | use-cases.md has ≥10 use cases | Each has actor, preconditions, main flow, postconditions, alternative flows |
| 01-D | glossary.md has ≥30 domain terms | Terms used consistently across all artifacts |
| 01-E | Every BR traces to ≥1 stakeholder need | Cross-reference check |

## Artifact 02: Functional Requirements (02-functional-requirements/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 02-A | functional-requirements.md has ≥30 numbered FRs | Each has ID, description, BR trace, priority |
| 02-B | Every FR traces to ≥1 BR | Cross-reference to 01-business-requirements |
| 02-C | acceptance-criteria.md has ≥1 criterion per FR | Given/When/Then format |
| 02-D | data-flows.md defines input→process→output for ≥10 functions | Structured format |
| 02-E | ≥5 integration functions defined (EDC, CTMS, LIMS, Safety, IWRS) | Each with source, target, data elements |

## Artifact 03: Technical Requirements (03-technical-requirements/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 03-A | non-functional-requirements.md has ≥15 NFRs | Performance, scalability, availability, security categories |
| 03-B | Each NFR has measurable target | e.g., "p99 latency < 500ms", "99.9% availability" |
| 03-C | infrastructure-requirements.md specifies compute, storage, network | Quantified (CPU, RAM, IOPS, bandwidth) |
| 03-D | compliance-requirements.md covers 21 CFR Part 11, GDPR, GxP | Each with specific system requirements |
| 03-E | integration-requirements.md lists ≥8 external systems | Each with protocol, auth, data format, SLA |

## Artifact 04: Technical Design (04-technical-design/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 04-A | architecture.md has ≥5 layers with components and patterns | ASCII diagram, design patterns named |
| 04-B | data-model-design.md has canonical model with ≥8 entities | ER diagram, entity descriptions, relationships |
| 04-C | transformation-design.md defines pipeline design | Source→target chains, transform engine architecture |
| 04-D | api-design.md specifies REST + event-driven design | Resource naming, event topology, error model |
| 04-E | security-design.md covers auth, encryption, audit | OAuth2/OIDC, field-level encryption, audit trail design |
| 04-F | deployment-design.md covers K8s, CI/CD, environments | Dev/staging/prod, Helm charts, pipeline stages |

## Artifact 05: Data Models (05-data-models/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 05-A | canonical/ has ≥8 JSON Schema files (Draft 2020-12) | Valid JSON, $schema, $id, required fields |
| 05-B | canonical/ has ≥8 ER table definitions (markdown) | Entity, attribute, type, constraint, description |
| 05-C | canonical/ has CDISC mappings for each entity | SDTM domain, variable, role, controlled term |
| 05-D | migrations/ has ≥3 versioned SQL migration files | Alembic format: upgrade() and downgrade() |
| 05-E | seed-data/ has controlled terminology (MedDRA, WHO Drug, CDISC CT) | SQL or CSV format |
| 05-F | JSON Schemas are consistent with ER tables | Cross-check fields and types |
| 05-F | Migrations create tables matching the canonical schemas | Cross-check DDL vs JSON Schema |

## Artifact 06: API Specifications (06-api-specifications/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 06-A | openapi/ has ≥1 OpenAPI 3.1 spec (YAML) | Valid OpenAPI, paths, schemas, security |
| 06-B | OpenAPI paths cover ≥10 CRUD operations | Named resources matching canonical entities |
| 06-C | OpenAPI schemas reference canonical JSON Schemas | Cross-check |
| 06-D | asyncapi/ has ≥1 AsyncAPI 3.0 spec (YAML) | Valid AsyncAPI, channels, messages |
| 06-E | AsyncAPI defines ≥8 events (one per integration) | Event schemas match canonical entities |
| 06-F | Error model defined (problem+json RFC 9457) | Consistent across REST and events |

## Artifact 07: Test Artifacts (07-test-artifacts/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 07-A | test-plan.md defines strategy, scope, approach | Entry/exit criteria, test types, environment |
| 07-B | unit-tests/ has ≥5 test files | Python pytest files, ≥3 tests each |
| 07-C | integration-tests/ has ≥3 test files | Per adapter or transform |
| 07-D | e2e-tests/ has ≥3 test files | Per business process (enrollment, safety, submission) |
| 07-E | performance-tests/ has ≥1 load test spec | Target TPS, latency percentiles, duration |
| 07-F | validation-tests/ has ≥21 CFR Part 11 validation tests | Audit trail, e-signature, access control tests |
| 07-G | Every test traces to ≥1 FR or NFR | Cross-reference check |

## Artifact 08: Software (08-software/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 08-A | services/core/ has ≥1 Python service with __init__.py | Importable, FastAPI app scaffold |
| 08-B | services/adapters/ has ≥3 adapter implementations | Interface + concrete class, Python |
| 08-C | services/transforms/ has ≥1 transform engine | Interface + key implementation |
| 08-D | api-gateway/ has FastAPI gateway with routing | app.py with router includes |
| 08-E | event-bus/ has Kafka producer/consumer interfaces | Abstract base + implementation |
| 08-F | shared/models/ has Pydantic models for ≥5 canonical entities | Consistent with JSON Schemas |
| 08-G | shared/utils/ has common utilities | Logging, config, error handling |
| 08-H | infrastructure/ has Terraform + K8s manifests | At least provider.tf + deployment.yaml |
| 08-I | All Python code is syntactically valid | `python -m py_compile` passes |
| 08-J | requirements.txt lists all dependencies | FastAPI, SQLAlchemy, Kafka, Pydantic, pytest |

## Artifact 09: Traceability (09-sdlc-traceability/)

| ID | Criterion | Verification |
|----|-----------|-------------|
| 09-A | requirements-traceability.md links BR→FR→TR→Design→Test→Code | Matrix or table format |
| 09-B | Every BR has ≥1 downstream trace | To FR at minimum |
| 09-C | Every FR has ≥1 downstream trace | To test or code |
| 09-D | decision-log.md has ≥5 Architecture Decision Records | Format: context, decision, consequences |
| 09-E | change-log.md documents all major changes | Chronological |

---

## Cross-Artifact Consistency (ALIGNMENT_RULES.md)

| ID | Criterion |
|----|-----------|
| X1 | BR IDs in 01 match BR references in 02 |
| X2 | FR IDs in 02 match FR references in 07 (tests) and 09 (traceability) |
| X3 | Entity names consistent across 04, 05, 06, 08 |
| X4 | System names consistent across 01, 03, 04, 08 |
| X5 | API paths in 06 match service routes in 08 |
| X6 | Test cases in 07 test code that exists in 08 |
| X7 | NFRs in 03 have corresponding performance tests in 07 |
| X8 | Data model schemas in 05 match Pydantic models in 08 |
| X9 | OpenAPI schemas in 06 match Pydantic models in 08 |
| X10 | Shared vocabulary used consistently (Subject not Patient, Site not Facility) |

---

## Scoring

```
PASS:  ALL criteria for ALL artifact sets pass  AND  X1-X10 all pass
FAIL:  Any single criterion fails

On FAIL: Only the failing artifact set is reworked (targeted iteration)
ITERATION LIMIT: 5 rounds per artifact set
```
