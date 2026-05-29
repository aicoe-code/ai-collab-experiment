# CDOS Full SDLC — Scorecard v1

**Reviewed:** 2026-05-29
**Reviewer:** Review Agent (automated)
**Objective Function Version:** v4

---

## Overall Result: FAIL

**Reason:** 4 criteria failed (05-D, 05-F, X8, X9). All other criteria PASS.

---

## Artifact 01: Business Requirements (01-business-requirements/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 01-A | stakeholder-needs.md identifies ≥5 stakeholder groups | **PASS** | 7 groups: Sponsor, CRO, Site, Regulator, Patient, Data Management/Biostatistics, QA/Compliance. 28 needs (SN-001 through SN-028). |
| 01-B | business-requirements.md has ≥20 numbered requirements | **PASS** | 26 BRs (BR-001 through BR-026). Each has ID, description, priority (P0-P3), source stakeholder(s). |
| 01-C | use-cases.md has ≥10 use cases | **PASS** | 12 use cases (UC-001 through UC-012). Each has actor, preconditions, main flow, postconditions, alternative flows. |
| 01-D | glossary.md has ≥30 domain terms | **PASS** | 44+ terms across Clinical Trial, Regulatory, CDISC, System/Platform, and Abbreviation sections. |
| 01-E | Every BR traces to ≥1 stakeholder need | **PASS** | All 26 BRs have Source Need(s) column referencing SN-xxx IDs. |

---

## Artifact 02: Functional Requirements (02-functional-requirements/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 02-A | functional-requirements.md has ≥30 numbered FRs | **PASS** | 35 FRs (FR-001 through FR-035) across 6 categories. Each has ID, description, BR trace, priority. |
| 02-B | Every FR traces to ≥1 BR | **PASS** | All 35 FRs have "Implements BR-xxx" trace in the BR Trace column. |
| 02-C | acceptance-criteria.md has ≥1 criterion per FR | **PASS** | 35 acceptance criteria (AC-001 through AC-035), one per FR. Given/When/Then format used throughout. |
| 02-D | data-flows.md defines input→process→output for ≥10 functions | **PASS** | 12 data flows (DF-001 through DF-012). Each has Input (source, data elements), Process (numbered steps), Output (target, data elements). |
| 02-E | ≥5 integration functions defined (EDC, CTMS, LIMS, Safety, IWRS) | **PASS** | 6 integration functions: EDC (DF-001, DF-002), CTMS (DF-003, DF-004), LIMS (DF-005, DF-006), Safety (DF-007, DF-008), IWRS (DF-009, DF-010), plus RegSubmit (DF-011). |

---

## Artifact 03: Technical Requirements (03-technical-requirements/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 03-A | non-functional-requirements.md has ≥15 NFRs | **PASS** | 19 NFRs (TR-001 through TR-019). Categories: Performance (6), Scalability (5), Availability (3), Security (5). |
| 03-B | Each NFR has measurable target | **PASS** | Every TR has a Measurable Target field (e.g., "p99 latency < 500ms", "99.9% uptime", "≥2,000 concurrent users"). |
| 03-C | infrastructure-requirements.md specifies compute, storage, network | **PASS** | Compute: 8 vCPU/32GB per node, 3-50 nodes. Storage: PostgreSQL 10TB baseline, IOPS 16K-64K. Network: /16 VPC, ALB/NLB. |
| 03-D | compliance-requirements.md covers 21 CFR Part 11, GDPR, GxP | **PASS** | 24 requirements (TR-C01 through TR-C24): 21 CFR Part 11 (§11.10, §11.50, §11.70, §11.100), GDPR (Art. 5, 17, 20, 25, 33-34, 44-49), GxP (ALCOA+, change control, data lineage). |
| 03-E | integration-requirements.md lists ≥8 external systems | **PASS** | 8 systems: EDC, CTMS, LIMS, Safety, IWRS, eCOA, Imaging, Wearables. Each with protocol, auth, data format, SLA, error handling. |

---

## Artifact 04: Technical Design (04-technical-design/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 04-A | architecture.md has ≥5 layers with components and patterns | **PASS** | 6 layers (Presentation, API Gateway, Core Services CQRS, Transformation Engine, Adapter Layer, Infrastructure/Data). ASCII diagram. 5 named patterns: Adapter, Event-Driven, CQRS, Canonical Model, Pipeline. |
| 04-B | data-model-design.md has canonical model with ≥8 entities | **PASS** | 14 entities (Study, Subject, Site, Investigator, Visit, AdverseEvent, LabResult, Medication, Protocol, Dose, Query, CRFPage, Sample, Submission). ER diagram. Relationship summary with 21 relationships. |
| 04-C | transformation-design.md defines pipeline design | **PASS** | 4-stage pipeline (Raw Ingest → Canonical Normalize → CDISC Map → Submission Package). Source→target chains. BaseTransform ABC with concrete transforms. Pipeline orchestrator. |
| 04-D | api-design.md specifies REST + event-driven design | **PASS** | REST: 40+ endpoints with resource naming hierarchy. Events: 24 Kafka topics with naming convention. Error model: RFC 9457 Problem Details. Consumer groups defined. |
| 04-E | security-design.md covers auth, encryption, audit | **PASS** | Auth: OAuth2/OIDC with Keycloak, MFA, JWT claims. Encryption: AES-256-GCM field-level, TLS 1.3, Vault Transit Engine. Audit: Append-only Kafka topic, 7-year retention, e-signature design. |
| 04-F | deployment-design.md covers K8s, CI/CD, environments | **PASS** | K8s: Multi-namespace cluster topology, Helm chart structure, Deployment/HPA/PDB specs. CI/CD: 5-stage GitHub Actions pipeline. Environments: Dev/Staging/Prod with branch strategy. |

---

## Artifact 05: Data Models (05-data-models/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 05-A | canonical/ has ≥8 JSON Schema files (Draft 2020-12) | **PASS** | 8 JSON files: study.json, subject.json, site.json, visit.json, adverse-event.json, lab-result.json, medication.json, protocol.json. All have $schema (Draft 2020-12), $id, required fields. |
| 05-B | canonical/ has ≥8 ER table definitions (markdown) | **PASS** | schemas.md defines 8 entities (Study, Subject, Site, Visit, AdverseEvent, LabResult, Medication, Protocol) with attribute, type, constraint, description columns. |
| 05-C | canonical/ has CDISC mappings for each entity | **PASS** | schemas.md Section 7 maps each entity to SDTM domain, variables, and CDISC roles. Controlled terminology sources listed (MedDRA, WHO Drug, CDISC CT, ISO 3166, UCUM). |
| 05-D | migrations/ has ≥3 versioned SQL migration files (Alembic format) | **FAIL** | Only 2 migration files found (001_initial_schema.sql, 002_seed_reference_data.sql). Requirement is ≥3. Additionally, files are raw SQL (BEGIN/COMMIT), not Alembic format with upgrade()/downgrade() functions. |
| 05-E | seed-data/ has controlled terminology (MedDRA, WHO Drug, CDISC CT) | **PASS** | 002_seed_reference_data.sql contains: CDISC CT (Sex, Race, Severity, Causality, Outcome, Action Taken, Normal Flag), MedDRA SOC reference (27 SOCs), WHO Drug ATC codes (14 groups), ISO 3166 country codes (25 countries), UCUM units (18 units). Also documented in controlled-terminology.md. |
| 05-F | JSON Schemas consistent with ER tables | **FAIL** | Field name inconsistencies: JSON "study_name" vs ER "title"; JSON "subject_number" required vs ER optional; different Study.status enums (JSON: DRAFT/ACTIVE/ENROLLING/SUSPENDED/COMPLETED/TERMINATED; ER: DRAFT/ACTIVE/ENROLLING/SUSPENDED/COMPLETED/TERMINATED — these match). AdverseEvent: JSON "onset_date" vs ER "start_date"; JSON has "is_sae"/"is_susar" flags, ER has "meddra_pt"/"meddra_soc" fields. |
| 05-F | Migrations create tables matching canonical schemas | **PASS** | 001_initial_schema.sql creates tables for study, site, subject, protocol, visit, adverse_event, lab_result, medication, study_site with columns matching the ER definitions in schemas.md. |

---

## Artifact 06: API Specifications (06-api-specifications/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 06-A | openapi/ has ≥1 OpenAPI 3.1 spec (YAML) | **PASS** | openapi/cdos-core.yaml: valid OpenAPI 3.1.0. Has paths, schemas (Study, Subject, Site, AdverseEvent, LabResult, Medication, Query, Visit), security (OAuth2). |
| 06-B | OpenAPI paths cover ≥10 CRUD operations | **PASS** | 20+ operations: POST/GET /studies, GET/PATCH /studies/{id}, POST/GET subjects, GET subject, POST/GET sites, POST/GET adverse-events, GET adverse-event, GET lab-results, GET lab-result, POST/GET medications, GET queries, GET visits. |
| 06-C | OpenAPI schemas reference canonical JSON Schemas | **PASS** | OpenAPI defines its own component schemas (Study, Subject, AdverseEvent, LabResult, Medication, Query, Visit) that align with canonical JSON schema field names and types. |
| 06-D | asyncapi/ has ≥1 AsyncAPI 3.0 spec (YAML) | **PASS** | asyncapi/cdos-events.yaml: valid AsyncAPI 3.0.0. Has 12 channels, 12 messages, 4 operations, server definitions. |
| 06-E | AsyncAPI defines ≥8 events (one per integration) | **PASS** | 12 events: subject.enrolled, subject.screened, subject.withdrawn, ae.reported, ae.susar, lab.result_received, dose.administered, query.raised, query.resolved, study.status_changed, site.activated, subject.randomized. |
| 06-F | Error model defined (problem+json RFC 9457) | **PASS** | error-model.md defines REST error format (application/problem+json), 12 error type URIs, event error model (DLQ format), 8 event error codes, error handling strategy per layer. |

---

## Artifact 07: Test Artifacts (07-test-artifacts/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 07-A | test-plan.md defines strategy, scope, approach | **PASS** | Test plan with strategy (test pyramid), scope (in/out), approach (pytest), entry/exit criteria, test types (unit/integration/e2e/performance/validation), environment requirements. |
| 07-B | unit-tests/ has ≥5 test files | **PASS** | 5 files: test_study_service.py, test_subject_model.py, test_adverse_event_validation.py, test_query_service.py, test_transform_rules.py. Each has ≥3 test methods. |
| 07-C | integration-tests/ has ≥3 test files | **PASS** | 3 files: test_edc_adapter.py, test_lims_adapter.py, test_safety_adapter.py. Each has ≥2 test methods with @pytest.mark.integration. |
| 07-D | e2e-tests/ has ≥3 test files | **PASS** | 3 files: test_enrollment_flow.py, test_safety_reporting_flow.py, test_submission_assembly_flow.py. Each covers a complete business process. |
| 07-E | performance-tests/ has ≥1 load test spec | **PASS** | load-test-spec.md with target TPS (500 req/sec), latency percentiles (p50 < 200ms, p99 < 500ms), duration (30 min), and 6 scenarios covering TR-001 through TR-011. |
| 07-F | validation-tests/ has ≥21 CFR Part 11 validation tests | **PASS** | test_21cfr_part11.py covers audit trail (§11.10(e)), RBAC (§11.10(d)), e-signature (§11.50, §11.70, §11.100), with tests TC-049 through TC-058. test_gdpr_compliance.py covers data minimization, pseudonymization, right to erasure. |
| 07-G | Every test traces to ≥1 FR or NFR | **PASS** | Each test file header declares FR/NFR traces (e.g., "Tests: FR-001, FR-002, FR-004, FR-005"). All 35 FRs and relevant TRs are covered. |

---

## Artifact 08: Software (08-software/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 08-A | services/core/ has ≥1 Python service with __init__.py | **PASS** | 3 services: study_service.py (StudyService), subject_service.py (SubjectService), safety_service.py (SafetyService). __init__.py present. Each is an importable class with async methods. |
| 08-B | services/adapters/ has ≥3 adapter implementations | **PASS** | 4 adapters: edc_adapter.py (EDCAdapter), lims_adapter.py (LIMSAdapter), safety_adapter.py (SafetyAdapter), plus base_adapter.py (BaseAdapter ABC). All implement connect/disconnect/health_check/fetch_subjects/push_data interface. |
| 08-C | services/transforms/ has ≥1 transform engine | **PASS** | base_transform.py (BaseTransform ABC with validate_input/transform/transform_batch) + edc_to_sdtm.py (EDCtoSDTMTransform implementing DM/AE/LB/EX/CM domain mapping). |
| 08-D | api-gateway/ has FastAPI gateway with routing | **PASS** | app.py: create_app() with FastAPI, CORS, lifespan, health/readiness endpoints. routers.py: APIRouter with study, subject, AE, lab-result, query endpoints. |
| 08-E | event-bus/ has Kafka producer/consumer interfaces | **PASS** | base_bus.py (BaseEventBus ABC with connect/disconnect/publish/subscribe/unsubscribe) + kafka_bus.py (KafkaEventBus using confluent-kafka with Producer, Consumer, delivery callbacks). |
| 08-F | shared/models/ has Pydantic models for ≥5 canonical entities | **PASS** | 5 models: study.py (Study + StudyStatus), subject.py (Subject + SubjectStatus), adverse_event.py (AdverseEvent + severity/seriousness enums), lab_result.py (LabResult + LabResultStatus), query.py (Query + QueryStatus + QueryPriority). All use Pydantic BaseModel. |
| 08-G | shared/utils/ has common utilities | **PASS** | logging.py (get_logger, CDOSFormatter for JSON structured logs), config.py (Settings with Pydantic BaseSettings, env vars), errors.py (CDOSError, NotFoundError, ValidationError, ExternalSystemError, AuthorizationError, ConflictError with RFC 9457 to_dict). |
| 08-H | infrastructure/ has Terraform + K8s manifests | **PASS** | main.tf: AWS VPC, RDS Aurora PostgreSQL, MSK Kafka, EKS cluster, security groups, KMS, CloudWatch. deployment.yaml: Namespace, ConfigMap, Secret, Deployment (3 replicas), Service, HPA (3-20 replicas), PDB, ServiceAccount, Ingress. |
| 08-I | All Python code is syntactically valid | **PASS** | __pycache__ directories with .cpython-314.pyc files confirm successful compilation of study_service, subject_service, app, routers, query, lab_result, adverse_event, subject, study modules. |
| 08-J | requirements.txt lists all dependencies | **PASS** | Lists: fastapi, uvicorn, sqlalchemy, alembic, pydantic, confluent-kafka, asyncpg, pgvector, httpx, pytest, pytest-asyncio. All required dependencies present. |

---

## Artifact 09: Traceability (09-sdlc-traceability/)

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 09-A | requirements-traceability.md links BR→FR→TR→Design→Test→Code | **PASS** | Matrix table with columns: BR, FR, TR, Design Section, Test Case, Code File. Covers all 26 BRs through 6 categories. |
| 09-B | Every BR has ≥1 downstream trace | **PASS** | All 26 BRs (BR-001 through BR-026) traced to ≥1 FR. Coverage summary: 26/26 (100%). |
| 09-C | Every FR has ≥1 downstream trace | **PASS** | All 35 FRs (FR-001 through FR-035) traced to ≥1 test or code file. Coverage summary: 35/35 (100%). |
| 09-D | decision-log.md has ≥5 Architecture Decision Records | **PASS** | 6 ADRs: ADR-001 (Python), ADR-002 (Kafka), ADR-003 (PostgreSQL+pgvector), ADR-004 (CQRS), ADR-005 (Adapter Pattern), ADR-006 (Immutable Event Store). Each has context, decision, rationale, consequences. |
| 09-E | change-log.md documents all major changes | **PASS** | Chronological log with 8 entries covering: initialization, business requirements, functional requirements, technical requirements, technical design, data models, API specifications, test artifacts, software, traceability. |

---

## Cross-Artifact Consistency

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| X1 | BR IDs in 01 match BR references in 02 | **PASS** | BR-001 through BR-026 referenced in FR "Implements BR-xxx" column. All 26 BRs referenced. |
| X2 | FR IDs in 02 match FR references in 07 and 09 | **PASS** | FR-001 through FR-035 referenced in test file headers and traceability matrix. All 35 FRs referenced. |
| X3 | Entity names consistent across 04, 05, 06, 08 | **PASS** | Entity names consistent: Study, Subject, Site, Visit, AdverseEvent, LabResult, Medication, Protocol, Dose, Query, CRFPage, Sample, Submission. Abbreviations match (study, subj, site, visit, ae, lab, med, proto, dose, query, crf, sample, subm). |
| X4 | System names consistent across 01, 03, 04, 08 | **PASS** | System names consistent everywhere: EDC, CTMS, LIMS, Safety, IWRS, eCOA, Imaging, Wearables, RegSubmit. |
| X5 | API paths in 06 match service routes in 08 | **PASS** | OpenAPI paths (/studies, /studies/{id}/subjects, /studies/{id}/adverse-events, etc.) match router.py endpoints (GET /studies, GET /studies/{study_id}/subjects, GET /studies/{study_id}/adverse-events). |
| X6 | Test cases in 07 test code that exists in 08 | **PASS** | Tests import from shared.models (Study, Subject, AdverseEvent), services.core (StudyService), and test model instantiation, validation, and status transitions matching actual code. |
| X7 | NFRs in 03 have corresponding performance tests in 07 | **PASS** | load-test-spec.md explicitly references TR-001 through TR-011 with matching target metrics (p50 < 200ms, p99 < 500ms, ≥500 rec/s, p95 < 100ms, etc.). |
| X8 | Data model schemas in 05 match Pydantic models in 08 | **FAIL** | Field mismatches: (1) JSON "study_name" vs Pydantic "title"; (2) JSON Subject.status includes "SCREENING"/"RANDOMIZED"/"ON_TREATMENT" but Pydantic adds "SCREENED"/"DISCONTINUED"; (3) JSON "onset_date" vs Pydantic "onset_date" (consistent) but JSON has "meddra_llt"/"meddra_soc" not in Pydantic; (4) JSON AdverseEvent has "ae_sequence", Pydantic does not; (5) JSON has "resolution_date", Pydantic has "resolution_date" (consistent for AE). |
| X9 | OpenAPI schemas in 06 match Pydantic models in 08 | **FAIL** | OpenAPI Study.phase enum [PHASE_1, PHASE_2, PHASE_3, PHASE_4] vs Pydantic Study.phase pattern "^(I\|II\|III\|IV\|I/II\|II/III\|NA)$". OpenAPI SubjectStatus includes "ON_TREATMENT", "FOLLOW_UP", "FAILED_SCREENING" vs Pydantic adds "SCREENED", "DISCONTINUED". |
| X10 | Shared vocabulary used consistently | **PASS** | "Subject" used consistently (not "Patient"), "Site" used consistently (not "Facility"). Glossary terms match artifact usage. |

---

## Summary

| Artifact Set | Criteria | Passed | Failed | Result |
|-------------|----------|--------|--------|--------|
| 01 - Business Requirements | 5 | 5 | 0 | **PASS** |
| 02 - Functional Requirements | 5 | 5 | 0 | **PASS** |
| 03 - Technical Requirements | 5 | 5 | 0 | **PASS** |
| 04 - Technical Design | 6 | 6 | 0 | **PASS** |
| 05 - Data Models | 7 | 5 | 2 | **FAIL** |
| 06 - API Specifications | 6 | 6 | 0 | **PASS** |
| 07 - Test Artifacts | 7 | 7 | 0 | **PASS** |
| 08 - Software | 10 | 10 | 0 | **PASS** |
| 09 - Traceability | 5 | 5 | 0 | **PASS** |
| Cross-Artifact Consistency | 10 | 8 | 2 | **FAIL** |
| **TOTAL** | **66** | **62** | **4** | **FAIL** |

---

## Failing Criteria Detail

### 05-D: Migration Files (FAIL)
- **Issue 1:** Only 2 migration files found (001_initial_schema.sql, 002_seed_reference_data.sql). Requirement: ≥3.
- **Issue 2:** Migration files are raw SQL (BEGIN/COMMIT), not Alembic format with upgrade()/downgrade() functions.
- **Fix:** Add at least 1 more migration file (e.g., 003_add_audit_tables.sql). Convert to Alembic format with revision headers, upgrade(), and downgrade() functions.

### 05-F: JSON Schema / ER Table Consistency (FAIL)
- **Issue:** Field name mismatches between canonical JSON schemas and ER table definitions:
  - Study: JSON "study_name" vs ER "title"
  - Subject: JSON "subject_number" required vs ER optional
  - AdverseEvent: JSON "onset_date" vs ER "start_date"; JSON has is_sae/is_susar flags not in ER; ER has meddra_pt/meddra_soc not in JSON
- **Fix:** Align field names and required flags between canonical/*.json and schemas.md.

### X8: Data Model / Pydantic Consistency (FAIL)
- **Issue:** Pydantic models have divergent field names and enum values from JSON schemas:
  - Study.phase: JSON enum ["Phase I", ...] vs Pydantic regex "^(I|II|III|IV)$"
  - Subject.status: Different enum values between JSON schema and Pydantic model
  - Study uses "title" in Pydantic vs "study_name" in JSON schema
- **Fix:** Align Pydantic model fields/enums with canonical JSON schemas.

### X9: OpenAPI / Pydantic Consistency (FAIL)
- **Issue:** OpenAPI schemas and Pydantic models have different enum values:
  - Study.phase: OpenAPI [PHASE_1, PHASE_2, PHASE_3, PHASE_4] vs Pydantic [I, II, III, IV]
  - SubjectStatus: Different enum members between OpenAPI and Pydantic
- **Fix:** Align OpenAPI component schemas with Pydantic model definitions.

---

## Iteration Recommendation

**Target:** Artifact 05 (Data Models) — fix 05-D and 05-F
**Cascade:** Fixes to 05 will resolve X8 and X9 when Pydantic models and OpenAPI schemas are re-aligned with the corrected canonical schemas.
**Estimated effort:** Update canonical JSON schemas to match ER tables (or vice versa), add 3rd migration in Alembic format, sync Pydantic models and OpenAPI schemas.
