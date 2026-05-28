# API Contracts — Unified Cross-Reference

This document provides a unified view of all system adapters in the CDOS integration layer. It cross-references every adapter, its endpoints, events, and canonical entity dependencies.

## Adapter Summary

| # | Adapter | File | Category | Real Products | Entity Dependencies |
|---|---------|------|----------|---------------|---------------------|
| 1 | [System:EDC] | edc-adapter.md | Data Capture | Medidata Rave, Oracle InForm, Veeva Vault CDMS, Castor | [Entity:Subject], [Entity:CRFPage], [Entity:Query], [Entity:AdverseEvent], [Entity:Visit], [Entity:Study], [Entity:Site] |
| 2 | [System:CTMS] | ctms-adapter.md | Trial Management | Oracle Siebel CTMS, Medidata CTMS, Veeva Vault CTMS | [Entity:Study], [Entity:Site], [Entity:Investigator], [Entity:Protocol] |
| 3 | [System:LIMS] | lims-adapter.md | Laboratory | Medidata Rave Lab, Covance LIMS, ICON LIMS | [Entity:Sample], [Entity:LabResult], [Entity:Subject], [Entity:Study] |
| 4 | [System:Safety] | safety-adapter.md | Pharmacovigilance | Argus Safety, ArisGlobal, Oracle AERS | [Entity:AdverseEvent], [Entity:Subject], [Entity:Study], [Entity:Submission] |
| 5 | [System:IWRS] | iwrs-adapter.md | Randomization | Signant Health, 4G Clinical, Medidata RTSM | [Entity:Subject], [Entity:Dose], [Entity:Study], [Entity:Site], [Entity:Visit] |
| 6 | [System:eCOA] | ecoa-adapter.md | Outcomes | ERT, Clario, Medidata Patient Cloud | [Entity:Subject], [Entity:Visit], [Entity:Study], [Entity:CRFPage] |
| 7 | [System:Imaging] | imaging-adapter.md | Medical Imaging | BioClinica, Parexel Imaging, Medidata Imaging | [Entity:Subject], [Entity:Visit], [Entity:Study], [Entity:CRFPage] |
| 8 | [System:Wearables] | wearables-adapter.md | IoT/Sensors | ActiGraph, Verily, Apple HealthKit | [Entity:Subject], [Entity:Study], [Entity:Visit], [Entity:CRFPage], [Entity:LabResult] |

## Endpoint Cross-Reference

### By HTTP Method

| Method | EDC | CTMS | LIMS | Safety | IWRS | eCOA | Imaging | Wearables | Total |
|--------|-----|------|------|--------|------|------|---------|-----------|-------|
| GET | 5 | 6 | 5 | 5 | 5 | 5 | 5 | 5 | 41 |
| POST | 3 | 2 | 3 | 4 | 4 | 3 | 3 | 3 | 25 |
| PUT | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 6 |
| PATCH | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 4 |
| **Total** | **10** | **9** | **10** | **10** | **10** | **9** | **9** | **9** | **76** |

### By Canonical Entity

| Entity | EDC | CTMS | LIMS | Safety | IWRS | eCOA | Imaging | Wearables | Adapters Count |
|--------|-----|------|------|--------|------|------|---------|-----------|----------------|
| [Entity:Study] | R | RW | R | R | R | R | R | R | 8 |
| [Entity:Subject] | RW | — | R | R | RW | R | R | R | 7 |
| [Entity:Site] | R | RW | — | — | R | — | — | — | 3 |
| [Entity:Visit] | RW | — | — | — | R | R | R | R | 5 |
| [Entity:AdverseEvent] | RW | — | — | RW | — | — | — | — | 2 |
| [Entity:CRFPage] | RW | — | — | — | — | W | W | W | 4 |
| [Entity:Query] | RW | — | — | — | — | — | — | — | 1 |
| [Entity:LabResult] | — | — | RW | — | — | — | — | W | 2 |
| [Entity:Sample] | — | — | RW | — | — | — | — | — | 1 |
| [Entity:Investigator] | — | RW | — | — | — | — | — | — | 1 |
| [Entity:Protocol] | — | RW | — | — | — | — | — | — | 1 |
| [Entity:Dose] | — | — | — | — | RW | — | — | — | 1 |
| [Entity:Submission] | — | — | — | RW | — | — | — | — | 1 |

*R = read-only, W = write, RW = read-write*

## Event Flow Cross-Reference

### All Events by Producer

| Producer | Event Count | Events |
|----------|-------------|--------|
| EDC | 8 | subject.enrolled, crfpage.submitted, query.raised, query.resolved, ae.reported, visit.completed, data.changed, study.locked |
| CTMS | 8 | study.created, study.updated, site.activated, site.deactivated, investigator.added, protocol.amended, enrollment.milestone, monitoring.visit-scheduled |
| LIMS | 7 | sample.received, sample.rejected, lab-result.released, lab-result.critical, kit.shipped, kit.depleted, reference-range.updated |
| Safety | 7 | case.created, case.updated, sae.detected, susar.detected, icsr.submitted, icsr.acknowledged, signal.detected |
| IWRS | 8 | subject.randomized, kit.assigned, kit.returned, supply.low-stock, supply.resupply-triggered, dose-escalation.decision, unblinding.requested, unblinding.executed |
| eCOA | 7 | assessment.completed, assessment.missed, response.submitted, compliance.alert, device.provisioned, device.returned, instrument.validated |
| Imaging | 7 | image.uploaded, image.qc-passed, image.qc-failed, reading.completed, reading.discrepancy, response.assessed, reader.assigned |
| Wearables | 7 | data.received, biomarker.derived, device.provisioned, device.returned, compliance.alert, alert.triggered, data.quality-issue |
| **Total** | **59** | |

### All Events by Consumer

| Consumer | Event Count | Key Incoming Events |
|----------|-------------|---------------------|
| CTMS | 35 | subject.enrolled, ae.reported, query.raised/resolved, visit.completed, study.locked (from EDC); all LIMS events; all Safety events; all IWRS events; all eCOA events; all Imaging events; all Wearables events |
| EDC | 22 | study.created/updated, site.activated, investigator.added, protocol.amended (from CTMS); sample.received/rejected, lab-result.released/critical (from LIMS); sae.detected (from Safety); subject.randomized, kit.assigned, dose-escalation.decision, unblinding.executed (from IWRS); assessment.completed, response.submitted (from eCOA); reading.completed, response.assessed (from Imaging); data.received, biomarker.derived (from Wearables) |
| Safety | 3 | ae.reported (from EDC); lab-result.critical (from LIMS); alert.triggered (from Wearables) |
| LIMS | 3 | crfpage.submitted, visit.completed (from EDC); study.created/updated, site.activated, protocol.amended (from CTMS); kit.shipped (from IWRS) |
| IWRS | 4 | subject.enrolled, visit.completed (from EDC); study.created/updated, site.activated/deactivated, protocol.amended (from CTMS) |
| RegSubmit | 2 | study.locked (from EDC); susar.detected (from Safety) |
| eTMF | 1 | study.updated (from CTMS) |
| Wearables | 0 | — (provides data, does not consume events) |
| eCOA | 1 | subject.enrolled (from EDC) |
| Imaging | 0 | — (provides data, does not consume events) |

### Critical Event Paths

| Path | Latency Requirement | Systems Involved |
|------|---------------------|------------------|
| AE Reporting Chain | < 15 min | EDC → Safety → RegSubmit |
| SUSAR Reporting | < 72 hours | EDC → Safety → RegSubmit |
| Critical Lab Result | < 1 min | LIMS → Safety, EDC |
| Randomization | < 5s (real-time) | EDC → IWRS → EDC, CTMS |
| Unblinding | < 1 min (real-time) | IWRS → CTMS, EDC |

## Authentication Summary

| Auth Method | All Adapters |
|-------------|--------------|
| Protocol | OAuth 2.0 with JWT Bearer tokens |
| Token Issuer | Central Identity Provider (IdP) |
| Token Lifetime | 1 hour (access), 24 hours (refresh) |
| Scope Model | Per-adapter scopes: `edc:read`, `edc:write`, `ctms:read`, etc. |
| MFA | Required for Safety unblinding, IWRS unblinding endpoints |
| API Key | Not used — OAuth2 only for audit compliance (21 CFR Part 11) |

## Error Handling Summary

| Policy | Value (All Adapters) |
|--------|----------------------|
| Retry Attempts | 3 |
| Backoff Strategy | Exponential: 1s, 5s, 25s |
| Dead Letter Queue | `dlq.<system-name>` |
| Circuit Breaker Threshold | 5 failures in 60s |
| Circuit Breaker Open Duration | 30s |
| Circuit Breaker Recovery | Half-open → 3 consecutive successes → close |
| API Timeout | 30s (standard), 60s (batch), 120s (large file upload) |
| Event Publish Timeout | 10s |
| Idempotency | All write endpoints accept `Idempotency-Key` header |

## SLA Summary

| Metric | Standard Adapters | Elevated Adapters |
|--------|-------------------|-------------------|
| **Latency (API p99)** | < 500ms | < 1s (IWRS randomization), < 30s (Imaging DICOM) |
| **Latency (Events p99)** | < 5s | < 1s (Safety SAE/SUSAR, LIMS critical, IWRS randomization) |
| **Availability** | 99.9% (≤8.76h/yr) | 99.95% (≤4.38h/yr) — Safety, IWRS |
| **RPO** | 0 (zero data loss) | 0 (all adapters) |
| **RTO** | < 15 min | < 10 min — Safety, IWRS |

## Cross-Module Dependencies

### Module 02 (Data Models) → Module 04 (Integrations)

All adapters reference canonical entities defined in `02-data-models/canonical/`. The entity JSON schemas serve as the request/response contract for API endpoints. Any schema change in module 02 triggers adapter contract review.

### Module 03 (Transformations) → Module 04 (Integrations)

Transforms in module 03 consume events from adapters and produce data for downstream systems. Key integration points:
- `edc-to-sdtm` consumes EDC events and produces SDTM datasets
- `sae-to-icsr` consumes Safety SAE events and produces ICSR submissions
- `lab-to-sdtm` consumes LIMS events and produces LB domain datasets

### Module 05 (Trial Designs) → Module 04 (Integrations)

Trial design variants may require adapter configuration changes:
- Adaptive trials: IWRS dose-escalation endpoints active
- Platform trials: CTMS multi-arm support required
- RWE studies: Wearables and eCOA adapters primary data source

### Module 06 (Risk Models) → Module 04 (Integrations)

Risk models monitor adapter health and data quality:
- Enrollment risk: CTMS enrollment events + IWRS randomization events
- Data quality risk: EDC query events + LIMS lab-result events
- Supply chain risk: IWRS supply events + LIMS kit events

### Module 07 (Compliance) → Module 04 (Integrations)

All adapters implement:
- 21 CFR Part 11: Audit trail on all endpoints, e-signature support for unblinding
- GDPR: Data minimization in event payloads, pseudonymized subject identifiers
- GxP: Validated endpoints per GAMP 5 Category 4/5
