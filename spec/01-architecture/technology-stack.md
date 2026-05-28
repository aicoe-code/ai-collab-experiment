# CDOS Technology Stack

## Overview

This document enumerates the real, production-grade tools selected for each component of the CDOS architecture. Every tool listed here has a concrete rationale tied to CDOS requirements. Tools referenced in other specification modules MUST appear in this table (criterion 01-E / X5).

---

## Core Platform Tools

| Tool Name | Category | Rationale | URL |
|-----------|----------|-----------|-----|
| **PostgreSQL** | Database / Canonical Store | ACID-compliant relational database with JSONB support for flexible entity storage. Supports row-level security (RLS) for multi-study isolation. Append-only audit tables via triggers satisfy 21 CFR Part 11 immutable audit trail requirements. | https://www.postgresql.org |
| **Apache Kafka** | Event Bus / Messaging | Distributed event streaming platform for domain events (subject.enrolled, ae.reported, query.raised). Provides exactly-once semantics, event sourcing capability, and 7-day retention for replay. Decouples producers from consumers across all layers. | https://kafka.apache.org |
| **Kubernetes** | Container Orchestration | Orchestrates all CDOS microservices with declarative deployment, auto-scaling, and self-healing. Supports sidecar injection for audit logging and encryption proxies. Runs on any cloud or on-premise for regulated environment flexibility. | https://kubernetes.io |
| **PostgREST** | API Layer / REST | Auto-generates RESTful APIs from PostgreSQL schema. Eliminates boilerplate CRUD code for canonical entities. Supports row-level security policies natively, ensuring study-level data isolation at the API layer. | https://postgrest.org |
| **Hasura** | API Layer / GraphQL | Provides real-time GraphQL subscriptions for dashboard queries. Enables the Monitoring Console to subscribe to live enrollment and AE data without polling. Supports role-based access control aligned to clinical roles. | https://hasura.io |
| **Camunda** | Workflow Engine | BPMN 2.0-compliant workflow orchestration for clinical processes (AE processing, query lifecycle, data review workflows). Visual process modeling enables clinical operations teams to review and approve workflow logic. | https://camunda.com |
| **Apache Airflow** | ETL / Batch Processing | Orchestrates scheduled data pipelines: nightly CDISC SDTM/ADaM generation, weekly lab data reconciliation, monthly submission artifact assembly. DAG-based dependencies ensure correct transform ordering. | https://airflow.apache.org |

## CDISC & Clinical Data Tools

| Tool Name | Category | Rationale | URL |
|-----------|----------|-----------|-----|
| **Pinnacle 21 (P21)** | CDISC Validation | Industry-standard CDISC conformance validator. Validates SDTM, ADaM, and Define-XML datasets against CDISC standards and FDA/PMDA business rules. Integrated into the Transformation Pipeline as a validation gate before submission. | https://www.pinnacle21.com |
| **SAS** | Statistical Computing | Regulatory-accepted statistical analysis environment. Generates ADaM datasets and Tables/Figures/Listings (TFLs). Required for FDA submissions where SAS transport files (.xpt) are the expected format. | https://www.sas.com |
| **R** | Statistical Computing | Open-source statistical computing for exploratory analysis, visualizations, and CDISC dataset generation via packages (haven, admiral, xportr). Used alongside SAS for analysis flexibility and reproducibility. | https://www.r-project.org |
| **ODM Study Designer** (XML4Pharma) | Define-XML Generation | Generates CDISC Define-XML v2.1 metadata files from dataset specifications. Automates the mapping between CDOS canonical entities and CDISC variables with controlled terminology references. | https://www.xml4pharma.com |
| **PhUSE Define-XML Tools** | Define-XML Utilities | Open-source Define-XML rendering and validation tools from the PhUSE community. Provides HTML rendering of Define-XML for reviewer-friendly dataset documentation. | https://github.com/phuse-org/define-xml-tools |
| **admiral** (R package) | ADaM Programming | CDISC-contributed R package for ADaM dataset creation. Provides modular, reusable functions for ADSL, ADAE, ADLB derivations that align with CDISC ADaM v2.1 implementation guides. | https://pharmaverse.github.io/admiral/ |

## Integration & Data Quality Tools

| Tool Name | Category | Rationale | URL |
|-----------|----------|-----------|-----|
| **Medidata Rave** | EDC / Data Capture | Leading EDC system for CRF data collection. CDOS integrates via the Rave Web Services API for real-time CRF data ingestion and ODM export. Supports CDASH-aligned CRFs. | https://www.medidata.com |
| **Argus Safety** | Pharmacovigilance / Safety | Oracle's safety database for SAE/SUSAR processing and ICSR generation. CDOS Safety Adapter interfaces with Argus via its API for automated adverse event reporting. | https://www.oracle.com/health-sciences/safety/ |
| **Apache NiFi** | Data Integration | Visual data flow orchestration for complex integration scenarios. Routes and transforms data between clinical systems with guaranteed delivery, back-pressure handling, and data provenance tracking. | https://nifi.apache.org |
| **Redis** | Caching / Session Store | In-memory cache for frequently accessed reference data (controlled terminology lookups, study configuration, user sessions). Reduces database load for dashboard queries with sub-millisecond latency. | https://redis.io |

## Infrastructure & Security Tools

| Tool Name | Category | Rationale | URL |
|-----------|----------|-----------|-----|
| **HashiCorp Vault** | Secrets Management / Encryption | Manages encryption keys, database credentials, and API tokens. Supports field-level encryption for PHI/PII via transit secrets engine. HSM integration for key rotation satisfies 21 CFR Part 11 requirements. | https://www.vaultproject.io |
| **Keycloak** | Identity & Access Management | OAuth2/OIDC identity provider with RBAC for clinical roles (CRA, Data Manager, Biostatistician, Medical Monitor). Supports LDAP/AD federation for enterprise SSO and multi-factor authentication. | https://www.keycloak.org |
| **OpenTelemetry** | Observability | Vendor-neutral distributed tracing, metrics, and logging standard. Provides end-to-end data lineage tracking from EDC ingestion through SDTM generation. Integrates with Grafana for visualization. | https://opentelemetry.io |
| **Grafana** | Monitoring & Visualization | Dashboard platform for system health, SLA monitoring, and operational metrics. Displays pipeline throughput, error rates, adapter latency, and data quality scores. Alerting via PagerDuty/email for SLA breaches. | https://grafana.com |
| **HashiCorp Terraform** | Infrastructure as Code | Declarative infrastructure provisioning for all CDOS components. Ensures reproducible, auditable deployments across development, staging, and production environments. State locking prevents configuration drift. | https://www.terraform.io |
| **Velero** | Backup & Disaster Recovery | Kubernetes-native backup and restore. Scheduled backups of PostgreSQL (via WAL-G), Kafka topics, and Vault secrets. Supports cross-region replication for disaster recovery with RPO < 1 hour. | https://velero.io |

---

## Tool Count Summary

| Category | Count | Tools |
|----------|-------|-------|
| Core Platform | 7 | PostgreSQL, Kafka, Kubernetes, PostgREST, Hasura, Camunda, Airflow |
| CDISC & Clinical | 6 | Pinnacle 21, SAS, R, ODM Study Designer, PhUSE Define-XML Tools, admiral |
| Integration & Data Quality | 4 | Medidata Rave, Argus Safety, Apache NiFi, Redis |
| Infrastructure & Security | 6 | Vault, Keycloak, OpenTelemetry, Grafana, Terraform, Velero |
| **Total** | **23** | |

---

## Cross-Reference: Tools by Architecture Layer

| Architecture Layer | Tools Used |
|-------------------|-----------|
| Presentation | Hasura (GraphQL), Grafana (dashboards) |
| Orchestration | Camunda (workflow), Kafka (events), Airflow (ETL) |
| Data | PostgreSQL (store), Redis (cache), admiral (ADaM), SAS (analysis), R (analysis) |
| Integration | Medidata Rave (EDC), Argus Safety (safety), Apache NiFi (routing), Pinnacle 21 (validation) |
| Infrastructure | Vault (encryption), Keycloak (IAM), OpenTelemetry (observability), Terraform (IaC), Velero (backup) |

---

## CDISC Tool Chain

The following diagram shows the CDISC-specific tool chain within the Transformation Pipeline:

```
Raw EDC Data (Medidata Rave)
        │
        ▼
  CDASH Mapping (CDOS CDISC Mapping Service)
        │
        ▼
  SDTM Generation (R/haven + SAS)
        │
        ▼
  SDTM Validation (Pinnacle 21) ──▶ Validation Report
        │
        ▼
  Define-XML Generation (ODM Study Designer / PhUSE Tools)
        │
        ▼
  ADaM Derivation (R/admiral + SAS)
        │
        ▼
  ADaM Validation (Pinnacle 21) ──▶ Validation Report
        │
        ▼
  Submission Package (eCTD assembly via Submission Builder)
```

---

## Version Pinning Strategy

All tools are pinned to specific major.minor versions in the Terraform configuration. Patch versions are auto-updated within the same minor version line. Major version upgrades require change control approval per [07-compliance](../07-compliance/) GxP validation requirements.

| Tool | Pinned Version | Update Policy |
|------|---------------|---------------|
| PostgreSQL | 16.x | Patch auto, minor quarterly |
| Kafka | 3.7.x | Patch auto, minor quarterly |
| Kubernetes | 1.30.x | Patch auto, minor via change control |
| Pinnacle 21 | Latest enterprise | Quarterly with CDISC CT updates |
| SAS | 9.4M8 / Viya 4 | Annual with validation |
| R | 4.4.x | Patch auto, minor with package testing |

---

## Related Modules

| Module | Tools Referenced |
|--------|-----------------|
| [03-transformations](../03-transformations/) | SAS, R, admiral, Pinnacle 21, Airflow |
| [04-integrations](../04-integrations/) | Medidata Rave, Argus Safety, Kafka, NiFi |
| [07-compliance](../07-compliance/) | Vault, Keycloak, PostgreSQL, OpenTelemetry |
| [08-implementation](../08-implementation/) | All tools (phased rollout plan) |
