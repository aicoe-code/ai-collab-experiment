# CDOS — Technical Architecture

## 1. Overview

The Clinical Data Orchestration System (CDOS) is designed as a layered, event-driven platform that ingests clinical data from multiple source systems (EDC, CTMS, LIMS, Safety, IWRS, eCOA, Imaging, Wearables), transforms it through a canonical model to CDISC standards (SDTM, ADaM), and produces regulatory submission artifacts consumed by RegSubmit.

This architecture satisfies:
- **04-A**: ≥5 layers with components, ASCII diagram, named design patterns
- Cross-references: BR-001 through BR-020, FR-001 through FR-030, TR-001 through TR-015

---

## 2. Architecture Principles

| ID | Principle | Rationale |
|----|-----------|-----------|
| ADR-001 | Layered architecture with strict dependency rules | Separation of concerns, testability |
| ADR-002 | Event-driven integration via Kafka | Decoupling, replayability, auditability |
| ADR-003 | Canonical data model as single source of truth | Eliminates N×M mapping problem |
| ADR-004 | Adapter pattern for external systems | Isolate vendor-specific logic |
| ADR-005 | CQRS for read/write optimization | High-throughput ingestion vs. low-latency queries |
| ADR-006 | Immutable event store | 21 CFR Part 11 audit trail compliance |
| ADR-007 | Python + FastAPI as primary stack | Async performance, type safety via Pydantic |

---

## 3. Layered Architecture (6 Layers)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 6: PRESENTATION                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Web UI       │  │  CLI Tools   │  │  Regulatory Dashboard    │  │
│  │  (React)      │  │  (Typer)     │  │  (Submission Status)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 5: API GATEWAY                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Gateway (api-gateway/app.py)                        │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │  │
│  │  │ Auth (OIDC) │ │ Rate Limit │ │ Validation │ │ Routing  │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 4: CORE SERVICES (CQRS)                   │
│  ┌─────────────────────────┐  ┌─────────────────────────────────┐ │
│  │  COMMAND SIDE (Write)    │  │  QUERY SIDE (Read)              │ │
│  │  ┌────────────────────┐  │  │  ┌──────────────────────────┐  │ │
│  │  │ StudyService        │  │  │  │ StudyQueryService         │  │ │
│  │  │ SubjectService      │  │  │  │ SubjectQueryService       │  │ │
│  │  │ AdverseEventService │  │  │  │ AdverseEventQueryService  │  │ │
│  │  │ SubmissionService   │  │  │  │ SubmissionQueryService    │  │ │
│  │  └────────────────────┘  │  │  └──────────────────────────┘  │ │
│  └─────────────────────────┘  └─────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 3: TRANSFORMATION ENGINE                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Transform Pipeline                                            │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ Raw       │→ │ Canonical    │→ │ CDISC    │→ │Submission│ │  │
│  │  │ Ingest    │  │ Normalize    │  │ SDTM/ADaM│  │ Package  │ │  │
│  │  └──────────┘  └──────────────┘  └──────────┘  └──────────┘ │  │
│  │                                                                │  │
│  │  Base classes: BaseTransform → concrete transforms             │  │
│  └──────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 2: ADAPTER LAYER (Adapter Pattern)         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐ │
│  │ EDC      │ │ CTMS    │ │ LIMS    │ │ Safety  │ │ IWRS        │ │
│  │ Adapter  │ │ Adapter │ │ Adapter │ │ Adapter │ │ Adapter     │ │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └──────┬──────┘ │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────────────┐ │
│  │ eCOA     │ │ Imaging │ │Wearables│ │ RegSubmit Adapter       │ │
│  │ Adapter  │ │ Adapter │ │ Adapter │ │                         │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────────────────────┘ │
│                                                                    │
│  Base class: BaseAdapter (ABC) → connect, fetch, push, disconnect │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 1: INFRASTRUCTURE / DATA                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │PostgreSQL│  │ Kafka     │  │ Redis    │  │ Object Storage   │  │
│  │(Primary  │  │ (Event    │  │ (Cache + │  │ (S3/MinIO:       │  │
│  │ Store)   │  │  Bus)     │  │  Queue)  │  │  submission pkgs)│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                        │
│  │ Vault    │  │ Keycloak │  │Prometheus│                        │
│  │(Secrets) │  │ (IdP)    │  │+ Grafana │                        │
│  └──────────┘  └──────────┘  └──────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Design Patterns

### 4.1 Adapter Pattern (Layer 2)

Each external system (EDC, CTMS, LIMS, Safety, IWRS, eCOA, Imaging, Wearables, RegSubmit) is wrapped in an adapter implementing `BaseAdapter`:

```
BaseAdapter (ABC)
  ├── connect() -> None
  ├── disconnect() -> None
  ├── fetch_subjects(study_id) -> list[Subject]
  ├── fetch_adverse_events(study_id) -> list[AdverseEvent]
  ├── push_submission(pkg) -> SubmissionReceipt
  └── health_check() -> bool

Concrete:
  EDCAdapter(BaseAdapter)        # Medidata Rave, Oracle InForm, etc.
  CTMSAdapter(BaseAdapter)       # Oracle Siebel CTMS, etc.
  LIMSAdapter(BaseAdapter)       # Covance LIMS, etc.
  SafetyAdapter(BaseAdapter)     # Argus Safety, etc.
  IWRSAdapter(BaseAdapter)       # Signant Health, etc.
  eCOAAdapter(BaseAdapter)       # ERT, Clario, etc.
  ImagingAdapter(BaseAdapter)    # BioClinica, etc.
  WearablesAdapter(BaseAdapter)  # ActiGraph, etc.
  RegSubmitAdapter(BaseAdapter)  # Veeva Vault RIM, Lorenz docuBridge
```

**Rationale**: Each source system has unique APIs, auth mechanisms, and data formats. The adapter isolates these details, presenting a uniform interface to the transformation engine.

### 4.2 Event-Driven Architecture (Cross-Layer)

All state changes produce domain events published to Kafka:

```
Producer → [Kafka Topic] → Consumer(s)

Events:
  study.created          → CTMS sync, audit log
  subject.enrolled       → IWRS randomization trigger
  adverse_event.reported → Safety system notification, SUSAR check
  crf_page.submitted     → Transformation engine trigger
  query.raised           → EDC notification
  submission.packaged    → RegSubmit upload trigger
  lab_result.received    → LIMS reconciliation
  dose.administered      → EX domain update
```

**Rationale**: Decouples producers from consumers, enables replay for audit (21 CFR Part 11), and supports multiple independent consumers per event.

### 4.3 CQRS Pattern (Layer 4)

Separates command (write) and query (read) paths:

```
COMMAND SIDE                          QUERY SIDE
─────────────                         ──────────
POST /studies                         GET /studies
  → StudyService.create()               → StudyQueryService.list()
  → Write to PostgreSQL                 → Read from PostgreSQL replica
  → Emit study.created                  → Optimized for reporting

POST /subjects                        GET /studies/{id}/subjects
  → SubjectService.enroll()             → SubjectQueryService.list_by_study()
  → Write to PostgreSQL                 → Denormalized views for fast reads
  → Emit subject.enrolled
```

**Rationale**: Ingestion (from 9 source systems) is write-heavy and throughput-sensitive. Reporting/querying (dashboards, regulatory review) is read-heavy and latency-sensitive. CQRS allows independent scaling.

### 4.4 Canonical Model Pattern (Cross-Layer)

All data passes through a canonical model before any downstream processing:

```
Source System Data (vendor-specific)
       │
       ▼
  Raw Ingest (store as-is + metadata)
       │
       ▼
  Canonical Model (Study, Subject, AdverseEvent, LabResult, ...)
       │
       ├──→ CDISC SDTM (DM, AE, LB, EX, CM domains)
       ├──→ CDISC ADaM (ADSL, ADAE, ADLB, ...)
       └──→ Submission Package (Define-XML + datasets)
```

**Rationale**: Without a canonical model, integrating N source systems with M downstream consumers requires N×M transformations. The canonical model reduces this to N+M transformations.

### 4.5 Pipeline Pattern (Layer 3)

Transformation follows a strict pipeline:

```
Raw → Validate → Normalize → Map → Enrich → Output
```

Each stage is a `BaseTransform` implementation:

```
BaseTransform (ABC)
  ├── transform(input) -> output
  ├── validate(input) -> ValidationResult
  └── get_metadata() -> TransformMetadata

Concrete:
  RawIngestTransform        # Ingest + store raw payload
  CanonicalNormalizeTransform # Map vendor fields to canonical model
  SdtmMappingTransform      # Map canonical → SDTM domains
  AdamMappingTransform      # Map canonical → ADaM datasets
  DefineXmlTransform        # Generate Define-XML metadata
  SubmissionPackageTransform # Package for RegSubmit
```

---

## 5. Data Flow Summary

```
┌─────────┐     ┌───────────┐     ┌───────────────┐     ┌───────────┐
│ Source   │────▶│ Adapter   │────▶│ Transform     │────▶│ Canonical │
│ Systems │     │ Layer     │     │ Engine        │     │ Store     │
│ (EDC,   │     │ (Layer 2) │     │ (Layer 3)     │     │ (Layer 1) │
│ CTMS..) │     └───────────┘     └───────────────┘     └─────┬─────┘
└─────────┘                                                    │
                                                               ▼
┌─────────┐     ┌───────────┐     ┌───────────────┐     ┌───────────┐
│RegSubmit│◀────│ Adapter   │◀────│ Submission    │◀────│ CDISC     │
│ System  │     │ Layer     │     │ Packaging     │     │ Transform │
└─────────┘     └───────────┘     └───────────────┘     └───────────┘
```

---

## 6. Component Inventory

| Component | Layer | Technology | Responsibility |
|-----------|-------|------------|----------------|
| Web UI | 6 | React + TypeScript | User interaction, dashboards |
| API Gateway | 5 | FastAPI (Python) | Auth, routing, validation |
| StudyService | 4 | Python + SQLAlchemy | Study lifecycle management |
| SubjectService | 4 | Python + SQLAlchemy | Subject enrollment, status |
| AdverseEventService | 4 | Python + SQLAlchemy | AE processing, SUSAR checks |
| SubmissionService | 4 | Python + SQLAlchemy | Submission packaging, status |
| Transform Engine | 3 | Python | Raw → Canonical → CDISC → Submission |
| EDC Adapter | 2 | Python + httpx | EDC system integration |
| CTMS Adapter | 2 | Python + httpx | CTMS system integration |
| LIMS Adapter | 2 | Python + httpx | LIMS system integration |
| Safety Adapter | 2 | Python + httpx | Safety system integration |
| IWRS Adapter | 2 | Python + httpx | IWRS system integration |
| eCOA Adapter | 2 | Python + httpx | eCOA system integration |
| Imaging Adapter | 2 | Python + httpx | Imaging system integration |
| Wearables Adapter | 2 | Python + httpx | Wearables system integration |
| RegSubmit Adapter | 2 | Python + httpx | Regulatory submission delivery |
| PostgreSQL | 1 | PostgreSQL 16 | Primary data store |
| Kafka | 1 | Apache Kafka 3.7 | Event bus |
| Redis | 1 | Redis 7 | Caching, rate limiting |
| S3/MinIO | 1 | S3-compatible | Submission package storage |
| Vault | 1 | HashiCorp Vault | Secrets management |
| Keycloak | 1 | Keycloak 24 | Identity provider (OIDC) |
| Prometheus + Grafana | 1 | OSS stack | Monitoring, alerting |

---

## 7. Non-Functional Architecture Attributes

| Attribute | Design Decision | TR Reference |
|-----------|----------------|--------------|
| Availability | Multi-AZ PostgreSQL, Kafka 3-broker cluster | TR-001 |
| Scalability | Horizontal pod autoscaling (Layer 3-4) | TR-002 |
| Performance | CQRS read replicas, Redis caching | TR-003 |
| Security | mTLS between services, field-level encryption | TR-005 |
| Auditability | Immutable event store, append-only audit log | TR-007 |
| Observability | Distributed tracing (OpenTelemetry), structured logging | TR-009 |

---

## 8. Architecture Decision Records (Summary)

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Layered architecture | Accepted |
| ADR-002 | Kafka as event bus | Accepted |
| ADR-003 | Canonical data model | Accepted |
| ADR-004 | Adapter pattern for integrations | Accepted |
| ADR-005 | CQRS for read/write separation | Accepted |
| ADR-006 | Immutable event store | Accepted |
| ADR-007 | Python + FastAPI stack | Accepted |
