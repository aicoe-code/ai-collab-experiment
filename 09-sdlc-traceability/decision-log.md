# CDOS Architecture Decision Log

## Document Metadata

| Field | Value |
|-------|-------|
| Document ID | CDOS-ADR-LOG-001 |
| Version | 1.0 |
| Author | Agent-Trace |
| Date | 2026-05-29 |
| Status | Draft |

---

## ADR-001: Python as Primary Implementation Language

**Status:** Accepted

**Context:**
The CDOS platform requires a language that supports async I/O for high-throughput data ingestion from multiple clinical systems (EDC, CTMS, LIMS, Safety, IWRS), strong type safety for regulated data handling, rich data science and CDISC tooling, and a mature web framework for REST APIs. The team evaluated Python, Java/Kotlin, Go, and TypeScript/Node.js.

**Decision:**
Python 3.11+ with FastAPI as the web framework, Pydantic for data validation and schema enforcement, and SQLAlchemy for ORM/database access.

**Rationale:**
- FastAPI provides async/await natively with Starlette/uvicorn, achieving p50 < 200ms (TR-001) and p99 < 500ms (TR-002) targets.
- Pydantic models enforce the canonical data model at runtime, with JSON Schema generation for cross-artifact consistency (X8, X9).
- Python has the strongest CDISC/SDTM ecosystem (cdisc-library, sdtmig-python) for the transformation engine.
- Type hints + mypy provide compile-time safety approaching statically-typed languages.
- Fast developer onboarding for clinical data teams who predominantly use Python/R.

**Consequences:**
- Positive: Single language across services, adapters, transforms, and shared models. JSON Schema ↔ Pydantic round-trip is native.
- Positive: pytest ecosystem enables comprehensive test coverage (07-A through 07-G).
- Negative: CPU-bound transforms (SDTM mapping at ≥500 rec/s per TR-003) may require Cython or multiprocessing for optimization.
- Negative: GIL limits true parallelism; mitigated by async I/O and horizontal scaling (TR-009: 3→50 nodes).
- Risk: Python version pinning required for reproducible builds in GxP environment.

---

## ADR-002: Event-Driven Architecture via Apache Kafka

**Status:** Accepted

**Context:**
CDOS integrates with 8+ external systems (EDC, CTMS, LIMS, Safety, IWRS, eCOA, Imaging, Wearables) that produce data at different rates and protocols. A synchronous request-reply integration pattern would create tight coupling, cascade failures, and prevent replay/audit of data flows — violating 21 CFR Part 11 audit trail requirements (TR-017).

**Decision:**
Apache Kafka as the central event bus, with domain events published to topic-per-entity (e.g., `subject.enrolled`, `ae.reported`, `visit.completed`). AsyncAPI 3.0 defines the event contracts. Consumer groups enable independent scaling per downstream service.

**Rationale:**
- Kafka provides durable, replayable event log — satisfying immutable audit trail requirements (TR-017: 15-year retention).
- Decouples producers (adapters) from consumers (transforms, dashboards, reconciliation) — enabling independent deployment and scaling.
- p95 publish-to-ack < 100ms (TR-004) is achievable with Kafka's append-only log and batching.
- Supports 1,000 topics, 10,000 partitions, 50K msg/sec (TR-011) for platform-wide throughput.
- Exactly-once semantics (EOS) with idempotent producers prevent duplicate data in clinical datasets.

**Consequences:**
- Positive: Loose coupling between EDC, CTMS, LIMS, Safety, IWRS adapters and downstream consumers.
- Positive: Event replay enables point-in-time reconstruction for regulatory audits.
- Positive: Consumer lag monitoring provides operational visibility (TR-011: lag < 10s).
- Negative: Eventual consistency model requires reconciliation jobs (FR-035: nightly cross-system recon).
- Negative: Kafka operational complexity (ZooKeeper→KRaft migration, partition rebalancing).
- Risk: Event schema evolution must be managed with Schema Registry and backward-compatible changes.

---

## ADR-003: PostgreSQL with pgvector for Persistent Storage

**Status:** Accepted

**Context:**
CDOS requires a primary data store for the canonical clinical data model (Study, Subject, Site, Visit, AdverseEvent, LabResult, CRFPage, Query, etc.) that supports: ACID transactions for data integrity, JSONB for flexible protocol-specific fields, vector similarity search for AI-assisted data review (FR-050 referenced in TR-006), and proven regulatory compliance track record.

**Decision:**
PostgreSQL 16+ with pgvector extension as the single relational + vector database.

**Rationale:**
- PostgreSQL is the most widely validated open-source RDBMS in FDA-submission environments.
- JSONB columns support metadata-driven study configuration (BR-016) without schema migrations per study.
- pgvector enables vector similarity search (TR-006: p95 < 500ms for top-10 matches) for semantic data review, query deduplication, and MedDRA term matching.
- Native partitioning supports multi-tenant study isolation (TR-008: 500 studies, 2.5B data points).
- Row-Level Security (RLS) enforces study-level and site-level data isolation for RBAC (TR-015).
- pg_cron enables scheduled reconciliation and aggregation jobs without external schedulers.

**Consequences:**
- Positive: Single database engine reduces operational complexity vs. separate RDBMS + vector store.
- Positive: Strong ecosystem for Alembic migrations (05-D), SQLAlchemy ORM, and pg_audit for compliance.
- Positive: Logical replication supports disaster recovery (TR-013: RTO ≤ 4h, RPO ≤ 1h).
- Negative: pgvector index performance degrades beyond ~10M vectors per table; requires partitioning strategy.
- Negative: Storage auto-expansion to 100TB (TR-010) requires careful tablespace and partition management.
- Risk: PostgreSQL major version upgrades require coordinated migration testing in GxP environment.

---

## ADR-004: CQRS Pattern for Read/Write Optimization

**Status:** Accepted

**Context:**
CDOS has fundamentally different read and write patterns:
- **Write side:** High-throughput data ingestion from EDC, LIMS, Safety (hundreds of records/sec), requiring strict validation, audit trail generation, and event publishing.
- **Read side:** Low-latency dashboards and queries (p50 < 200ms, p99 < 500ms per TR-001/TR-002) across potentially millions of records, with aggregation and vector search.

A single model serving both would require compromise on either ingestion throughput or query latency.

**Decision:**
Command Query Responsibility Segregation (CQRS) with:
- **Command side:** StudyService, SubjectService, AdverseEventService, SubmissionService write to PostgreSQL via SQLAlchemy, publish domain events to Kafka.
- **Query side:** StudyQueryService, SubjectQueryService, AdverseEventQueryService, SubmissionQueryService read from PostgreSQL with optimized indexes, materialized views, and pgvector indexes.

**Rationale:**
- Write path optimizes for correctness: full Pydantic validation, audit trail insertion (TR-017), event publishing (TR-004).
- Read path optimizes for speed: pre-computed aggregations, covering indexes, connection pooling.
- Materialized views refresh on event consumption, keeping read models eventually consistent.
- Aligns with layered architecture (architecture.md §3 Layer 4: Core Services CQRS).

**Consequences:**
- Positive: Write path can enforce all business rules without query-performance impact.
- Positive: Read path can use denormalized views, full-text search, and vector indexes independently.
- Positive: Clear separation of concerns improves testability (command tests vs. query tests).
- Negative: Eventual consistency window between write and read models (typically < 1 second).
- Negative: Additional complexity in keeping read models synchronized via event consumers.
- Risk: Stale read models during Kafka consumer lag spikes; mitigated by lag monitoring (TR-011).

---

## ADR-005: Adapter Pattern for External System Integration

**Status:** Accepted**

**Context:**
CDOS must integrate with 8+ external clinical systems (EDC, CTMS, LIMS, Safety, IWRS, eCOA, Imaging, Wearables, RegSubmit), each with different:
- Protocols (REST, SOAP, HL7 FHIR, SFTP, vendor-specific APIs)
- Authentication methods (OAuth2, API keys, mutual TLS, SAML)
- Data formats (JSON, XML, HL7, CSV, proprietary)
- SLAs and availability characteristics

A monolithic integration layer would be unmaintainable and create vendor lock-in.

**Decision:**
Adapter pattern with:
- `BaseAdapter` abstract base class defining the adapter interface (`connect`, `fetch_subjects`, `push_events`, `health_check`).
- Concrete implementations per system: `EDCAdapter`, `CTMSAdapter`, `LIMSAdapter`, `SafetyAdapter`, `IWRSAdapter`, `eCOAAdapter`, `ImagingAdapter`, `WearableAdapter`.
- Each adapter translates vendor-specific data to/from the canonical model.
- Adapters are registered via dependency injection and selected by configuration.

**Rationale:**
- Isolates vendor-specific logic behind a uniform interface, enabling testing with mock adapters.
- New EDC vendor support (e.g., switching from Medidata Rave to Castor) requires only a new adapter implementation.
- Each adapter manages its own connection pooling, retry logic, circuit breaker, and rate limiting.
- Aligns with architecture.md §3 (Layer 2: Integration Adapters) and ALIGNMENT_RULES §5c (Interface Pattern).

**Consequences:**
- Positive: Adding a new external system requires implementing BaseAdapter without modifying core services.
- Positive: Adapter unit tests can mock external systems, enabling fast CI/CD (TR-018: SAST/DAST per build).
- Positive: Circuit breaker per adapter prevents cascade failures from one system to others.
- Negative: Adapter proliferation (8+ adapters) requires consistent implementation patterns and shared utilities.
- Negative: Each adapter must independently implement authentication, retry, and error handling.
- Risk: Vendor API changes require adapter updates; mitigated by contract testing and versioned adapter interfaces.

---

## ADR-006: Immutable Event Store for 21 CFR Part 11 Audit Trail

**Status:** Accepted

**Context:**
21 CFR Part 11 requires that electronic records maintain an audit trail that is "secure, computer-generated, time-stamped" and captures "date and time of entries and actions that create, modify, or delete electronic records." The audit trail must be retained for the life of the record (minimum 15 years per TR-017). Traditional database audit triggers can be disabled, modified, or bypassed.

**Decision:**
Append-only event store backed by Kafka topics with compaction disabled for audit topics. Every data mutation produces an immutable event containing: user identity, timestamp (UTC), entity, field, old value, new value, and reason for change. Events are the system of record; PostgreSQL state is a materialized projection.

**Rationale:**
- Kafka's append-only log is inherently immutable — events cannot be modified after writing.
- Event retention configured to 15 years (TR-017) with tiered storage (hot/warm/cold) to manage costs.
- Audit queries reconstruct point-in-time state by replaying events from any timestamp.
- Aligns with ADR-002 (event-driven architecture) and security-design.md §3 (audit trail design).

**Consequences:**
- Positive: Audit trail integrity is guaranteed by storage immutability, not application logic.
- Positive: Point-in-time reconstruction supports regulatory inspection and data forensics.
- Positive: Event replay enables disaster recovery and data migration scenarios.
- Negative: Storage costs for 15-year retention across all entities; mitigated by tiered storage and compression.
- Negative: Event schema evolution over 15 years requires careful versioning and backward compatibility.
- Risk: Kafka topic configuration errors (compaction enabled on audit topics) could destroy audit data; mitigated by infrastructure-as-code and policy enforcement.
