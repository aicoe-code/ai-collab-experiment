# CDOS Architecture Overview

## 1. System Purpose

The Clinical Development Operating System (CDOS) is a unified platform that orchestrates clinical trial data from protocol design through regulatory submission. It replaces fragmented point-to-point integrations with a canonical, event-driven architecture that ensures CDISC compliance, data integrity, and real-time visibility across all clinical operations.

---

## 2. Architecture Layers

### Layer 1: Presentation Layer
Provides user-facing interfaces for all clinical stakeholders.

| Component | Description |
|-----------|-------------|
| **Study Dashboard** | Real-time visualization of study health metrics: enrollment rates, query aging, AE summaries, and site performance KPIs |
| **Monitoring Console** | Risk-based monitoring interface showing triggered risk signals, SDV status, and site-level data quality scores |
| **Submission Builder** | Drag-and-drop eCTD assembly tool for compiling regulatory submission packages from CDOS-managed artifacts |

### Layer 2: Orchestration Layer
Coordinates business processes, workflow automation, and cross-system event routing.

| Component | Description |
|-----------|-------------|
| **Workflow Engine** | State-machine-driven process orchestration (e.g., AE processing from receipt → coding → severity grading → safety reporting) |
| **Event Bus** | Publish-subscribe message broker routing domain events (subject.enrolled, ae.reported, query.raised) to all subscribed systems |
| **Transformation Pipeline** | Sequential execution of data transforms from raw EDC data → CDISC CDASH → SDTM → ADaM with validation gates between each stage |
| **Rule Engine** | Declarative business rule evaluation for risk triggers, auto-queries, and compliance checks |

### Layer 3: Data Layer
Manages canonical data models, persistence, and CDISC-compliant data structures.

| Component | Description |
|-----------|-------------|
| **Canonical Data Store** | Central repository holding CDOS canonical entities (Study, Subject, Site, AdverseEvent, LabResult, etc.) with full audit trail |
| **CDISC Mapping Service** | Bidirectional mapping engine between CDOS canonical models and CDISC standards (CDASH, SDTM, ADaM, ODM) |
| **Metadata Registry** | Stores dataset definitions, controlled terminology versions (MedDRA, WHO Drug, CDISC CT), and Define-XML metadata |
| **Data Quality Engine** | Continuous validation against CDISC conformance rules, edit checks, and business logic constraints |

### Layer 4: Integration Layer
Connects external clinical systems via standardized adapters.

| Component | Description |
|-----------|-------------|
| **EDC Adapter** | Bidirectional connector to electronic data capture systems (Medidata Rave, Oracle InForm, Veeva Vault CDMS) for CRF data ingestion |
| **Safety Adapter** | Interface to pharmacovigilance systems (Argus Safety, ArisGlobal) for SAE/SUSAR reporting and ICSR generation |
| **LIMS Adapter** | Laboratory data ingestion from central and local lab systems with unit normalization and reference range mapping |
| **IWRS Adapter** | Randomization and trial supply management integration for treatment assignment and drug accountability |

### Layer 5: Infrastructure Layer
Provides foundational platform services for security, observability, and deployment.

| Component | Description |
|-----------|-------------|
| **Identity & Access Management** | OAuth2/OIDC authentication with role-based access control (RBAC) aligned to clinical roles (CRA, DM, Biostat, Medical Monitor) |
| **Audit & Compliance Service** | 21 CFR Part 11 compliant immutable audit trail for all data changes with electronic signature support |
| **Observability Stack** | Distributed tracing, structured logging, and metrics collection for system health and SLA monitoring |
| **Encryption & Key Management** | AES-256 encryption at rest, TLS 1.3 in transit, field-level encryption for PHI/PII with HSM-backed key rotation |

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                                  │
│  ┌───────────────┐  ┌──────────────────┐  ┌────────────────────┐           │
│  │ Study         │  │ Monitoring       │  │ Submission         │           │
│  │ Dashboard     │  │ Console          │  │ Builder            │           │
│  └───────┬───────┘  └────────┬─────────┘  └─────────┬──────────┘           │
└──────────┼───────────────────┼───────────────────────┼─────────────────────┘
           │                   │                       │
           ▼                   ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                                 │
│  ┌───────────────┐  ┌──────────────────┐  ┌────────────────────┐           │
│  │ Workflow      │  │ Event Bus        │  │ Transformation     │           │
│  │ Engine        │◄─┤ (Pub/Sub)        ├──▶│ Pipeline           │           │
│  └───────┬───────┘  └────────┬─────────┘  └─────────┬──────────┘           │
│          │                   │                       │                      │
│          │            ┌──────┴───────┐               │                      │
│          └────────────▶ Rule Engine  ◀───────────────┘                      │
│                       └──────────────┘                                      │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐        │
│  │ Canonical Data   │  │ CDISC Mapping    │  │ Metadata           │        │
│  │ Store            │◄─┤ Service          ├──▶│ Registry           │        │
│  └────────┬─────────┘  └──────────────────┘  └────────────────────┘        │
│           │                                                                 │
│  ┌────────┴─────────┐                                                       │
│  │ Data Quality     │                                                       │
│  │ Engine           │                                                       │
│  └──────────────────┘                                                       │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INTEGRATION LAYER                                   │
│  ┌───────────────┐  ┌──────────────────┐  ┌────────────────────┐           │
│  │ EDC           │  │ Safety           │  │ LIMS               │           │
│  │ Adapter       │  │ Adapter          │  │ Adapter            │           │
│  └───────┬───────┘  └────────┬─────────┘  └─────────┬──────────┘           │
│          │                   │                       │                      │
│  ┌───────┴───────┐  ┌────────┴─────────┐  ┌─────────┴──────────┐           │
│  │ IWRS          │  │ eTMF             │  │ eCOA               │           │
│  │ Adapter       │  │ Adapter          │  │ Adapter            │           │
│  └───────────────┘  └──────────────────┘  └────────────────────┘           │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       INFRASTRUCTURE LAYER                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐        │
│  │ Identity &       │  │ Audit &          │  │ Observability      │        │
│  │ Access Mgmt      │  │ Compliance       │  │ Stack              │        │
│  └──────────────────┘  └──────────────────┘  └────────────────────┘        │
│  ┌──────────────────┐  ┌──────────────────┐                                │
│  │ Encryption &     │  │ Container        │                                │
│  │ Key Mgmt         │  │ Orchestration    │                                │
│  └──────────────────┘  └──────────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘

Cross-layer data flow:
  Presentation ──REST/GraphQL──▶ Orchestration ──Domain Events──▶ Data
  Data ──API Calls──▶ Integration ──Vendor APIs──▶ External Systems
  Infrastructure ──Sidecar/Middleware──▶ All Layers
```

---

## 4. Design Principles

### Principle 1: Canonical Data Model
All clinical data is normalized into a CDOS canonical model before any processing occurs. External system data (from EDC, LIMS, Safety, etc.) is transformed into canonical entities on ingestion and transformed back to vendor-specific formats on egress. This eliminates N×M point-to-point mappings and ensures a single source of truth for every Study, Subject, AdverseEvent, and LabResult.

**Concrete application:** When EDC: Medidata Rave sends CRF data, the EDC Adapter transforms Rave-specific ODM into CDOS canonical entities. Downstream consumers (CDISC Mapping Service, Monitoring Console) read only from the canonical store — they never need to understand Rave's internal schema.

### Principle 2: Event-Driven Architecture
All state changes in CDOS produce domain events published to the Event Bus. Consumers subscribe to events they care about without coupling to the producer. This enables real-time reactivity, loose coupling, and complete auditability of the system's history.

**Concrete application:** When a new AdverseEvent is created, the system publishes `ae.reported`. The Safety Adapter subscribes and triggers ICSR generation. The Monitoring Console subscribes and updates site-level AE rates. The Transformation Pipeline subscribes and queues the AE for SDTM mapping. None of these consumers know about each other.

### Principle 3: Adapter Pattern for Integrations
Every external system is connected through a standardized adapter that translates vendor-specific APIs, data formats, and error handling into CDOS's internal contracts. Adapters encapsulate vendor complexity and expose a uniform interface to the Orchestration Layer.

**Concrete application:** The EDC Adapter handles Medidata Rave's REST API pagination, OAuth token refresh, and ODM XML parsing internally. It exposes a clean internal API: `POST /ingest/crf-data` with canonical JSON. If the organization switches from Rave to Veeva Vault CDMS, only the adapter changes — no downstream impact.

### Principle 4: CDISC-First Data Design
Every data entity in CDOS has an explicit mapping to CDISC standards (CDASH, SDTM, ADaM). CDISC mappings are not an afterthought — they are defined alongside the canonical model. Controlled terminology is versioned and enforced at the data layer.

**Concrete application:** The canonical `AdverseEvent` entity includes CDISC mapping metadata: `ae.term → AETERM (AE domain, Topic variable)`, `ae.severity → AESEV (AE domain, Qualifier variable, SEVERITY codelist)`. The Data Quality Engine validates that all coded fields use the correct CDISC CT version before any SDTM dataset is generated.

### Principle 5: Separation of Concerns via Layered Architecture
Each layer has a single, well-defined responsibility and only communicates with adjacent layers through defined contracts. The Presentation Layer never directly accesses the Data Layer. The Integration Layer never directly modifies the Orchestration Layer's state.

**Concrete application:** The Submission Builder (Presentation) requests an eCTD package via the Orchestration Layer's API. The Workflow Engine coordinates data retrieval from the Data Layer, document generation via the CDISC Mapping Service, and assembly. The Submission Builder receives a completed package — it has no direct access to the canonical data store or external systems.

### Principle 6: Immutable Audit Trail
Every data mutation in CDOS is recorded as an append-only audit event. No record is ever physically deleted — only soft-deleted with a timestamp and reason. This satisfies 21 CFR Part 11 requirements and enables complete data lineage from source to submission.

**Concrete application:** When a CRA corrects an AdverseEvent severity from MILD to MODERATE, the original record is preserved with its creation timestamp. A new version is created with the updated value, the change timestamp, the CRA's identity, and the reason for change. Both versions are queryable, and the audit trail shows the complete modification history.

### Principle 7: Fail-Safe Defaults with Explicit Error Handling
Every data transformation, integration call, and business rule evaluation has explicit handling for failure cases. The system defaults to the safest action: quarantine suspicious data, retry transient failures, and alert on persistent errors. No data silently disappears.

**Concrete application:** If the LIMS Adapter receives a LabResult with a value outside the instrument's measurement range, the record is quarantined (not rejected) with an error code `LAB-004: value_out_of_range`. A Data Steward is alerted via the Monitoring Console. The quarantined record is excluded from SDTM mapping until reviewed but remains visible in the audit trail.

---

## 5. Cross-Layer Communication Patterns

| Pattern | Source Layer | Target Layer | Protocol | Use Case |
|---------|-------------|-------------|----------|----------|
| REST API | Presentation | Orchestration | HTTPS/JSON | User-initiated actions |
| GraphQL | Presentation | Data | HTTPS/JSON | Dashboard queries |
| Domain Events | Orchestration | All | AMQP/Kafka | State change notifications |
| Sync API | Orchestration | Integration | gRPC/Protobuf | Real-time system calls |
| Batch ETL | Integration | Data | SFTP/API | Scheduled data loads |
| Sidecar | Infrastructure | All | localhost/gRPC | Auth, audit, encryption |

---

## 6. Entity Relationship Summary

The canonical data model is defined in [02-data-models/](../02-data-models/). Key relationships relevant to architecture:

```
Study 1──N Subject
Study 1──N Site
Study 1──1 Protocol
Subject 1──N Visit
Subject 1──N AdverseEvent
Subject 1──N LabResult
Subject 1──N Medication
Subject 1──N Dose
Subject 1──N Sample
Site 1──N Investigator
AdverseEvent 1──N Query
CRFPage 1──N Query
Study 1──N Submission
```

All entities are referenced using the canonical names from [ALIGNMENT_RULES.md](../ALIGNMENT_RULES.md).

---

## 7. Technology Stack Reference

For detailed tool selections and rationale, see [technology-stack.md](./technology-stack.md).

---

## 8. Related Modules

| Module | Relationship |
|--------|-------------|
| [02-data-models](../02-data-models/) | Defines the canonical entities stored in the Data Layer |
| [03-transformations](../03-transformations/) | Implements the Transformation Pipeline in the Orchestration Layer |
| [04-integrations](../04-integrations/) | Implements the adapters in the Integration Layer |
| [05-trial-designs](../05-trial-designs/) | Extends architecture for specific trial design patterns |
| [06-risk-models](../06-risk-models/) | Drives the Rule Engine and Monitoring Console logic |
| [07-compliance](../07-compliance/) | Defines requirements for Infrastructure Layer services |
| [08-implementation](../08-implementation/) | Phases the build-out of all layers |
