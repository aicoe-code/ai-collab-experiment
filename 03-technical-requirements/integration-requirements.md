# CDOS Integration Requirements

**Document Version:** 1.0
**Author:** Agent-TR
**Last Updated:** 2026-05-29

This document specifies the technical integration requirements for each external system
connected to the CDOS platform. Integration pattern names follow the canonical system
names defined in `ALIGNMENT_RULES.md` (Section 3).

Each integration specifies: protocol, authentication, data format, data direction,
frequency, SLA, and error handling.

---

## Integration Overview

| # | System | Category | Direction | Priority |
|---|--------|----------|-----------|----------|
| 1 | EDC | Data Capture | Bidirectional | Critical |
| 2 | CTMS | Trial Management | Bidirectional | Critical |
| 3 | LIMS | Laboratory | Inbound | High |
| 4 | Safety | Pharmacovigilance | Bidirectional | Critical |
| 5 | IWRS | Randomization | Bidirectional | Critical |
| 6 | eCOA | Outcomes | Inbound | High |
| 7 | Imaging | Medical Imaging | Inbound | Medium |
| 8 | Wearables | IoT/Sensors | Inbound | Medium |

---

## 1. EDC (Electronic Data Capture)

### TR-I01: EDC Integration

| Attribute | Specification |
|-----------|--------------|
| **System** | EDC (Medidata Rave, Oracle InForm, Veeva Vault CDMS, Castor) |
| **Protocol** | REST API (primary) / SFTP + flat file (fallback for batch) |
| **Authentication** | OAuth 2.0 Client Credentials Grant; API key as secondary factor |
| **Data Format** | JSON (REST); CDISC ODM v2.0 XML (batch export); CDASH v2.1 field mapping |
| **Direction** | Bidirectional |
| **Frequency** | Near real-time (event-driven via webhooks, 5-minute polling fallback); Batch: nightly full extract |
| **Data Elements** | CRFPage (crf), Query (query), Subject (subj) demographics, Visit (visit) schedule |
| **Volume** | Up to 500,000 CRF pages per study; 10,000 query exchanges per study |
| **SLA** | API availability: 99.5%; Data sync latency: < 15 minutes (real-time), < 4 hours (batch) |
| **Error Handling** | Dead letter queue for failed transforms; automatic retry (3 attempts, exponential backoff); alert on failure after retries exhausted |
| **CDISC Mapping** | CDASH v2.1 -> CDOS Canonical -> SDTM v3.4 (DM, AE, LB, CM, EX domains) |

---

## 2. CTMS (Clinical Trial Management System)

### TR-I02: CTMS Integration

| Attribute | Specification |
|-----------|--------------|
| **System** | CTMS (Oracle Siebel CTMS, Medidata CTMS, Veeva Vault CTMS) |
| **Protocol** | REST API (primary) / SOAP (legacy systems) |
| **Authentication** | OAuth 2.0 Authorization Code Grant (user-context operations); Client Credentials (system operations) |
| **Data Format** | JSON (REST); XML (SOAP); CDISC ODM v2.0 for study metadata |
| **Direction** | Bidirectional |
| **Frequency** | Real-time event-driven for study/site/subject status changes; Batch: daily reconciliation |
| **Data Elements** | Study (study), Site (site), Investigator (inv), Visit (visit) schedule, Subject (subj) enrollment status, Protocol (proto) amendments |
| **Volume** | Up to 500 active studies; 50,000 sites; 500,000 subjects |
| **SLA** | API availability: 99.5%; Status sync latency: < 5 minutes (real-time), < 1 hour (batch) |
| **Error Handling** | Conflict resolution: CTMS is source-of-truth for study/site metadata; CDOS is source-of-truth for clinical data. Conflict logged and escalated to data manager. |
| **CDISC Mapping** | Study metadata aligned with ODM v2.0 Study protocol definition |

---

## 3. LIMS (Laboratory Information Management System)

### TR-I03: LIMS Integration

| Attribute | Specification |
|-----------|--------------|
| **System** | LIMS (Medidata Rave Lab, Covance LIMS, ICON LIMS) |
| **Protocol** | HL7 v2.5.1 (primary for lab results) / REST API (for metadata and queries) / SFTP + flat file (batch) |
| **Authentication** | TLS mutual authentication (client certificates) for HL7; OAuth 2.0 Client Credentials for REST API |
| **Data Format** | HL7 v2.5.1 ORM/ORU messages (lab results); JSON (REST); CSV (batch flat file) |
| **Direction** | Inbound to CDOS |
| **Frequency** | Near real-time (HL7 message per lab result); Batch: daily for reference ranges and normal values |
| **Data Elements** | LabResult (lab), Sample (sample), reference ranges, normal flags, lab panel definitions |
| **Volume** | Up to 2,000,000 lab results per study; 500,000 samples per study |
| **SLA** | Message delivery: 99.9% (no lost results); Processing latency: < 30 minutes from receipt |
| **Error Handling** | HL7 ACK/NAK protocol; unparseable messages quarantined with manual review workflow; duplicate detection via message control ID |
| **CDISC Mapping** | Lab results mapped to SDTM LB (Lab) domain; CDISC controlled terminology for lab test codes (LBTESTCD) |

---

## 4. Safety (Pharmacovigilance System)

### TR-I04: Safety Integration

| Attribute | Specification |
|-----------|--------------|
| **System** | Safety (Argus Safety, ArisGlobal, Oracle AERS) |
| **Protocol** | REST API (primary) / ICSR E2B(R3) XML exchange (regulatory) |
| **Authentication** | OAuth 2.0 Client Credentials; digital signature on ICSR submissions (XML-DSig) |
| **Data Format** | JSON (REST API); ICSR E2B(R3) XML (Individual Case Safety Reports); MedDRA coding (current version) |
| **Direction** | Bidirectional |
| **Frequency** | Real-time for SAE (Serious Adverse Event) and SUSAR (Suspected Unexpected Serious Adverse Reaction) notifications; Batch: weekly safety data reconciliation |
| **Data Elements** | AdverseEvent (ae), SAE classification, SUSAR assessment, causality assessment, MedDRA preferred terms, Reporter information |
| **Volume** | Up to 100,000 AEs per study; 10,000 SAEs per study; ICSR submissions per regulatory timelines |
| **SLA** | SAE notification latency: < 1 hour from data entry; SUSAR notification: < 24 hours; ICSR submission: per regulatory timeline (7-day, 15-day) |
| **Error Handling** | Critical priority: SAE/SUSAR failures trigger immediate alert (PagerDuty P1); MedDRA coding failures queued for manual review; ICSR rejection triggers re-submission workflow |
| **CDISC Mapping** | Adverse events mapped to SDTM AE domain; concomitant medications to CM domain; MedDRA coding aligned with SDTM AEDECOD, AEBODSYS |

---

## 5. IWRS (Interactive Web Response System)

### TR-I05: IWRS Integration

| Attribute | Specification |
|-----------|--------------|
| **System** | IWRS (Signant Health, 4G Clinical, Medidata RTSM) |
| **Protocol** | REST API (primary) / SOAP (legacy) |
| **Authentication** | OAuth 2.0 Client Credentials; mutual TLS for production |
| **Data Format** | JSON (REST); XML (SOAP) |
| **Direction** | Bidirectional |
| **Frequency** | Real-time (synchronous request-response for randomization and drug assignment) |
| **Data Elements** | Subject (subj) randomization, Dose (dose) assignment, kit numbers, drug supply levels, stratification factors, unblinding requests |
| **Volume** | Up to 500,000 randomization events across all studies; 100 concurrent randomization requests |
| **SLA** | API response time: < 3 seconds for randomization request; Availability: 99.99% during business hours; No data loss tolerance |
| **Error Handling** | Synchronous: timeout after 10 seconds triggers retry (max 3); after 3 failures, alert to clinical operations; randomization data never lost (idempotent retry with same request ID) |
| **CDISC Mapping** | Randomization data mapped to SDTM DM (Demographics: ARM, ARMCD); exposure data to SDTM EX domain |

---

## 6. eCOA (Electronic Clinical Outcome Assessments)

### TR-I06: eCOA Integration

| Attribute | Specification |
|-----------|--------------|
| **System** | eCOA (ERT, Clario, Medidata Patient Cloud) |
| **Protocol** | REST API (primary) / SFTP + flat file (batch) |
| **Authentication** | OAuth 2.0 Client Credentials; API key rotation every 90 days |
| **Data Format** | JSON (REST); CDISC ODM v2.0 XML (instrument definitions); CSV (batch data export) |
| **Direction** | Inbound to CDOS |
| **Frequency** | Near real-time (event-driven on assessment completion); Batch: daily for instrument metadata and scoring algorithms |
| **Data Elements** | Patient-reported outcomes (PRO), clinician-reported outcomes (ClinRO), instrument scores, completion timestamps, compliance metrics |
| **Volume** | Up to 1,000,000 assessment records per study; 10,000 subjects submitting assessments |
| **SLA** | Data availability: < 1 hour from patient submission; Processing: < 2 hours from receipt |
| **Error Handling** | Assessment data queued for retry on failure (max 3 attempts); scoring algorithm version mismatches flagged for review; missing assessments trigger reminder workflow |
| **CDISC Mapping** | Assessment data mapped to SDTM QS (Questionnaire), FT (Function Tests) domains; controlled terminology per CDISC CT |

---

## 7. Imaging (Medical Imaging System)

### TR-I07: Imaging Integration

| Attribute | Specification |
|-----------|--------------|
| **System** | Imaging (BioClinica, Parexel Imaging) |
| **Protocol** | DICOM (image transfer) / DICOMweb WADO-RS (image retrieval) / REST API (metadata and reads) |
| **Authentication** | OAuth 2.0 Client Credentials for REST API; TLS with client certificates for DICOM node communication |
| **Data Format** | DICOM (images); JSON (reads, assessments, metadata); DICOM SR (Structured Reports for assessments) |
| **Direction** | Inbound to CDOS |
| **Frequency** | Batch: image upload within 24 hours of acquisition; Reads/assessments: event-driven on read completion |
| **Data Elements** | Image metadata (modality, body part, acquisition date), reader assessments, measurements, response criteria (RECIST, irRECIST), image links (not stored in CDOS — stored in Imaging system) |
| **Volume** | Up to 100,000 image metadata records per study; 50,000 reads per study |
| **SLA** | Metadata sync: < 24 hours from upload; Read sync: < 4 hours from read completion; Image retrieval via DICOMweb: < 10 seconds per image |
| **Error Handling** | DICOM metadata parsing failures quarantined; orphaned reads (no matching image) flagged; retry on DICOMweb timeout (max 3 attempts) |
| **CDISC Mapping** | Image assessments mapped to SDTM RS (Results) domain; RECIST measurements to custom SDTM supplemental qualifiers |

---

## 8. Wearables (IoT/Sensor Platform)

### TR-I08: Wearables Integration

| Attribute | Specification |
|-----------|--------------|
| **System** | Wearables (ActiGraph, Verily, Apple HealthKit) |
| **Protocol** | REST API (primary) / MQTT (real-time sensor data streams) / SFTP + flat file (batch) |
| **Authentication** | OAuth 2.0 Client Credentials (device-to-cloud); Per-device API keys with rotation; TLS 1.3 |
| **Data Format** | JSON (REST); Protocol Buffers (MQTT high-frequency data); CSV (batch exports) |
| **Direction** | Inbound to CDOS |
| **Frequency** | Real-time (MQTT for continuous monitoring: heart rate, activity); Batch: daily aggregated summaries (step count, sleep metrics) |
| **Data Elements** | Vital signs (heart rate, blood pressure, SpO2), activity data (steps, distance, calories), sleep metrics, device compliance (wearing time), alerts (threshold breaches) |
| **Volume** | Up to 10,000 subjects with devices; 1,000 data points per subject per day; ~10M data points per day at scale |
| **SLA** | Real-time data availability: < 5 minutes from device transmission; Daily aggregation: available by 06:00 UTC next day; Data completeness: > 95% expected readings received |
| **Error Handling** | MQTT QoS level 1 (at least once delivery); duplicate detection via device_id + timestamp; device disconnection alerts after 24 hours of no data; data quality checks (outlier detection, range validation) |
| **CDISC Mapping** | Vital signs mapped to SDTM VS domain; device data to custom SDTM supplemental qualifiers; activity data to custom domains per study protocol |

---

## Integration Architecture Summary

### Common Integration Patterns

| Pattern | Implementation |
|---------|---------------|
| **Adapter Pattern** | Each external system has a dedicated adapter class implementing `BaseAdapter` interface (see `ALIGNMENT_RULES.md` Section 5c) |
| **Event-Driven** | Kafka topics per integration: `edc.events`, `ctms.events`, `lims.events`, `safety.events`, `iwrs.events`, `ecoa.events`, `imaging.events`, `wearables.events` |
| **Dead Letter Queue** | Failed messages routed to `*.dlq` topics for manual review |
| **Idempotency** | All inbound integrations use source_system + source_record_id as idempotency key |
| **Circuit Breaker** | Circuit breaker pattern on all outbound API calls (failure threshold: 5 consecutive failures, reset timeout: 60 seconds) |
| **Schema Validation** | Inbound data validated against JSON Schema or HL7 message profile before processing |

### Integration SLA Summary

| System | Availability | Latency | Error Rate |
|--------|-------------|---------|------------|
| EDC | 99.5% | < 15 min (real-time) | < 0.1% |
| CTMS | 99.5% | < 5 min (real-time) | < 0.1% |
| LIMS | 99.9% | < 30 min | < 0.05% |
| Safety | 99.9% | < 1 hour (SAE) | 0% (no lost SAEs) |
| IWRS | 99.99% | < 3 sec | 0% (no lost randomizations) |
| eCOA | 99.5% | < 1 hour | < 0.1% |
| Imaging | 99.0% | < 24 hours | < 0.5% |
| Wearables | 99.0% | < 5 min (real-time) | < 1% |

### Error Handling Summary

| Severity | Response Time | Action |
|----------|-------------|--------|
| P1 - Critical (Safety/IWRS failure) | < 15 min | PagerDuty alert, war room |
| P2 - High (EDC/CTMS sync failure) | < 1 hour | Alert, automatic retry |
| P3 - Medium (LIMS/eCOA delay) | < 4 hours | Alert, queue for retry |
| P4 - Low (Imaging/Wearables delay) | < 24 hours | Log, batch retry |
