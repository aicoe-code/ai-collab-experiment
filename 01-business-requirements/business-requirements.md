# CDOS Business Requirements

This document defines the business requirements for the Clinical Development Operating System (CDOS).
Each requirement follows the 12-section template defined in BR_TEMPLATE.md.

**Priority Legend:**
- **P0 — Critical**: Must be in initial release; trial operations cannot function without it.
- **P1 — High**: Required for core value proposition; targeted for initial release.
- **P2 — Medium**: Important for full adoption; planned for release 2.
- **P3 — Low**: Nice-to-have; future roadmap.

---

# Business Requirements: BR-001 through BR-003

---

## BR-001: Unified Data Ingestion from EDC Systems

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-001 |
| **Title** | Unified Data Ingestion from EDC Systems |
| **Priority** | P0 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-001, SN-006, SN-007 |
| **Regulatory Basis** | 21 CFR Part 11, ICH E6(R2), CDISC SDTM v3.4 |
| **Status** | Draft |

### 2. Business Rationale

Clinical trials today are executed across a fragmented landscape of Electronic Data Capture (EDC) systems — Medidata Rave, Oracle InForm, Veeva Vault CDMS, and Castor are each used by different CROs and sponsors. Data managers currently spend 6–8 weeks per study manually reconciling and transforming EDC exports into a unified format for analysis, costing sponsors an estimated $150K–$300K per study in labor and delay. Without a unified ingestion layer, sponsors cannot achieve a single-pane-of-glass view of their trial portfolio (SN-001), and CROs are forced to build custom point-to-point integrations for every new sponsor engagement (SN-006). This fragmentation also prevents timely access to clean, analysis-ready data (SN-007), directly impacting database lock timelines and regulatory submission readiness.

### 3. Detailed Description

The CDOS shall provide a unified data ingestion service that connects to all major EDC platforms — Medidata Rave, Oracle InForm, Veeva Vault CDMS, and Castor — and extracts clinical data in near real-time. When a data change is committed in any connected EDC system, the ingestion service detects the change (via webhooks, API polling, or event streams depending on the EDC vendor) and retrieves the updated record. The service then normalizes the heterogeneous EDC data into the CDOS canonical model, specifically the Subject-Visit-CRFPage hierarchy, which serves as the universal representation across all studies. Each EDC adapter translates vendor-specific field names, controlled terminologies, and data types into the canonical schema, preserving original values alongside normalized values for auditability. The normalization process includes mapping CDASH-aligned CRF fields to their canonical equivalents and resolving cross-system subject identifiers using a master subject index. The service supports both initial bulk loads (for historical data migration) and incremental delta loads (for ongoing synchronization). All ingested data is written to the CDOS data store with full provenance metadata, including the source EDC system, extraction timestamp, and source record identifier. The service operates with at-least-once delivery semantics and provides idempotent write operations to ensure data integrity even in the event of retries or partial failures. Study administrators can configure ingestion schedules, field-level mapping overrides, and data quality rules through a metadata-driven configuration interface without requiring code changes.

### 4. Preconditions

- [ ] At least one EDC system (Medidata Rave, Oracle InForm, Veeva Vault CDMS, or Castor) is provisioned with API credentials and connectivity verified.
- [ ] A CDOS Study has been created with the canonical Subject-Visit-CRFPage metadata model defined (study protocol, visit schedule, CRF page definitions).
- [ ] The EDC-to-canonical field mapping configuration has been completed and validated for the target study.

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-001-AC01 | Single-subject ingestion from Medidata Rave | A subject is enrolled in Medidata Rave with visit data recorded on 3 CRF pages | The ingestion service processes the delta load for that subject | Subject, Visit, and CRFPage records are created in the CDOS canonical store with correct field values and provenance metadata |
| BR-001-AC02 | Cross-EDC normalization consistency | Two different studies capture the same clinical data point (e.g., vital signs) — one in Oracle InForm, one in Veeva Vault CDMS | Both datasets are ingested and normalized | The canonical CRFPage representation is structurally identical for both, with vendor-specific field names mapped to the same canonical fields |
| BR-001-AC03 | Idempotent re-ingestion | A CRFPage record has already been ingested from Castor | The same record is re-ingested due to a retry or reprocessing event | No duplicate records are created; the existing record is updated only if the source data has changed (based on source timestamp comparison) |
| BR-001-AC04 | EDC connectivity failure resilience | The Medidata Rave API is temporarily unavailable | The ingestion service attempts a scheduled delta load | The service retries with exponential backoff, logs the failure, raises an alert, and resumes ingestion automatically when connectivity is restored without data loss |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-002 | Related | Laboratory data from LIMS complements EDC-captured data; both must feed the same canonical Subject-Visit model for completeness |
| BR-003 | Related | IWRS/RTSM subject assignment data must be synchronized with EDC-ingested subject records to maintain a unified subject identity |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC (Medidata Rave) | Reads from | Extracts subject, visit, and CRF page data via Rave API / ODM feeds |
| EDC (Oracle InForm) | Reads from | Extracts clinical data via InForm web services |
| EDC (Veeva Vault CDMS) | Reads from | Extracts data via Vault REST API |
| EDC (Castor) | Reads from | Extracts data via Castor API |
| CDOS Canonical Data Store | Writes to | Writes normalized Subject, Visit, CRFPage records |
| CDOS Event Bus | Publishes to | Publishes `subject.data.ingested` events for downstream consumers |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Subject | Create, Read, Update | Subject demographic and enrollment data sourced from EDC |
| Visit | Create, Read, Update | Visit schedule and visit-level status from EDC |
| CRFPage | Create, Read, Update | Individual CRF page data (form fields, responses, audit trail) from EDC |
| Study | Read | Study metadata used for mapping configuration and validation |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A subject is enrolled in multiple EDC systems for the same study (e.g., mid-study EDC migration) | The system detects the duplicate via the master subject index and merges records, preserving full provenance from both sources. A reconciliation alert is raised for data manager review. |
| An EDC system returns data with a controlled terminology code not present in the CDOS canonical code list | The system ingests the record, flags the unmapped code as a data quality issue, stores the original value, and queues the mapping for manual resolution. Ingestion of other fields on the same record proceeds normally. |
| A study uses a non-standard CRF structure that does not map cleanly to the Subject-Visit-CRFPage model | The system allows study-specific override mappings configured via the metadata interface. If the override is insufficient, the record is ingested into a staging area with a "requires manual mapping" flag. |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Sponsors cannot achieve portfolio-level trial visibility, leading to delayed decision-making | High | High | Manual reconciliation via spreadsheets (not scalable) |
| CROs incur significant per-study integration costs, reducing margins and competitiveness | High | Medium | Maintain custom point-to-point integrations per sponsor (high ongoing cost) |
| Data quality issues are discovered late in the trial, delaying database lock by weeks | Medium | High | Implement downstream data cleaning scripts (reactive, not proactive) |

### 11. Assumptions

- All target EDC systems provide a documented API or data export mechanism (REST API, ODM XML, or SFTP-based extract) that the CDOS adapters can use.
- EDC vendors do not change their API contracts without advance notice; the CDOS adapter layer includes version detection and graceful degradation.
- The CDOS canonical model (Subject-Visit-CRFPage) is sufficient to represent data from all four target EDC systems without loss of clinical meaning.
- Network connectivity between the CDOS platform and EDC systems is available with acceptable latency (< 2s round-trip for API calls).

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | TBD | Pending |
| CRO | TBD | Pending |
| Site | TBD | Pending |

---

## BR-002: Laboratory Data Integration

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-002 |
| **Title** | Laboratory Data Integration |
| **Priority** | P0 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-007, SN-023 |
| **Regulatory Basis** | 21 CFR Part 11, CDISC SDTM v3.4 (LB domain), ICH E6(R2) |
| **Status** | Draft |

### 2. Business Rationale

Laboratory data is among the most critical and voluminous data types in clinical trials, accounting for approximately 40% of all CRF data points in a typical Phase III study. Today, lab results arrive from central and local laboratories in disparate formats — flat files, HL7 messages, and vendor-specific APIs — and must be manually reconciled against EDC-captured data, a process that takes 4–6 weeks per study and introduces significant error rates (estimated 5–8% discrepancy rate requiring manual review). Without automated LIMS integration, biostatisticians cannot access clean, CDISC SDTM LB-domain-ready data in a timely manner (SN-023), and data managers are forced into reactive query cycles rather than proactive data quality management. The CDOS must normalize laboratory data at ingestion, apply reference ranges, and link results to the canonical Subject-Visit model to ensure analysis-ready data is continuously available.

### 3. Detailed Description

The CDOS shall integrate with Laboratory Information Management Systems (LIMS) to ingest laboratory test results, normalize them to the CDISC SDTM LB (Laboratory) domain structure, and link them to the canonical Subject-Visit model. The integration supports multiple LIMS providers commonly used in clinical trials, including Medidata Rave Lab, Covance LIMS, and ICON LIMS, via configurable adapters. When a laboratory result is finalized or updated in the LIMS, the CDOS ingestion service detects the change and retrieves the result record, including the test name, result value, units, normal range (low and high), collection date/time, specimen identifier, and the performing laboratory. The service normalizes the result to the LB domain structure, mapping laboratory test names to LOINC codes and applying CDISC-controlled terminology for units and specimen types. Reference ranges are validated at ingestion: results outside the normal range are flagged with an abnormal indicator (A, B, N per SDTM conventions) and trigger configurable alerts for the data management team. Specimen tracking information is preserved, linking each LabResult to the originating Sample entity in the canonical model, which enables traceability from result back to the physical specimen. The service handles both central lab data (batch file uploads) and local lab data (entered via EDC CRF pages), reconciling the two sources when both exist for the same subject-visit-test combination. All laboratory data is stored with full provenance metadata, including the source LIMS, performing lab, and extraction timestamp.

### 4. Preconditions

- [ ] A CDOS Study has been created with the Subject-Visit model defined, and the study's laboratory schedule (expected tests per visit) has been configured.
- [ ] At least one LIMS system is provisioned with API credentials or file transfer connectivity verified, and the laboratory test catalog (test names, LOINC mappings, units) has been loaded into CDOS.
- [ ] Reference range tables (age-, sex-, and population-specific normal ranges) have been configured for each laboratory test in the study.

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-002-AC01 | Lab result ingestion and SDTM LB mapping | A central lab uploads a batch file containing 500 lab results for a study | The ingestion service processes the file | All 500 results are normalized to SDTM LB domain structure with LOINC codes, CDISC units, and linked to the correct Subject-Visit entities |
| BR-002-AC02 | Reference range validation and abnormal flagging | A subject's ALT result is 2x the upper limit of normal for their demographic group | The result is ingested | The LabResult record is created with LBSTRESN populated, abnormal indicator set to "A" (abnormal-high), and an alert is published to the data management team |
| BR-002-AC03 | Specimen traceability | A lab result references specimen ID "SP-00123" collected at Visit 3 | The result is ingested | The LabResult is linked to the canonical Sample entity with specimen ID "SP-00123", and the Sample status is updated to "Resulted" |
| BR-002-AC04 | Central-to-local lab reconciliation | A subject has a hemoglobin result from both the central lab and a local lab for the same visit | Both results are ingested | The system creates two LabResult records with distinct source identifiers, flags the discrepancy for data manager review, and presents both values in the reconciliation dashboard |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 | Related | EDC-ingested Subject and Visit records must exist before lab results can be linked to them; the canonical Subject-Visit model is shared |
| BR-003 | Related | Lab results may inform dosing decisions managed by IWRS/RTSM; consistent subject identity is required |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| LIMS (Medidata Rave Lab) | Reads from | Extracts lab results, specimen data, and reference ranges via API |
| LIMS (Covance LIMS) | Reads from | Extracts lab results via HL7 or flat file transfer |
| LIMS (ICON LIMS) | Reads from | Extracts lab results via API or SFTP |
| CDOS Canonical Data Store | Writes to | Writes normalized LabResult and Sample records |
| CDOS Event Bus | Publishes to | Publishes `lab.result.ingested` and `lab.result.abnormal` events |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| LabResult | Create, Read, Update | Laboratory test result mapped to SDTM LB domain (LBTESTCD, LBSTRESN, LBSTRESU, LBNRIND, etc.) |
| Sample | Create, Read, Update | Biological specimen tracking (specimen type, collection datetime, status) |
| Subject | Read | Subject demographic data used for reference range population selection |
| Visit | Read | Visit metadata used to link lab results to the correct study timepoint |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A lab result arrives for a subject-visit combination that does not exist in the CDOS canonical store (e.g., unscheduled visit, data entry error) | The system creates the LabResult in a staging area with a "subject-visit not found" flag and raises an alert. The result is not linked until the corresponding Subject-Visit record is resolved. |
| A LIMS batch file contains duplicate results for the same subject-visit-test (e.g., corrected result) | The system applies the latest result (by specimen collection datetime or result version number) and preserves the previous result as a superseded version with full audit trail. |
| Reference range tables are missing for a specific test or demographic subgroup | The system ingests the result without abnormal flagging, logs a "reference range missing" data quality issue, and alerts the data management team to configure the missing range. |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Biostatisticians receive lab data weeks after collection, delaying interim analyses and DSMB reviews | High | High | Manual SDTM LB mapping at database lock (delays submission by 4–8 weeks) |
| Discrepancies between central and local lab results go undetected until late-stage data cleaning | Medium | High | Manual cross-check by data managers (error-prone, not scalable) |
| Specimen-to-result traceability is lost, jeopardizing audit readiness | Medium | Medium | Maintain separate specimen tracking spreadsheet (fragile, not GxP-compliant) |

### 11. Assumptions

- LIMS vendors provide data export mechanisms (API, HL7, or flat file) that are documented and stable.
- LOINC codes are available for all laboratory tests used in the study, or the CDOS provides a configurable mapping table.
- Reference ranges are provided by the central laboratory and are population-specific (age, sex, and where applicable, race/ethnicity).
- The CDOS canonical LabResult entity can represent all SDTM LB domain variables required for regulatory submission.

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | TBD | Pending |
| CRO | TBD | Pending |
| Site | TBD | Pending |

---

## BR-003: IWRS/RTSM Integration

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-003 |
| **Title** | IWRS/RTSM Integration |
| **Priority** | P0 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-007, SN-001 |
| **Regulatory Basis** | 21 CFR Part 11, ICH E6(R2), ICH E9(R1) (Statistical Principles) |
| **Status** | Draft |

### 2. Business Rationale

Randomization and treatment assignment are the foundational processes of a controlled clinical trial, and the Interactive Web Response System (IWRS) / Randomization and Trial Supply Management (RTSM) is the system of record for these critical decisions. Today, subject randomization data lives in siloed IWRS/RTSM systems (Signant Health, 4G Clinical, Medidata RTSM) and is often reconciled manually with EDC subject records — a process that takes 2–3 weeks per study and carries the risk of mismatched subject assignments. Sponsors require a unified view of each subject's treatment arm, kit assignments, and randomization strata alongside their clinical data (SN-001), and CROs need automated ingestion of IWRS/RTSM data to eliminate manual reconciliation (SN-007). Without this integration, there is a material risk of treatment assignment errors, unblinding events, and regulatory findings during inspection.

### 3. Detailed Description

The CDOS shall integrate with IWRS/RTSM systems to ingest randomization events, treatment assignments, kit dispensation records, and subject stratification factors in real-time or near real-time. The integration supports the major IWRS/RTSM platforms — Signant Health, 4G Clinical, and Medidata RTSM — via configurable adapters that connect to each vendor's API or event stream. When a subject is randomized in the IWRS/RTSM, the CDOS ingestion service captures the randomization event, including the subject identifier, randomization number, treatment arm assignment, stratification factors (e.g., disease severity, region), and the timestamp of the randomization. The service creates or updates the Subject entity in the canonical store, linking the IWRS subject identifier to the CDOS master subject index that already contains identifiers from the EDC system. Kit management data is also ingested: when kits are dispensed, returned, or destroyed, the CDOS records the kit number, medication type, lot number, and dispensation status against the Subject and Visit entities. The integration supports both open-label and blinded trial designs; for blinded studies, treatment arm assignments are stored in an access-controlled partition of the data store with role-based visibility. The service publishes events when critical IWRS/RTSM state changes occur — subject randomized, treatment arm unblinded, kit dispensed, supply threshold alert — enabling downstream systems (CTMS, Safety, eTMF) to react accordingly. All IWRS/RTSM data is stored with full provenance metadata and immutable audit trails to satisfy 21 CFR Part 11 requirements.

### 4. Preconditions

- [ ] A CDOS Study has been created, and the IWRS/RTSM system for that study has been provisioned with API credentials and connectivity verified.
- [ ] At least one Subject record exists in the CDOS canonical store from EDC ingestion (BR-001), with the master subject index operational for cross-system identifier resolution.
- [ ] The study's randomization scheme (stratification factors, treatment arms, block size) has been configured in the CDOS metadata and validated against the IWRS/RTSM configuration.

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-003-AC01 | Real-time randomization capture | A subject with ID "SUBJ-0042" is randomized in Signant Health IWRS to Treatment Arm B | The randomization event is published by the IWRS | The CDOS Subject record for "SUBJ-0042" is updated with randomization number, treatment arm assignment (B), stratification factors, and timestamp within 5 minutes of the IWRS event |
| BR-003-AC02 | Cross-system subject identity synchronization | A subject is enrolled in Medidata Rave (EDC) with subject ID "SITE01-003" and randomized in 4G Clinical (IWRS) with subject ID "RND-10042" | The IWRS randomization event is ingested | The CDOS master subject index links "SITE01-003" (EDC) and "RND-10042" (IWRS) to a single canonical Subject entity, and both identifiers are queryable |
| BR-003-AC03 | Blinded study data access control | A study is double-blind and the treatment arm assignment is stored in CDOS | A Clinical Research Associate (CRA) queries the subject's treatment assignment | The CRA receives a "data not available — blinded" response; only users with the "Unblinded Data Manager" role can view the treatment arm |
| BR-003-AC04 | Kit dispensation tracking | Subject "SUBJ-0042" is dispensed Kit "KIT-0089" (Drug X, Lot L2025-01) at Visit 5 | The dispensation event is ingested from Medidata RTSM | A Medication entity is created linked to Subject "SUBJ-0042" and Visit 5, with kit number, drug name, lot number, and dispensation timestamp recorded |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 | Blocks | EDC-ingested Subject records must exist in the CDOS canonical store before IWRS/RTSM data can be linked to them via the master subject index |
| BR-002 | Related | Lab results may inform dose adjustments managed by the RTSM; consistent subject identity across systems is required |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| IWRS (Signant Health) | Reads from | Extracts randomization events, treatment assignments, and kit data via API |
| IWRS (4G Clinical) | Reads from | Extracts randomization and supply management data via API |
| IWRS (Medidata RTSM) | Reads from | Extracts randomization, dispensation, and drug supply data via API |
| CDOS Canonical Data Store | Writes to | Writes/updates Subject randomization fields, creates Medication (kit dispensation) records |
| CDOS Event Bus | Publishes to | Publishes `subject.randomized`, `subject.treatment.assigned`, `kit.dispensed` events |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Subject | Read, Update | Subject records updated with randomization number, treatment arm, and stratification factors |
| Medication | Create, Read | Kit dispensation records linked to Subject and Visit (kit number, drug, lot, dispensation datetime) |
| Visit | Read | Visit metadata used to link kit dispensation to the correct study timepoint |
| Study | Read | Study metadata including randomization scheme, treatment arms, and blinding status |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A subject is randomized in the IWRS but no matching Subject record exists in the CDOS canonical store (e.g., EDC data not yet ingested) | The system creates a placeholder Subject record with IWRS-sourced data, flags it as "pending EDC confirmation", and publishes an alert. When the EDC record is subsequently ingested, the system merges the records via the master subject index. |
| A re-randomization event occurs (e.g., dose escalation cohort reassignment in an adaptive trial) | The system preserves the original randomization as a historical record with a "superseded" status, creates a new randomization record with the updated treatment arm, and publishes a `subject.re-randomized` event. The full randomization history is queryable. |
| The IWRS system is unavailable when a randomization occurs (offline-capable IWRS at a site) | The system queues the randomization event upon reconnection and processes it in order. If the randomization occurred during a connectivity gap, the system logs the delay and flags the record with the actual randomization timestamp (not the ingestion timestamp). |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Treatment assignment mismatches between IWRS and EDC records go undetected, potentially compromising the integrity of the randomization | Medium | Critical | Manual reconciliation by data managers at database lock (too late to prevent errors) |
| Unintentional unblinding due to inconsistent access controls across IWRS and CDOS | Medium | Critical | Maintain separate access control lists in each system (high administrative burden, error-prone) |
| Regulatory inspectors find gaps in randomization audit trail, leading to findings or warning letters | Medium | High | Maintain paper-based randomization logs (not compliant with 21 CFR Part 11) |

### 11. Assumptions

- IWRS/RTSM vendors provide real-time or near-real-time APIs (webhook or polling) for event notification; the CDOS does not replace the IWRS/RTSM but acts as a downstream consumer.
- The master subject index (established in BR-001) can resolve cross-system subject identifiers from EDC and IWRS/RTSM using a deterministic matching rule (site + subject number) or a configurable reconciliation workflow.
- Blinded study access controls can be enforced at the CDOS data store level (e.g., encrypted field with role-based decryption key management) without requiring a separate data store.
- Treatment arm assignments are immutable once recorded in the IWRS; the CDOS ingests them as authoritative and does not allow modification via the CDOS interface.

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | TBD | Pending |
| CRO | TBD | Pending |
| Site | TBD | Pending |


---

# Business Requirements: BR-004 through BR-006

---

## BR-004: Safety System Integration

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-004 |
| **Title** | Safety System Integration |
| **Priority** | P0 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-017, SN-001 |
| **Regulatory Basis** | ICH E6(R2) §4.11, 21 CFR Part 312.32, ICSR E2B(R3), EU GVP Module VI |
| **Status** | Draft |

### 2. Business Rationale

Adverse event data is among the most safety-critical information in clinical trials, yet it is routinely siloed in pharmacovigilance systems (Argus Safety, ArisGlobal) that are disconnected from the operational data platforms used by clinical operations teams. This disconnect means sponsors lack a unified safety signal view across trials and must manually reconcile safety data with operational data during DSMB reviews and regulatory submissions. Manual reconciliation of SAE/SUSAR events across systems currently takes 2–4 weeks per study and introduces transcription errors in approximately 5–8% of cases. Failure to integrate safety data in near-real-time increases regulatory risk and delays safety signal detection. A centralized integration ensures SN-017 (Safety Signal Transparency) and SN-001 (Unified Trial Visibility) are fulfilled by providing a single authoritative source for all adverse event data.

### 3. Detailed Description

The CDOS shall establish bidirectional, near-real-time integration with pharmacovigilance systems—specifically Argus Safety and ArisGlobal—to ingest, normalize, and present AdverseEvent data alongside operational clinical data. When a new adverse event is entered in the Safety system, the CDOS adapter shall receive the event via message queue or API webhook, map it to the canonical AdverseEvent entity, and apply MedDRA coding (Preferred Term, High-Level Group Term, System Organ Class). The integration must distinguish between Serious Adverse Events (SAE) and Suspected Unexpected Serious Adverse Reactions (SUSAR), applying appropriate notification routing and escalation timelines per regulatory requirements (7-day fatal/life-threatening, 15-day all others for ICSRs). The CDOS shall enrich incoming safety events with subject, study, site, and visit context from the canonical data model so that safety reviewers can immediately see the trial context. Outbound, when operational data changes affect safety-relevant fields (e.g., subject withdrawal, dose modification), the CDOS shall push updates to the Safety system to keep causality assessments current. All safety data flows must comply with ICH E2B(R3) ICSR format requirements and maintain a complete, immutable audit trail per 21 CFR Part 11. The integration shall support multiple concurrent studies and CROs, with configurable routing rules per sponsor. Safety dashboards within CDOS shall present aggregated and drill-down views of adverse events by study, site, severity, and MedDRA classification.

### 4. Preconditions

- [ ] The canonical AdverseEvent entity and its JSON Schema are defined in the CDOS data model (05-data-models/canonical/)
- [ ] Connectivity credentials and API endpoints for Argus Safety and ArisGlobal are provisioned and tested
- [ ] MedDRA dictionary version is configured per study and available in the CDOS terminology service
- [ ] Safety system adapters (services/adapters/safety_adapter.py) are registered in the adapter registry

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-004-AC01 | SAE ingestion with MedDRA coding | A new SAE is reported in Argus Safety for Study ABC-101 | The CDOS safety adapter receives the event | An AdverseEvent entity is created in the canonical model with correct MedDRA PT, HLGT, SOC codes, SAE flag set to true, and audit trail entry recorded |
| BR-004-AC02 | SUSAR notification escalation | A SUSAR event is identified in ArisGlobal for a fatal outcome | The event is ingested by CDOS | A high-priority notification is sent to the sponsor safety team and study lead within 15 minutes, and the event is flagged for 7-day expedited reporting |
| BR-004-AC03 | Outbound safety update on dose modification | A subject's dose is modified in CDOS and that subject has an open AdverseEvent | The dose modification is committed | The Safety system receives an update with the new dose context, and the audit trail records both the modification and the outbound sync |
| BR-004-AC04 | Cross-study safety dashboard | AdverseEvent data exists across three studies in CDOS | A sponsor user opens the safety signal dashboard | The dashboard displays aggregated SAE/SUSAR counts by MedDRA SOC, with drill-down to individual events, and loads within 5 seconds |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (Canonical Data Model) | Blocks | The AdverseEvent entity definition must exist before safety data can be mapped |
| BR-002 (EDC Integration) | Related | Subject and visit context from EDC data enriches safety events |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| Safety (Argus Safety) | Reads from, Writes to | Bidirectional AdverseEvent data flow |
| Safety (ArisGlobal) | Reads from, Writes to | Bidirectional AdverseEvent data flow |
| CDOS Event Bus | Writes to | Publishes safety.received and safety.updated events |
| CDOS Canonical Store | Writes to | Creates/updates AdverseEvent entities |
| CDOS Notification Service | Writes to | Triggers SAE/SUSAR alerts |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| AdverseEvent | Create, Read, Update | Ingested and enriched adverse event records |
| Subject | Read | Subject context for safety event enrichment |
| Study | Read | Study context and safety routing configuration |
| Visit | Read | Visit timing context for causality assessment |
| Dose | Read | Dose context for causality assessment |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Safety system is unavailable during event ingestion | Events are queued in a dead-letter queue with retry logic (3 retries, exponential backoff). If all retries fail, an alert is sent to the integration operations team and the event is logged for manual reconciliation. |
| Duplicate SAE received from two safety systems for the same event | The CDOS deduplicates based on (subject_id, event_term, onset_date, safety_system_id). If a true duplicate is detected, the second record is linked as a duplicate reference, not a new entity. |
| MedDRA version mismatch between study and safety system | The CDOS flags the mismatch, maps using the study-configured MedDRA version, and creates a reconciliation task for the data management team. |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Delayed safety signal detection across trials | High | High | Manual cross-system safety review process with weekly reconciliation meetings |
| Regulatory finding during inspection for incomplete safety data integration | High | High | Maintain documented manual SOPs for safety data reconciliation as interim measure |
| Transcription errors in manual SAE reconciliation | Medium | Medium | Dual data entry and verification process as interim control |

### 11. Assumptions

- Argus Safety and ArisGlobal expose RESTful APIs or support HL7/FHIR messaging for integration; if not, a file-based (CSV/XML) integration fallback will be designed
- MedDRA licensing is managed centrally and a current version is always available to the CDOS terminology service
- Safety system data retention policies align with CDOS archival requirements (minimum 15 years per ICH E6(R2))
- Sponsor safety teams will designate authorized users for CDOS safety dashboards within 30 days of deployment

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor (Pharmacovigilance) | TBD | Pending |
| CRO (Safety Operations) | TBD | Pending |
| Regulatory Affairs | TBD | Pending |
| QA / Compliance | TBD | Pending |

---

## BR-005: eCOA and Wearable Data Ingestion

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-005 |
| **Title** | eCOA and Wearable Data Ingestion |
| **Priority** | P1 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-020, SN-023 |
| **Regulatory Basis** | FDA Guidance on eCOA (2022), 21 CFR Part 11, ICH E6(R2) §5.5 |
| **Status** | Draft |

### 2. Business Rationale

Electronic Clinical Outcome Assessments (eCOA) and wearable/IoT sensor data are becoming central to modern clinical trials, particularly in decentralized and hybrid study designs. Currently, eCOA data from platforms like ERT and Clario arrives in proprietary formats that must be manually mapped to CDISC standards, a process that takes data management teams 4–6 weeks per study. Wearable data from devices such as ActiGraph and Verily generates high-frequency time-series data (heart rate, activity counts, sleep metrics) that has no standard mapping path and is often excluded from analysis due to integration complexity. This exclusion means sponsors miss potentially valuable safety and efficacy signals. By providing automated ingestion and canonical mapping for both eCOA and wearable data, CDOS fulfills SN-020 (Safety Reporting Accessibility) by enabling patient-reported outcomes to flow into the safety signal pipeline, and SN-023 (Clean, Analysis-Ready Data) by ensuring these data types are available in CDISC-compatible format without manual rework.

### 3. Detailed Description

The CDOS shall provide configurable ingestion adapters for eCOA platforms (ERT, Clario, Medidata Patient Cloud) and wearable/IoT sensor systems (ActiGraph, Verily, Apple HealthKit). For eCOA data, the adapter shall ingest electronic Patient-Reported Outcomes (ePRO), Clinician-Reported Outcomes (ClinRO), and Observer-Reported Outcomes (ObsRO) data, mapping questionnaire responses to the canonical data model and applying CDASH/SDTM domain mappings (e.g., QS domain for questionnaires, FA domain for functional assessments). For wearable data, the adapter shall ingest high-frequency time-series sensor data, perform configurable aggregation (e.g., daily averages, epoch-level summaries), and map aggregated outputs to appropriate SDTM domains or supplementary qualifiers. All ingested data shall be validated against study-specific edit checks and value ranges defined in the study configuration. The system shall support both push (streaming/API) and pull (batch/file) ingestion modes depending on the source system's capabilities. Incoming eCOA and wearable data shall be linked to the canonical Subject and Visit entities to maintain traceability to the trial context. The CDOS shall flag data quality issues (missing assessments, out-of-range values, device malfunctions) and generate Queries per the configured edit check rules. All ingested data shall carry provenance metadata (source system, ingestion timestamp, device ID for wearables, form version for eCOA) to support audit and regulatory inspection.

### 4. Preconditions

- [ ] eCOA platform API credentials and data format specifications are obtained from ERT, Clario, and Medidata Patient Cloud
- [ ] Wearable device data format specifications and aggregation rules are defined per study protocol
- [ ] CDISC mapping specifications for eCOA instruments (questionnaire mappings to QS, FA domains) are documented and version-controlled
- [ ] The canonical Subject and Visit entities exist and are populated for studies requiring eCOA/wearable ingestion

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-005-AC01 | eCOA ePRO ingestion with CDISC mapping | Study ABC-102 uses ERT for ePRO collection, and a subject completes a PHQ-9 questionnaire | The CDOS eCOA adapter pulls the completed assessment | A canonical eCOA record is created with CDASH/SDTM QS domain mapping, linked to the correct Subject and Visit, with audit trail entry |
| BR-005-AC02 | Wearable data aggregation and mapping | A subject wears an ActiGraph device that generates 7 days of accelerometer data | The CDOS wearable adapter ingests the raw data | Daily step counts and activity summaries are computed, mapped to the FA domain, and linked to the subject, with device ID and provenance metadata recorded |
| BR-005-AC03 | Data quality query generation | An eCOA assessment has a PHQ-9 total score of 30, exceeding the validated maximum of 27 | The CDOS edit check engine processes the record | A Query is auto-generated, the record is flagged as "under review," and the site data coordinator is notified |
| BR-005-AC04 | Missing assessment detection | A subject is expected to complete a weekly ePRO diary but no data is received within the protocol-defined window | The grace period expires | The CDOS generates a missing data alert, creates a Query for the site, and updates the visit compliance dashboard |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (Canonical Data Model) | Blocks | Canonical Subject, Visit, and eCOA entities must be defined |
| BR-003 (EDC Integration) | Related | Visit schedules from EDC define expected assessment windows |
| BR-004 (Safety System Integration) | Related | Patient-reported adverse events in eCOA may trigger safety ingestion flows |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| eCOA (ERT, Clario, Medidata Patient Cloud) | Reads from | Ingests ePRO, ClinRO, ObsRO data |
| Wearables (ActiGraph, Verily, Apple HealthKit) | Reads from | Ingests sensor time-series data |
| CDOS Canonical Store | Writes to | Creates/updates eCOA and wearable data entities |
| CDOS Query Service | Writes to | Generates data quality queries |
| CDOS Event Bus | Writes to | Publishes ecoa.received and wearable.received events |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| CRFPage | Create, Read | eCOA assessment forms mapped to canonical CRF pages |
| Subject | Read | Subject linkage for incoming eCOA/wearable data |
| Visit | Read, Update | Visit completion status updated when assessments arrive |
| Query | Create | Auto-generated data quality queries |
| LabResult | Create | Wearable-derived metrics treated as results for analysis |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| eCOA platform returns data in a format version not yet supported by the adapter | The adapter rejects the file with a descriptive error, logs the unsupported format version, and creates an integration operations ticket. No partial data is committed. |
| Wearable device transmits data with significant gaps (device removed or battery dead) | The adapter identifies gaps exceeding the protocol-defined tolerance, marks affected time periods as "missing," generates a Query, and continues processing available data. |
| Duplicate eCOA submission from a subject (e.g., re-submitted diary) | The adapter detects duplicate based on (subject_id, instrument_id, assessment_date) and applies the last-submitted-wins rule with full audit trail of both submissions. |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| eCOA and wearable data excluded from regulatory submissions due to integration gaps | High | High | Manual mapping and CDISC conversion processes with dedicated data management resources |
| Patient-reported safety events from eCOA not flowing to pharmacovigilance | Medium | High | Manual adverse event reconciliation between eCOA and safety systems |
| Increased site burden due to duplicate data entry across EDC and eCOA | High | Medium | Provide sites with data entry SOPs that reference both systems |

### 11. Assumptions

- eCOA platforms support RESTful API or SFTP-based data export in a documented format (e.g., CDISC ODM, vendor-proprietary XML/CSV)
- Wearable device data is available via cloud APIs (e.g., ActiGraph CentrePoint, Verily Study Watch cloud) with appropriate authentication
- Study protocols define acceptable data collection windows and aggregation rules for wearable data
- CDISC mapping specifications for common eCOA instruments (PHQ-9, GAD-7, EQ-5D, etc.) are maintained centrally and reusable across studies

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor (Data Management) | TBD | Pending |
| CRO (Clinical Operations) | TBD | Pending |
| Site (Investigator) | TBD | Pending |
| Data Management / Biostatistics | TBD | Pending |

---

## BR-006: CTMS Synchronization

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-006 |
| **Title** | CTMS Synchronization |
| **Priority** | P1 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-003, SN-008 |
| **Regulatory Basis** | ICH E6(R2) §5.0 (Trial Management), 21 CFR Part 11 |
| **Status** | Draft |

### 2. Business Rationale

Clinical Trial Management Systems (CTMS) are the primary operational backbone for study planning, site management, and enrollment tracking. However, CTMS data (study metadata, site activation status, enrollment counts, visit schedules) frequently diverges from the actual clinical data in EDC and other source systems because synchronization is manual. This divergence leads to inaccurate enrollment forecasts, delayed milestone reporting, and unreliable cost projections—directly impacting SN-003 (Cost and Timeline Predictability). CRO operational teams also need real-time dashboards combining CTMS operational data with EDC data quality metrics, as expressed in SN-008 (Operational Dashboards). Currently, CROs report spending 10–15 hours per week per study manually reconciling CTMS records with EDC data. Bidirectional synchronization between CDOS and leading CTMS platforms (Veeva Vault CTMS, Oracle Siebel CTMS) eliminates this reconciliation burden and ensures a single source of truth for study operations.

### 3. Detailed Description

The CDOS shall establish bidirectional synchronization with Clinical Trial Management Systems, specifically Veeva Vault CTMS and Oracle Siebel CTMS, to keep study operational data consistent across platforms. The synchronization shall cover four primary data domains: (1) Study metadata—protocol number, title, phase, therapeutic area, regulatory identifiers, and study status; (2) Site status—site activation dates, site capabilities, investigator information, and regulatory approvals; (3) Enrollment data—screened, enrolled, randomized, and discontinued subject counts by site, with automatic recalculation when EDC enrollment events occur; (4) Visit schedules—protocol-defined visit windows, actual visit dates, and visit compliance status. The CDOS shall detect changes in either system and propagate them to the other within a configurable synchronization interval (default: 15 minutes for critical fields like enrollment, 1 hour for metadata). Conflict resolution shall follow a configurable precedence rule—by default, the system with the most recent change timestamp wins, but sponsors can override this per entity type. All synchronization events shall be logged with full provenance (source system, timestamp, user, before/after values) in an immutable audit trail. The CDOS shall provide a synchronization health dashboard showing the status of all active sync jobs, error counts, and lag metrics. If the CTMS or CDOS is temporarily unavailable, the sync engine shall queue changes and apply them in order when connectivity is restored, with automatic conflict detection.

### 4. Preconditions

- [ ] CTMS API credentials and connectivity are established for Veeva Vault CTMS and Oracle Siebel CTMS
- [ ] The canonical Study, Site, and Visit entities are defined and version-controlled in the CDOS data model
- [ ] Field-level mapping specifications between CTMS data models and the CDOS canonical model are documented per CTMS platform
- [ ] Conflict resolution rules are approved by the sponsor data governance team

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-006-AC01 | Enrollment count synchronization | Study ABC-103 has 50 subjects enrolled in CDOS (from EDC) and 48 in Veeva Vault CTMS | The CDOS sync engine runs the enrollment reconciliation job | CTMS is updated to 50 enrolled subjects, the discrepancy is logged, and an audit trail entry records the sync with source=EDC, target=CTMS |
| BR-006-AC02 | Site activation bidirectional sync | A new site is activated in Oracle Siebel CTMS with activation date and PI assignment | The CDOS sync adapter detects the new site record | A canonical Site entity is created in CDOS, linked to the correct Study, and published to the event bus as site.activated |
| BR-006-AC03 | Visit schedule sync with conflict detection | A visit window is updated in CDOS (via protocol amendment) and simultaneously updated in CTMS by a different user | The sync engine detects conflicting updates | The conflict is logged, the sponsor-configured precedence rule is applied (CTMS wins by default), and a notification is sent to the study manager with both values for manual review |
| BR-006-AC04 | Sync health dashboard | Multiple sync jobs are running across 10 studies | A CRO operations manager opens the sync health dashboard | The dashboard shows per-study sync status, last successful sync timestamp, error count, and average sync lag, with drill-down to individual sync events |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (Canonical Data Model) | Blocks | Canonical Study, Site, and Visit entities must exist |
| BR-002 (EDC Integration) | Enables | EDC enrollment events trigger CTMS enrollment count updates |
| BR-003 (Operational Dashboards) | Related | Sync health metrics feed into the CDOS operational dashboard |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CTMS (Veeva Vault CTMS) | Reads from, Writes to | Bidirectional study metadata, site, enrollment, visit sync |
| CTMS (Oracle Siebel CTMS) | Reads from, Writes to | Bidirectional study metadata, site, enrollment, visit sync |
| CDOS Canonical Store | Reads from, Writes to | Canonical Study, Site, Visit entities updated via sync |
| CDOS Event Bus | Writes to | Publishes sync.completed, sync.conflict events |
| CDOS Sync Engine | Core component | Manages sync jobs, conflict resolution, and queuing |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Study | Read, Update | Study metadata synchronization (title, phase, status, identifiers) |
| Site | Create, Read, Update | Site activation, PI assignment, capability data |
| Subject | Read | Enrollment counts derived from Subject status changes |
| Visit | Read, Update | Visit schedule windows and actual visit dates |
| Investigator | Read, Update | PI and sub-investigator assignments per site |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| CTMS and CDOS both modify the same site record within the sync interval | The sync engine detects the conflict, logs both versions, applies the precedence rule, and sends a notification to the study manager with a side-by-side diff for manual resolution if needed. |
| CTMS API rate limit is reached during a large batch sync | The sync engine throttles requests, respects the rate limit header, queues remaining records, and resumes when the limit resets. A warning is logged and displayed on the sync health dashboard. |
| A study is decommissioned in CTMS but still active in CDOS | The sync engine does not automatically decommission in CDOS. Instead, it creates a "pending decommission" flag and notifies the sponsor data steward to confirm, preventing accidental data loss. |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Enrollment forecasts and cost projections are unreliable due to stale CTMS data | High | High | Weekly manual reconciliation meetings with CRO and sponsor operations teams |
| Site activation delays go undetected because CTMS status is not reflected in CDOS | Medium | Medium | Manual site status reporting via email and shared spreadsheets |
| Regulatory inspection findings for inconsistent study records across systems | Medium | High | Documented SOPs for cross-system data reconciliation with audit trail evidence |

### 11. Assumptions

- Veeva Vault CTMS and Oracle Siebel CTMS expose RESTful APIs with webhook or polling-based change detection capabilities
- CTMS data models follow a reasonably standard schema that can be mapped to the CDOS canonical model without per-study custom development (though per-CTMS-variant adapters are expected)
- Sponsors and CROs will designate a data steward responsible for reviewing sync conflicts within 48 hours
- The CTMS is the system of record for study-level operational metadata (protocol version, regulatory status), while CDOS/EDC is the system of record for subject-level data

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor (Clinical Operations) | TBD | Pending |
| CRO (Trial Management) | TBD | Pending |
| Site (Study Coordinator) | TBD | Pending |
| QA / Compliance | TBD | Pending |


---

# Business Requirements: BR-007, BR-008, BR-009

Detailed business requirements for CDISC Standards Mapping, ADaM Generation, and 21 CFR Part 11 Compliance within the Clinical Development Operating System (CDOS).

---

## BR-007: CDISC SDTM Mapping Engine

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-007 |
| **Title** | CDISC SDTM Mapping Engine |
| **Priority** | P0 — Critical |
| **Category** | Data Standards |
| **Source Stakeholder Need(s)** | SN-002, SN-015, SN-023 |
| **Regulatory Basis** | ICH E3, ICH M8, FDA Study Data Technical Conformance Guide, PMDA SDTM Implementation Guide |
| **Status** | Draft |

### 2. Business Rationale

Regulatory agencies including the FDA, EMA, and PMDA require clinical trial data submissions in CDISC SDTM format. Currently, sponsors and CROs spend 4-8 weeks per study performing manual or semi-automated SDTM mapping, costing between $150,000 and $400,000 per Phase III trial in data management labor. Errors in SDTM mapping are among the top reasons for FDA refuse-to-file decisions and information request cycles that delay approval by 3-6 months. A built-in, configurable SDTM mapping engine eliminates the bottleneck between data cleaning and regulatory submission readiness, enabling continuous, real-time SDTM compliance throughout the trial lifecycle.

### 3. Detailed Description

CDOS shall provide a configurable transformation engine that converts canonical clinical data (Subject, AdverseEvent, LabResult, Dose, Medication entities) into CDISC SDTM v3.4 domain datasets. When a data manager initiates an SDTM export for a study, the engine shall read the current canonical data, apply study-specific mapping rules, and produce SDTM domain datasets (DM, AE, LB, EX, CM at minimum) in SAS transport (.xpt) or CSV format. The mapping rules shall be configurable per study via a mapping specification UI or uploaded mapping spreadsheet, without requiring code changes. Each mapping rule shall define the source canonical field, the target SDTM variable, the domain, and any required value-level transformations (e.g., unit conversions, code list translations, date formatting to ISO 8601). The engine shall validate all generated SDTM datasets against the SDTM v3.4 structural validation rules (e.g., required variables present, correct variable types, valid code list values) and produce a validation report listing any conformance issues with severity levels (error, warning, note). For each SDTM dataset generated, the engine shall also produce a Define-XML v2.1 metadata file that describes the structure, variables, code lists, and computational methods used, enabling reviewers to understand the data without accessing the source systems. The engine shall support incremental SDTM generation — when new data arrives for a study that has already been partially mapped, only the changed or new records shall be re-processed, reducing compute time for large studies. Study-level SDTM mapping configurations shall be version-controlled, with the ability to compare and rollback mapping versions and to lock a mapping configuration for a specific regulatory submission.

### 4. Preconditions

- [ ] Canonical data model entities (Subject, AdverseEvent, LabResult, Dose, Medication) are populated from integrated EDC, LIMS, IWRS, and Safety systems (BR-001 through BR-006).
- [ ] CDISC SDTM v3.4 controlled terminology and code lists are loaded and maintained in the CDOS terminology service.
- [ ] Study-specific SDTM mapping specifications (source-to-target mappings) have been configured by the data management team for the target study.

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-007-AC01 | DM domain generation | A study with 500 enrolled subjects in canonical Subject data | The data manager triggers SDTM export for the DM domain | A valid SDTM DM dataset is produced containing USUBJID, SUBJID, AGE, SEX, RACE, ETHNIC, ARMCD, ARM, COUNTRY, with all required variables populated per SDTM v3.4 specification, and a validation report with zero errors |
| BR-007-AC02 | AE domain mapping | A study with 1,200 AdverseEvent records in canonical data with MedDRA codes | The data manager triggers SDTM export for the AE domain | A valid SDTM AE dataset is produced containing USUBJID, AETERM, AEDECOD, AESEV, AESER, AEACN, AESTDTC, AEENDTC, with MedDRA preferred terms correctly mapped from the canonical MedDRA coding fields |
| BR-007-AC03 | Define-XML generation | SDTM datasets have been generated for DM, AE, LB, EX, CM domains | The data manager requests Define-XML generation | A Define-XML v2.1 file is produced that accurately describes all generated domains, variables, code lists, and value-level metadata, passing the Define-XML v2.1 validation schema |
| BR-007-AC04 | Mapping validation | A study SDTM mapping specification contains a mapping rule that converts canonical weight (kg) to SDTM LB domain variable with target unit (g) | SDTM export is triggered | The engine applies the unit conversion correctly, produces the LB dataset with values in grams, and the validation report flags any records where the original value was null or out of physiologic range |
| BR-007-AC05 | Incremental export | SDTM was previously generated for a study with 300 subjects; 50 new subjects are enrolled | The data manager triggers a re-export | Only the 50 new subjects' records are processed; the output contains all 350 subjects; the previously generated 300 subjects' records are unchanged unless their source data was modified |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 | Blocks | EDC data ingestion must be operational so canonical Subject and CRFPage data exists for SDTM mapping |
| BR-002 | Blocks | LIMS integration must provide LabResult data for LB domain generation |
| BR-004 | Blocks | Safety integration must provide AdverseEvent data for AE domain generation |
| BR-003 | Blocks | IWRS integration must provide Dose/randomization data for EX domain generation |
| BR-016 | Enables | Metadata-driven study configuration supports mapping configuration per study |
| BR-019 | Enables | Role-based access control ensures only authorized data managers can configure and execute SDTM mappings |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS Canonical Data Store | Reads from | The engine reads canonical entities (Subject, AdverseEvent, LabResult, Dose, Medication) as source data for SDTM transformation |
| CDOS Mapping Configuration Service | Reads from / Writes to | The engine reads mapping rules and writes mapping execution logs and version history |
| CDOS Terminology Service | Reads from | The engine reads CDISC controlled terminology, code lists, and codelists for value-level transformations |
| CDOS Validation Service | Writes to | The engine writes SDTM validation reports to the validation service for data manager review |
| CDOS Export Service | Writes to | The engine writes generated SDTM datasets (.xpt, .csv) and Define-XML files to the export service for download or submission assembly |
| RegSubmit | Writes to | Generated SDTM packages may be forwarded to the Regulatory Submission system for eCTD assembly |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Subject | Read | Subject demographic and enrollment data mapped to SDTM DM domain |
| AdverseEvent | Read | Adverse event data mapped to SDTM AE domain |
| LabResult | Read | Laboratory result data mapped to SDTM LB domain |
| Dose | Read | Study drug dosing data mapped to SDTM EX domain |
| Medication | Read | Concomitant medication data mapped to SDTM CM domain |
| Submission | Create | SDTM submission packages created as output artifacts |
| CRFPage | Read | CRF page metadata used to trace SDTM variables back to source CRF fields |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A canonical record maps to multiple SDTM domains (e.g., a LabResult that feeds both LB and a supplemental qualifier domain) | The engine shall produce records in all applicable domains, maintaining referential integrity via USUBJID and sequence variables |
| A mapping rule references a code list value that does not exist in the canonical data | The engine shall flag the record as a validation warning in the report, assign the SDTM default value per the mapping specification (e.g., "NOT DONE" or null), and continue processing remaining records |
| SDTM mapping specification contains a circular dependency (e.g., variable A derived from variable B which is derived from variable A) | The engine shall detect the circular dependency at configuration time, reject the mapping rule, and display a clear error message to the data manager |
| A study has no canonical data for a required SDTM domain (e.g., no AdverseEvent records exist but AE domain is configured for export) | The engine shall produce an empty AE dataset with correct header/variable structure and a validation note indicating zero records, rather than failing the export |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Regulatory submission delays due to manual SDTM mapping errors requiring multiple correction cycles | High | High | Provide real-time validation feedback during mapping configuration; pre-validate before export |
| Inconsistent SDTM mappings across studies managed by different data management teams | Medium | High | Implement organization-level mapping templates that can be inherited and customized per study |
| Define-XML metadata drifts from actual SDTM datasets due to manual maintenance | Medium | Medium | Generate Define-XML automatically from the same mapping configuration used for dataset generation |

### 11. Assumptions

- CDISC SDTM v3.4 remains the current regulatory-required submission standard during the initial CDOS release; future versions (e.g., SDTM v3.5) will be supported via version upgrade of the terminology service and mapping rules.
- Studies within CDOS will use the canonical data model as the single source of truth; no direct SDTM mapping from raw EDC data bypassing the canonical model is required.
- Data management teams are trained in CDISC SDTM conventions and can configure study-specific mapping rules using the CDOS mapping specification interface.
- SAS transport (.xpt) format generation requires the CDOS export service to have access to a SAS-compatible XPT writer library (e.g., pyreadstat or xport library).

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [Sponsor Data Management Lead] | Pending |
| CRO | [CRO Biostatistics Director] | Pending |
| Regulatory | [Regulatory Affairs Manager] | Pending |
| QA | [QA Compliance Officer] | Pending |

---

## BR-008: ADaM Dataset Generation

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-008 |
| **Title** | ADaM Dataset Generation |
| **Priority** | P1 — High |
| **Category** | Data Standards |
| **Source Stakeholder Need(s)** | SN-002, SN-015, SN-024 |
| **Regulatory Basis** | ICH E9, FDA Study Data Technical Conformance Guide, CDISC ADaM v2.1 Implementation Guide |
| **Status** | Draft |

### 2. Business Rationale

After SDTM datasets are produced, biostatisticians must create ADaM (Analysis Data Model) datasets to perform the statistical analyses that form the basis of regulatory submission efficacy and safety conclusions. ADaM dataset creation is currently a highly manual, SAS-programming-intensive process that takes 6-12 weeks per study and requires deep domain expertise in both statistics and CDISC standards. Inconsistencies between SDTM source data and ADaM derivations frequently lead to data reviewer questions from the FDA, adding 2-4 months to review timelines. Automating ADaM generation from SDTM data with full traceability ensures that analysis datasets are reproducible, derivations are transparent, and sponsors can respond rapidly to regulatory data requests.

### 3. Detailed Description

CDOS shall generate CDISC ADaM v2.1 analysis-ready datasets from SDTM-mapped data, supporting the most commonly required ADaM structures: ADSL (Subject-Level Analysis Dataset), ADAE (Adverse Event Analysis Dataset), and ADLB (Laboratory Analysis Dataset). When a biostatistician initiates ADaM generation for a study, the engine shall read the SDTM datasets (previously generated by BR-007), apply ADaM derivation rules, and produce ADaM datasets in SAS transport (.xpt) or CSV format. The derivation rules shall define how analysis variables are computed from SDTM source variables, including: treatment arm assignments, analysis population flags (ITT, mITT, per-protocol), baseline and change-from-baseline calculations for lab parameters, adverse event grouping by system organ class and preferred term, and exposure-adjusted incidence rates. Each ADaM dataset variable shall include traceability metadata linking it back to its source SDTM domain, variable, and derivation method, enabling a regulatory reviewer to trace any analysis result back to the underlying tabulation data. The engine shall generate ADaM Define-XML v2.1 metadata describing the analysis datasets, computational methods, and parameter definitions. ADaM derivation rules shall be configurable per study, supporting custom analysis visit windows, custom population definitions, and study-specific endpoint derivations without code changes. The engine shall validate generated ADaM datasets against CDISC ADaM v2.1 conformance rules and produce a validation report. When SDTM source data is updated (e.g., due to data cleaning or query resolution), the engine shall support re-generation of affected ADaM datasets with change impact analysis showing which analysis results may have changed.

### 4. Preconditions

- [ ] SDTM datasets for the study have been successfully generated and validated via BR-007 (CDISC SDTM Mapping Engine).
- [ ] ADaM derivation specifications (analysis visit mappings, population definitions, endpoint derivations) have been configured by the biostatistics team for the target study.
- [ ] CDISC ADaM v2.1 conformance rules and controlled terminology are loaded in the CDOS terminology service.

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-008-AC01 | ADSL generation | A study with SDTM DM, EX, and DS (disposition) domains generated, with treatment arm and disposition data | The biostatistician triggers ADSL generation | A valid ADSL dataset is produced containing USUBJID, SUBJID, TRT01P, TRT01A, ITTFL, SAFFL, PPFL, RANDDT, TRTSDT, TRTEDT, with population flags correctly derived from disposition and exposure data |
| BR-008-AC02 | ADAE generation with traceability | A study with SDTM AE and EX domains, and ADSL already generated | The biostatistician triggers ADAE generation | A valid ADAE dataset is produced containing each adverse event record with treatment-emergent flag (TRTEMFL), analysis start/stop relative day (ARELSTRTD, ARELSTOPTD), and every derived variable traceable to its source SDTM AE variable and derivation method |
| BR-008-AC03 | ADLB with baseline and change-from-baseline | A study with SDTM LB domain containing lab results at screening (baseline), Week 4, Week 8, and Week 12 visits | The biostatistician triggers ADLB generation | A valid ADLB dataset is produced with BASE (baseline value), CHG (change from baseline), and PCHG (percent change from baseline) correctly calculated for each post-baseline visit, with ABLFL (baseline flag) correctly set on the pre-treatment assessment |
| BR-008-AC04 | Define-XML for ADaM | ADaM datasets have been generated for ADSL, ADAE, ADLB | The biostatistician requests ADaM Define-XML generation | A Define-XML v2.1 file is produced describing all analysis datasets, analysis variables, computational methods (including parameter-level derivations), and controlled terminology, passing Define-XML v2.1 schema validation |
| BR-008-AC05 | SDTM update propagation | An ADaM dataset was generated; subsequently 10 SDTM AE records were updated due to query resolution | The biostatistician triggers ADaM re-generation with change analysis | The engine re-generates ADAE, identifies which ADAE records are affected by the SDTM changes, and produces a change impact report listing affected subjects and variables |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-007 | Blocks | SDTM datasets must be generated before ADaM can be derived from them |
| BR-016 | Enables | Metadata-driven study configuration supports ADaM derivation rule configuration per study |
| BR-019 | Enables | Role-based access control ensures only authorized biostatisticians can configure and execute ADaM derivations |
| BR-024 | Related | Cross-study data harmonization (central data dictionary) ensures consistent ADaM derivations across studies in a program |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS SDTM Data Store | Reads from | The engine reads SDTM domain datasets (DM, AE, LB, EX, CM, DS) as source data for ADaM derivation |
| CDOS ADaM Configuration Service | Reads from / Writes to | The engine reads derivation rules and writes execution logs and version history |
| CDOS Terminology Service | Reads from | The engine reads CDISC ADaM controlled terminology and code lists |
| CDOS Validation Service | Writes to | The engine writes ADaM validation reports for biostatistician review |
| CDOS Export Service | Writes to | The engine writes generated ADaM datasets (.xpt, .csv) and Define-XML files for download or submission assembly |
| CDOS Analytics Service | Reads from | The analytics service may read ADaM datasets for interim analysis and reporting |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Subject | Read | Subject-level data from SDTM DM used to generate ADSL population flags and treatment arm variables |
| AdverseEvent | Read | Adverse event data from SDTM AE used to generate ADAE with analysis derivations |
| LabResult | Read | Laboratory data from SDTM LB used to generate ADLB with baseline and change-from-baseline derivations |
| Dose | Read | Exposure data from SDTM EX used to derive treatment start/end dates and exposure-adjusted calculations |
| Submission | Create | ADaM submission packages created as output artifacts linked to the associated SDTM submission |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A subject has multiple treatment arms due to dose adjustment or treatment switch during the study | The engine shall derive both TRT01P (planned) and TRT01A (actual) treatment variables, and flag the subject appropriately in population derivation; the biostatistician can configure which treatment variable drives the analysis populations |
| A lab result has no matching baseline assessment for a subject (e.g., subject missed the screening visit) | The engine shall set ABLFL to null and BASE to null for that subject's post-baseline records, flag the derivation in the validation report as a warning, and continue processing; the biostatistician can review and decide on imputation strategy |
| SDTM source data contains records with future dates or logically inconsistent date sequences (e.g., AE end date before start date) | The engine shall produce the ADaM record with derivations based on available dates, set derived relative-day variables to null where calculation is impossible, and flag the record in the validation report as an error for data management review |
| A study has an adaptive design with interim analysis and population re-estimation | The engine shall support multiple ADaM versions per study (e.g., interim analysis ADaM and final analysis ADaM), each with its own derivation configuration and population definitions, maintaining full version history |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Biostatisticians spend 6-12 weeks per study writing custom SAS programs for ADaM derivation, delaying submission timelines | High | High | Provide pre-built ADaM derivation templates for standard designs; allow customization for adaptive and complex designs |
| ADaM derivations are inconsistent across studies in the same program due to different biostatistician approaches | Medium | High | Implement program-level ADaM derivation templates with study-level overrides; enforce review/approval workflow for derivation configurations |
| Regulatory reviewers cannot trace ADaM analysis results back to SDTM source data, leading to information requests | Medium | High | Enforce mandatory traceability metadata for every derived variable; generate traceability reports automatically |

### 11. Assumptions

- SDTM datasets are the sole source for ADaM derivation; direct ADaM generation from canonical data bypassing SDTM is not in scope for this release.
- Biostatisticians will configure study-specific ADaM derivation rules using the CDOS configuration interface; complex custom derivations (e.g., time-to-event endpoint calculations) may still require external statistical programming with ADaM export as input.
- The initial CDOS release supports ADSL, ADAE, and ADLB as the standard ADaM dataset structures; additional structures (ADPC, ADPP, etc.) will be added based on demand.
- ADaM datasets are generated from the same SDTM snapshot used for regulatory submission; interim analysis ADaM datasets are treated as separate versions.

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [Sponsor Biostatistics Lead] | Pending |
| CRO | [CRO Biostatistics Director] | Pending |
| Regulatory | [Regulatory Affairs Manager] | Pending |
| Data Management | [Data Management Lead] | Pending |

---

## BR-009: 21 CFR Part 11 Compliance

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-009 |
| **Title** | 21 CFR Part 11 Compliance |
| **Priority** | P0 — Critical |
| **Category** | Compliance |
| **Source Stakeholder Need(s)** | SN-009, SN-016, SN-018 |
| **Regulatory Basis** | 21 CFR Part 11 (FDA), ICH E6(R2) Section 5.5, EU Annex 11 (Computerised Systems) |
| **Status** | Draft |

### 2. Business Rationale

21 CFR Part 11 is the FDA regulation governing electronic records and electronic signatures in clinical trials. Non-compliance can result in FDA warning letters, clinical hold orders, or refusal to approve a marketing application — outcomes that can cost a sponsor $50M-$500M in delayed revenue per drug. In 2024, the FDA issued 23 warning letters citing Part 11 deficiencies, with the most common findings being inadequate audit trails, lack of electronic signature controls, and insufficient system access management. For CDOS to be used as the system of record for clinical trial data submitted to the FDA, full 21 CFR Part 11 compliance is not optional — it is a regulatory prerequisite that must be designed into the system from the ground up, not retrofitted.

### 3. Detailed Description

CDOS shall comply with all applicable requirements of 21 CFR Part 11 for electronic records and electronic signatures. Every data creation, modification, or deletion event in CDOS shall generate an immutable audit trail record that captures the user identity (unique user ID), timestamp (UTC with timezone offset), the action performed, the previous value, the new value, and the reason for change (mandatory free-text or structured reason code). Audit trail records shall be append-only — no audit trail record may be modified or deleted by any user, including system administrators; any attempt to tamper with audit trail data shall be logged as a security event. Electronic signatures in CDOS shall be implemented as a two-factor authentication process (user ID + password, or user ID + biometric) that captures the signer's identity, the date and time of the signature, the meaning of the signature (e.g., "authored," "reviewed," "approved," "rejected"), and shall be linked to the signed electronic record in a way that cannot be altered after signing. CDOS shall enforce unique user identification through a centralized identity provider (IdP) integration, ensuring that no two users share a user ID, and that user IDs cannot be reused after account deactivation. System access controls shall implement role-based access control (BR-019) with the additional requirement that access permissions shall be documented, periodically reviewed (per BR-026), and that all failed login attempts shall be logged and, after a configurable threshold (default: 5 attempts), the account shall be locked and an alert sent to the system administrator. CDOS shall support data integrity controls including: checksums on all electronic records to detect unauthorized modification, session timeouts requiring re-authentication after a configurable period of inactivity (default: 30 minutes), and prohibition of concurrent editing of the same record by multiple users without explicit locking. The system shall be validated per GxP computer system validation (CSV) requirements (BR-011) and shall produce compliance reports demonstrating Part 11 adherence for regulatory inspection.

### 4. Preconditions

- [ ] CDOS user management and role-based access control (BR-019) are implemented and operational.
- [ ] A centralized identity provider (IdP) supporting SAML 2.0 or OpenID Connect is available for user authentication and unique user ID management.
- [ ] The CDOS infrastructure has been provisioned with tamper-evident storage for audit trail records (e.g., append-only database tables, blockchain-anchored hashes, or write-once storage).

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-009-AC01 | Immutable audit trail | A Subject record with DOB = 1985-03-15 exists in CDOS | A data manager corrects the DOB to 1985-05-13 and provides a reason "Data entry error corrected per source document" | An audit trail record is created containing: user ID of the data manager, UTC timestamp, entity type (Subject), record ID, field (DOB), previous value (1985-03-15), new value (1985-05-13), reason ("Data entry error corrected per source document"); the audit trail record cannot be modified or deleted by any user including administrators |
| BR-009-AC02 | Electronic signature | A biostatistician has finalized an ADaM dataset for a study | The biostatistician applies an electronic signature with meaning "Approved for submission" | The signature record captures: user ID, authentication method (password), UTC timestamp, signature meaning ("Approved for submission"), linked ADaM dataset version; the signed dataset becomes read-only and any subsequent modification requires a new signature with a new version |
| BR-009-AC03 | Failed login lockout | A user account exists with active status | 5 consecutive failed login attempts occur within 15 minutes | The account is locked, a security event is logged with IP address and timestamp, an alert email is sent to the system administrator, and the account remains locked until an administrator explicitly unlocks it |
| BR-009-AC04 | Session timeout | An authenticated user is idle in a CDOS session | 30 minutes of inactivity elapse (configurable per deployment) | The session is terminated, the user is redirected to the login screen, and a session timeout event is logged in the audit trail; any unsaved work is preserved as a draft with a recovery option |
| BR-009-AC05 | Audit trail tamper detection | CDOS audit trail records exist in the database | A database administrator attempts to directly modify or delete an audit trail record via database tooling | The modification is blocked by database-level constraints (append-only); if bypassed via backup/restore or other means, a checksum integrity check during the nightly compliance scan detects the discrepancy and generates a critical security alert |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-019 | Blocks | Role-based access control is a prerequisite for user identification and permission enforcement |
| BR-011 | Enables | GxP CSV support provides the validation framework needed to demonstrate Part 11 compliance |
| BR-025 | Enables | Audit trail reporting provides the compliance reports needed for regulatory inspection |
| BR-026 | Enables | Periodic access reviews ensure ongoing compliance with Part 11 access control requirements |
| BR-021 | Related | Electronic informed consent (eConsent) relies on Part 11-compliant electronic signatures |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS API Gateway | Reads from / Writes to | All API requests pass through authentication, authorization, and audit trail middleware |
| CDOS Canonical Data Store | Reads from / Writes to | All data mutations are intercepted by the audit trail layer; data integrity checksums are computed and stored |
| CDOS Identity Service | Reads from / Writes to | User authentication, session management, and failed login tracking are managed by the identity service integrated with the IdP |
| CDOS Audit Trail Store | Writes to | Immutable, append-only store for all audit trail records; separate from the canonical data store to prevent co-mingling and tampering |
| CDOS Signature Service | Reads from / Writes to | Electronic signature capture, verification, and binding to signed records |
| All external systems (EDC, LIMS, IWRS, Safety) | Syncs with | Audit trail events from external system data ingestion are captured in CDOS audit trail with source system attribution |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Subject | Create, Read, Update | All Subject data mutations generate audit trail records |
| AdverseEvent | Create, Read, Update | All AdverseEvent data mutations generate audit trail records |
| LabResult | Create, Read, Update | All LabResult data mutations generate audit trail records |
| Dose | Create, Read, Update | All Dose data mutations generate audit trail records |
| Medication | Create, Read, Update | All Medication data mutations generate audit trail records |
| Query | Create, Read, Update | All Query lifecycle events generate audit trail records |
| CRFPage | Create, Read, Update | All CRFPage data mutations generate audit trail records |
| Submission | Create, Read, Update | All Submission lifecycle events and electronic signatures generate audit trail records |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A system administrator needs to correct a data error that was introduced by a system bug (not a user error) | The correction shall be performed via a documented administrative override process that requires: (1) a support ticket with root cause documentation, (2) approval by a second administrator, (3) an audit trail record that tags the event as "system correction" with the support ticket reference, and (4) a compliance report entry for QA review |
| A user's electronic signature on a dataset is later found to be applied to an incorrect version due to a race condition | The system shall prevent this by enforcing a record-level lock during the signature workflow; if a lock cannot be acquired (e.g., another user is editing), the signature request shall be rejected with a clear error message, and the user shall be prompted to retry after the lock is released |
| Regulatory inspector requests audit trail data for a study conducted 5 years ago, but the original system infrastructure has been migrated | Audit trail data shall be preserved in a format-independent, tamper-evident archive with cryptographic integrity verification; the archive shall be readable independent of the original CDOS infrastructure, and a compliance report shall demonstrate chain of custody from creation to archive |
| A subject exercises their GDPR right to erasure, which conflicts with the need to maintain immutable audit trails | The system shall pseudonymize the subject's personal data in the canonical records while preserving the audit trail with pseudonymized identifiers; the mapping between original and pseudonymized identifiers shall be stored in a separate, access-restricted data store with its own audit trail |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| FDA issues a warning letter or clinical hold due to inadequate audit trail or electronic signature controls | High | Critical | Implement Part 11 compliance as a foundational architecture requirement, not a feature add-on; validate before any study data is entered |
| Regulatory submission is rejected because the FDA cannot verify data integrity for the submitted datasets | Medium | Critical | Generate automated Part 11 compliance reports with each submission package; include audit trail summaries in the submission |
| Sponsor loses confidence in CDOS as a validated system and reverts to legacy EDC/CTMS with known Part 11 compliance | Medium | High | Engage sponsor QA teams early in the validation process; provide transparent access to compliance documentation and audit trail functionality |

### 11. Assumptions

- CDOS will be deployed in a validated state (per BR-011) before any study data is entered; Part 11 compliance is a go/no-go criterion for production deployment.
- The CDOS deployment environment provides the necessary infrastructure for tamper-evident storage (e.g., append-only database configurations, encrypted storage at rest, TLS in transit).
- Electronic signatures in CDOS use the "safe electronic signature" approach per FDA guidance (unique user ID + password as two distinct components), not digital certificates, unless the deploying organization requires PKI-based signatures.
- Audit trail data retention meets or exceeds the regulatory retention period for clinical trial data (typically 15-25 years post-approval per ICH E6(R2) and local regulations).
- Integration with a centralized IdP (e.g., Azure AD, Okta, Ping Identity) is available at the deployment site; CDOS does not maintain its own user credential store.

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [Sponsor QA Director] | Pending |
| CRO | [CRO Compliance Officer] | Pending |
| Regulatory | [Regulatory Affairs VP] | Pending |
| QA | [QA Systems Validation Manager] | Pending |


---

# Business Requirements: BR-010 and BR-011

---

## BR-010: GDPR and Data Privacy Compliance

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-010 |
| **Title** | GDPR and Data Privacy Compliance |
| **Priority** | P0 |
| **Category** | Compliance |
| **Source Stakeholder Need(s)** | SN-021, SN-018 |
| **Regulatory Basis** | GDPR (Regulation (EU) 2016/679) — Articles 4(5), 15–22, 44–49, 7, 6; 21 CFR Part 11; HIPAA Privacy Rule |
| **Status** | Draft |

### 2. Business Rationale

Clinical trials increasingly operate across EU member states and other jurisdictions with stringent data privacy laws. Under GDPR, the processing of special-category health data (Article 9) requires explicit consent and robust safeguards. Failure to comply exposes the organization to fines of up to €20 million or 4% of global annual turnover, whichever is higher. Beyond financial penalties, non-compliance erodes patient trust and can trigger regulatory holds on ongoing studies. Currently, pseudonymization of subject identifiers is performed manually in disparate systems, and data subject rights requests (access, rectification, erasure) are handled via ad-hoc spreadsheets — a process that takes 10–15 business days and is error-prone. The CDOS must embed privacy-by-design and privacy-by-default principles into its core data model and processing workflows to ensure continuous compliance across all active studies.

### 3. Detailed Description

The CDOS shall implement a comprehensive data privacy framework that covers the full lifecycle of personal data in clinical trials. When subject data enters the system — whether from EDC, eCOA, ePRO, lab, or wearable sources — the system must automatically pseudonymize direct identifiers (name, date of birth, national ID, contact details) by replacing them with a study-specific pseudonymous key. The original identifiers must be stored in a separate, access-controlled "re-identification vault" accessible only to authorized site personnel under dual-control. The system must maintain a mapping between pseudonymous keys and real identities, encrypted at rest with AES-256 and in transit with TLS 1.3.

For data subject rights, the system must provide self-service and administrator-initiated workflows for: (a) right of access — generating a structured export of all data held about a subject within 72 hours; (b) right to rectification — allowing authorized site users to correct inaccurate data with a full audit trail; (c) right to erasure ("right to be forgotten") — with automated checks for legal retention obligations (e.g., regulatory requirement to retain trial data for 15–25 years post-approval); and (d) right to data portability — exporting data in a machine-readable, interoperable format (JSON, CDISC ODM XML).

Consent management must track granular consent per data processing purpose (trial participation, biomarker research, future contact) with timestamps, consent version, and withdrawal capability. When consent is withdrawn for a specific purpose, the system must automatically halt processing for that purpose and notify downstream systems. Data residency requirements must be enforced at the study level — the system must ensure that subject data is stored and processed only in geographically approved regions (e.g., EU-only for EU subjects) as configured in the study setup. All privacy-related events (consent changes, data subject requests, pseudonymization operations, cross-border transfers) must be logged in an immutable, tamper-evident audit log.

### 4. Preconditions

- [ ] CDOS core data model and canonical Subject entity are defined and deployed
- [ ] Role-Based Access Control (RBAC) framework (BR-009) is implemented
- [ ] Encryption infrastructure (key management, TLS certificates) is provisioned
- [ ] Legal/Privacy team has approved the consent language and data processing purposes per study
- [ ] Data Processing Agreements (DPAs) are in place with all third-party processors

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-010-AC01 | Automatic pseudonymization | A subject record with direct identifiers is ingested from any source system | The data reaches the CDOS ingestion layer | Direct identifiers are replaced with a study-specific pseudonymous key; original identifiers are stored only in the re-identification vault; pseudonymized data is written to the canonical Subject entity |
| BR-010-AC02 | Data subject access request | A subject's pseudonymous key is known and the requester has the "Privacy Officer" role | A "Right of Access" request is submitted | The system generates a complete data export for that subject within 72 hours in structured format (JSON and PDF), including all processing purposes and consent history |
| BR-010-AC03 | Consent withdrawal and processing halt | A subject has consented to trial participation and biomarker research | The subject withdraws consent for biomarker research via the consent management UI | Biomarker data processing halts immediately; the consent record is updated with withdrawal timestamp; a notification is sent to the data management team; trial participation data processing continues unaffected |
| BR-010-AC04 | Data residency enforcement | A study is configured with "EU-only" data residency | An integration attempt routes subject data to a non-EU processing node | The system rejects the transfer and logs a data residency violation event with full context |
| BR-010-AC05 | Erasure with retention check | A subject requests data erasure and the study has a 15-year regulatory retention obligation | A "Right to Erasure" request is submitted | The system erases all non-regulated personal data; regulated data is flagged for restricted processing and scheduled for deletion at the end of the retention period; the subject receives a written explanation of partial erasure with legal basis |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-009 (Role-Based Access Control) | Blocks | Pseudonymized data and the re-identification vault require fine-grained RBAC to restrict access |
| BR-004 (Canonical Data Model) | Blocks | Subject entity and identifier fields must be defined before pseudonymization logic can be applied |
| BR-011 (GxP CSV Support) | Related | Validation documentation must cover privacy-related configurations |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC | Reads from | Ingests raw subject identifiers that must be pseudonymized at the CDOS boundary |
| eCOA / ePRO | Reads from | Subject-reported data linked via pseudonymous key |
| Consent Management Module | Writes to | Creates, updates, and reads consent records with full version history |
| Re-Identification Vault | Creates, Reads | Separate encrypted store for mapping pseudonymous keys to real identities |
| Audit / Compliance Log | Writes to | All privacy events are written to immutable audit log |
| Data Export Service | Reads from | Generates data subject access and portability exports |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Subject | Create, Read, Update | Core subject record with pseudonymized identifiers |
| SubjectIdentifier | Create, Read | Mapping between pseudonymous key and real identity (vault only) |
| Consent | Create, Read, Update | Granular consent records per processing purpose with version history |
| DataSubjectRequest | Create, Read, Update | Tracks access, rectification, erasure, and portability requests through workflow states |
| DataResidencyPolicy | Read | Study-level configuration defining approved geographic regions for data processing |
| PrivacyAuditEvent | Create, Read | Immutable log of all privacy-related operations |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Subject enrolled in multiple studies across different sponsors | Each study uses a distinct pseudonymous key; cross-study linkage requires explicit sponsor approval and documented legal basis |
| Consent withdrawal for trial participation while safety reporting is required | System marks subject as withdrawn from active participation; safety data processing continues under "vital interest" legal basis (GDPR Art. 6(1)(d)); subject is notified |
| Data subject access request for a deceased patient | Request is processed by authorized legal representative; system verifies representative authority before releasing data |
| Cross-border data transfer to a country without EU adequacy decision | System requires Standard Contractual Clauses (SCCs) or Binding Corporate Rules (BCRs) to be attached to the transfer configuration; transfer is blocked if no valid legal mechanism is documented |
| Pseudonymization key compromise | System triggers emergency key rotation; all affected mappings are re-encrypted; incident is logged and Privacy Officer is notified within 24 hours |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| GDPR fines up to €20M or 4% of global revenue | High | Critical | No alternative — regulatory requirement for EU trial operations |
| Patient trust erosion leading to recruitment difficulties | Medium | High | Transparent privacy notices and consent UX partially mitigate, but systemic compliance requires platform support |
| Regulatory inspection findings (EMA, national DPAs) | High | High | Manual processes are unsustainable at scale; automation reduces human error |
| Data breach exposing identifiable subject information | Medium | Critical | Pseudonymization reduces the blast radius; without it, any breach exposes full identities |

### 11. Assumptions

- The organization's Data Protection Officer (DPO) will define the approved data processing purposes and consent language per study
- GDPR applies to the majority of studies in the CDOS pipeline; non-EU studies may use a relaxed configuration but pseudonymization remains a best practice
- The re-identification vault will be operated under dual-control (site physician + privacy officer) and will not be accessible to CRO or sponsor personnel
- Standard Contractual Clauses (SCCs) templates will be provided by the Legal team

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [TBD] | Pending |
| CRO | [TBD] | Pending |
| Site | [TBD] | Pending |
| Privacy / Legal | [TBD] | Pending |
| QA / Compliance | [TBD] | Pending |

---

## BR-011: GxP Computer System Validation Support

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-011 |
| **Title** | GxP Computer System Validation Support |
| **Priority** | P1 |
| **Category** | Compliance |
| **Source Stakeholder Need(s)** | SN-026, SN-027, SN-018 |
| **Regulatory Basis** | 21 CFR Part 11, EU Annex 11, ICH E6(R2) Section 5.5, GAMP 5 (2nd Edition), ISPE GAMP Guide for Records and Data Integrity |
| **Status** | Draft |

### 2. Business Rationale

Every computerized system used in GxP-regulated clinical trials must be validated to demonstrate that it operates as intended, consistently produces reliable results, and maintains data integrity throughout its lifecycle. Currently, computer system validation (CSV) is a manual, document-heavy process: QA teams spend 4–8 weeks per major release assembling requirements traceability matrices (RTMs), writing validation protocols (IQ/OQ/PQ), and executing manual test scripts. Configuration changes are tracked in spreadsheets rather than version control, leading to configuration drift between environments. Validation report generation requires copying test results from multiple tools into Word documents — a process prone to copy-paste errors and inconsistencies discovered during regulatory inspections. The CDOS must natively support the CSV lifecycle by providing automated requirements-to-test traceability, version-controlled configuration management, and one-click generation of validation evidence reports. This reduces validation cycle time by 60–70% and ensures the system is always in an inspection-ready state.

### 3. Detailed Description

The CDOS shall provide a built-in GxP validation framework that spans the full system lifecycle — from requirements through design, build, test, deploy, and operate. The system must maintain a bidirectional traceability matrix linking each business requirement (BR) to functional specifications (FS), design elements, code commits, test cases, and test execution results. When a requirement changes, the system must automatically identify all downstream artifacts (specs, code, tests) that are impacted and flag them for review or re-validation.

For configuration management, all system configuration parameters (study setup, edit checks, workflow rules, role definitions, integration endpoints, environment variables) must be stored in version-controlled repositories with full commit history, branching, and merge capabilities. Configuration changes must follow a formal change control workflow: draft → review → approve → deploy → verify. Each configuration change must be linked to a change request record that documents the rationale, risk assessment, approvers, and affected studies. The system must support environment promotion (DEV → TEST → PROD) with automated validation gates that verify configuration consistency between environments before promotion is approved.

For validation reporting, the system must generate on-demand validation evidence packages that include: (a) Installation Qualification (IQ) — confirming software version, infrastructure configuration, and installed components match specifications; (b) Operational Qualification (OQ) — confirming all functional requirements operate correctly under normal conditions with links to automated test results; (c) Performance Qualification (PQ) — confirming the system performs reliably under production-like load with performance benchmarks. These reports must be generated in PDF format with electronic signature capability (21 CFR Part 11 compliant) and stored in a validated document management system. The system must also produce a requirements-to-test traceability matrix (RTM) that shows, for every requirement, the linked test cases, their last execution status, and the date of last execution — enabling QA to demonstrate continuous validation compliance at any point.

### 4. Preconditions

- [ ] Business requirements (BR-001 through BR-025+) are documented in the CDOS requirements repository
- [ ] A CI/CD pipeline is established with automated test execution
- [ ] A version-controlled configuration repository (e.g., Git-based) is provisioned
- [ ] GAMP 5 system categorization is completed for each CDOS component
- [ ] QA team has defined the validation policy, including risk-based approach per GAMP 5

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-011-AC01 | Automated traceability matrix | Business requirements, functional specs, and test cases are linked in the CDOS traceability repository | A QA user requests the requirements traceability matrix for a given release | The system generates a complete RTM showing every BR → FS → Code → Test Case → Test Result chain, with pass/fail status and execution timestamps, exportable as CSV and PDF |
| BR-011-AC02 | Impact analysis on requirement change | A business requirement is modified by an authorized user | The requirement change is saved | The system automatically identifies and lists all downstream functional specs, code modules, and test cases impacted by the change; assigns "Review Required" status to each impacted artifact; notifies the responsible owners |
| BR-011-AC03 | Version-controlled configuration | Study configuration parameters are defined in the CDOS configuration module | A configuration change is submitted | The change is committed to the version-controlled repository with commit message, author, timestamp, linked change request ID, and diff showing the exact change; previous versions remain accessible |
| BR-011-AC04 | Environment promotion with validation gates | A configuration change has been approved for production deployment | The change is promoted from TEST to PROD environment | The system runs an automated configuration consistency check; if the check passes, the promotion proceeds and a promotion audit record is created; if it fails, the promotion is blocked with a detailed diff report |
| BR-011-AC05 | Validation report generation | Automated tests have been executed for a release candidate | A QA user requests an OQ validation report | The system generates a PDF report including: test case inventory, execution results with pass/fail/skip status, defect references, environment details, and a summary signature block; the report is available for electronic signature |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 through BR-010 (all prior BRs) | Related | Every BR defines requirements that must be traceable in the RTM |
| BR-009 (Role-Based Access Control) | Blocks | Change control and approval workflows require role-based permissions |
| BR-004 (Canonical Data Model) | Related | Data model changes must be tracked under version control |
| CI/CD Pipeline (infrastructure) | Blocks | Automated test execution and environment promotion depend on CI/CD tooling |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| Requirements Management Repository | Creates, Reads, Updates | Stores BRs, FS, and traceability links |
| Version Control System (Git) | Creates, Reads | Stores all configuration artifacts with full history |
| CI/CD Pipeline | Syncs with | Triggers automated test execution; reads test results for validation reports |
| Change Control Module | Creates, Reads, Updates | Manages change request lifecycle (draft → approve → deploy) |
| Document Management System | Writes to | Stores generated validation reports (IQ/OQ/PQ) with electronic signatures |
| All CDOS Modules | Reads from | All module configurations are subject to version control and validation |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| BusinessRequirement | Read | Source requirements for traceability |
| FunctionalSpecification | Read | Design specifications linked to requirements |
| TestCase | Read, Update | Test cases linked to specifications; execution status tracked |
| TestExecutionResult | Create, Read | Results of automated and manual test runs |
| TraceabilityLink | Create, Read | Bidirectional links between BR → FS → Code → Test |
| ConfigurationItem | Create, Read, Update | Version-controlled configuration parameters |
| ChangeRequest | Create, Read, Update | Formal change control records with approval workflow |
| ValidationReport | Create, Read | Generated IQ/OQ/PQ reports with signature blocks |
| EnvironmentPromotionRecord | Create, Read | Audit trail for configuration promotions between environments |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A requirement has no linked test cases | The RTM highlights the gap with a "No Test Coverage" warning; the requirement cannot be marked as validated until at least one test case is linked and passing |
| Configuration change rejected during promotion gate | Promotion is blocked; the change request is returned to "Rework" status with the consistency check diff report attached; the submitter and approver are notified |
| Emergency hotfix deployed without full change control | The system allows the deployment under an "Emergency Change" workflow but automatically creates a retroactive change request that must be completed and approved within 72 hours; the emergency event is flagged in the next validation report |
| Test case fails in PROD but passed in TEST | The system flags an environment discrepancy; an investigation record is auto-created linking the test failure, environment configs, and relevant change requests |
| Legacy system migration where source requirements are unstructured | The system supports bulk import of requirements from CSV/Excel with manual traceability linking; a "Traceability Gap Report" identifies unlinked artifacts |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Regulatory inspection findings for inadequate CSV | High | Critical | Manual validation is possible but unsustainable; leads to 4–8 week validation cycles per release |
| Configuration drift between DEV, TEST, and PROD environments | High | High | Manual config tracking in spreadsheets is error-prone; no automated consistency checks |
| Delayed releases due to lengthy manual validation | High | High | Releases are held pending validation documentation, adding 4–8 weeks to release cycles |
| Incomplete traceability leading to re-validation scope creep | Medium | High | Without automated impact analysis, QA must re-validate broadly rather than surgically |

### 11. Assumptions

- The CDOS will be classified as GAMP 5 Category 4 (Configured Product) or Category 5 (Custom Application) depending on the component; validation approach will follow risk-based GAMP 5 principles accordingly
- Automated tests (unit, integration, end-to-end) are maintained by the development team and are available in the CI/CD pipeline
- Electronic signatures on validation reports will comply with 21 CFR Part 11 (unique user ID, signature meaning, signature date/time)
- The QA team will define the validation policy and acceptance criteria for IQ/OQ/PQ protocols prior to system deployment
- The organization will invest in a Git-based configuration repository and integrate it with the CDOS configuration management module

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [TBD] | Pending |
| CRO | [TBD] | Pending |
| Site | [TBD] | Pending |
| QA / Compliance | [TBD] | Pending |
| IT / DevOps | [TBD] | Pending |


---

# Business Requirements: BR-012 and BR-013

---

## BR-012: Cross-Study Dashboard

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-012 |
| **Title** | Cross-Study Dashboard |
| **Priority** | P0 |
| **Category** | Analytics |
| **Source Stakeholder Need(s)** | SN-001, SN-003, SN-008 |
| **Regulatory Basis** | ICH E6(R2) Section 5.0 (sponsor oversight obligations); 21 CFR Part 312.50 (sponsor responsibility for trial conduct) |
| **Status** | Draft |

### 2. Business Rationale

Sponsors and CRO leadership currently lack a consolidated, real-time view of clinical trial performance across their portfolio. Each study team reports metrics independently using a patchwork of spreadsheets, EDC system exports, and slide decks updated on weekly or biweekly cycles. This fragmentation means that executive-level decisions about resource allocation, milestone forecasting, and risk escalation are based on data that is 5-10 business days stale. In a typical mid-size portfolio of 15-25 active studies, this lag results in delayed identification of enrollment shortfalls (averaging 3-4 weeks before escalation) and an estimated 12-18% cost overrun per study due to late corrective action. A unified cross-study dashboard providing real-time metrics on enrollment, data entry timeliness, query rates, adverse event counts, and milestone status would enable proactive portfolio management and reduce mean time-to-detect for critical issues from weeks to hours.

### 3. Detailed Description

The CDOS shall provide a configurable, role-based cross-study dashboard that aggregates key operational and safety metrics from all active clinical trials into a single pane of glass. When a user with appropriate permissions (e.g., Sponsor Portfolio Manager, CRO Operations Director) navigates to the dashboard, the system shall display real-time or near-real-time (refreshed within 15 minutes) summary metrics across all studies the user is authorized to view.

The dashboard shall present the following primary metric categories: (a) enrollment status — including planned vs. actual randomization counts, screen failure rates, and enrollment velocity trends per study; (b) data entry timeliness — measuring the median and 90th-percentile lag between subject visit date and data entry completion, broken down by study and site; (c) query rates — showing open queries, queries older than 7/14/30 days, and query resolution velocity per study; (d) adverse event counts — displaying total AEs, SAEs, SUSARs, and AESIs by study with severity and causality breakdowns; and (e) milestone status — tracking key study milestones (site activation, first patient in, 50% enrollment, database lock target) against planned dates with variance indicators.

Users shall be able to filter the dashboard by study, phase, therapeutic area, CRO partner, region, and date range. The dashboard shall support drill-down from portfolio-level summaries to study-level detail and further to site-level data. Color-coded status indicators (green/yellow/red) shall be automatically assigned based on configurable thresholds for each metric. The system shall support export of dashboard data to PDF and CSV formats for offline distribution and board-level reporting. Dashboard configurations (filters, layout, threshold settings) shall be saveable per user and shareable across user groups.

### 4. Preconditions

- [ ] At least one study has been provisioned and is in an active state within CDOS
- [ ] EDC data feeds (or manual data loads) are flowing for enrolled subjects
- [ ] Milestone definitions and planned dates have been configured per study
- [ ] User roles and study-level access permissions have been defined
- [ ] Threshold values for metric status indicators have been configured by an administrator

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-012-AC01 | Real-time enrollment display | The user has access to 5 active studies with varying enrollment counts | The user opens the cross-study dashboard | All 5 studies display current enrolled count, screen failure rate, and enrollment velocity, with data no older than 15 minutes |
| BR-012-AC02 | Data entry timeliness metrics | Two studies have sites with data entry lag exceeding the configured threshold | The user views the data entry timeliness panel | Sites exceeding the threshold are flagged red; the user can drill down to see per-site median and 90th-percentile lag values |
| BR-012-AC03 | Query rate aggregation | Three studies have open queries, one study has queries older than 30 days | The user opens the query rate section | The dashboard displays total open queries per study, highlights the study with aged queries, and allows drill-down to see individual query details |
| BR-012-AC04 | AE count summary with safety signals | A study has reported 2 SAEs and 1 SUSAR in the current reporting period | The user views the adverse event panel | The SUSAR is highlighted with a red indicator; the user can filter by severity, causality, and MedDRA preferred term |
| BR-012-AC05 | Milestone tracking with variance | Study ABC has missed its 50% enrollment milestone by 14 days | The user views the milestone status section | Study ABC shows the milestone as overdue with a red indicator and displays the 14-day variance |
| BR-012-AC06 | Role-based filtering | A CRO Operations Director has access to 10 studies, but only 4 are assigned to their CRO | The CRO Operations Director logs in and opens the dashboard | Only the 4 assigned studies are displayed; no unauthorized study data is visible |
| BR-012-AC07 | Dashboard export | The user has configured a filtered view of 8 studies with selected metrics | The user clicks "Export to PDF" | A formatted PDF is generated containing all currently displayed metrics, filters, and status indicators |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (Data Integration Hub) | Blocks | Dashboard requires normalized data feeds from EDC and other source systems to populate metrics |
| BR-003 (Role-Based Access Control) | Blocks | Role-based filtering and study-level access control must be in place before dashboard can enforce data segregation |
| BR-005 (Audit Trail) | Related | Dashboard interactions (views, exports) should be logged for compliance; underlying data provenance supports metric accuracy |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC (e.g., Medidata Rave, Oracle InForm) | Reads from | Enrollment counts, data entry timestamps, query metadata, AE/SAE records |
| CDOS Analytics Engine | Writes to | Aggregated metric calculations, threshold evaluations, trend computations |
| CDOS Presentation Layer | Writes to | Dashboard rendering, user-configurable layouts, filter state persistence |
| IWRS/RTSM | Reads from | Randomization counts and drug assignment data for enrollment metrics |
| Safety Database (e.g., Argus) | Reads from | SAE and SUSAR counts, causality assessments for adverse event panel |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Study | Read | Study metadata, phase, therapeutic area, milestone definitions and planned dates |
| Site | Read | Site activation status, site-level enrollment and data quality metrics |
| Subject | Read | Enrollment status (screened, randomized, completed, withdrawn), visit schedules |
| Query | Read | Query open/close timestamps, aging, resolution status for query rate calculations |
| AdverseEvent | Read | AE, SAE, SUSAR counts, severity, causality, MedDRA coding for safety panel |
| Milestone | Read, Update | Milestone definitions, planned dates, actual dates, variance calculations |
| DashboardConfig | Create, Read, Update | User-specific dashboard layouts, saved filters, threshold configurations |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Study has zero enrolled subjects (pre-enrollment phase) | Dashboard displays study with "Not Yet Enrolled" status; enrollment metrics show as N/A rather than zero to avoid misleading trend calculations |
| Data feed from EDC is delayed or interrupted | Dashboard displays a "Data Staleness" warning banner with the timestamp of the last successful refresh; metrics are shown with a staleness indicator (e.g., amber clock icon) |
| User has access to a very large portfolio (100+ studies) | Dashboard defaults to a paginated or scrollable view with summary-level metrics; full detail is available via drill-down; performance target of <5 second load time is maintained |
| A study is temporarily unblinded for a DSMB review | Unblinded safety data is excluded from the dashboard unless the user has explicit unblinded access; a placeholder indicates data is temporarily restricted |
| Threshold values are changed by an administrator mid-study | Historical dashboard snapshots retain the threshold values in effect at the time of capture; current view reflects new thresholds immediately |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Delayed identification of enrollment shortfalls leading to extended study timelines and increased costs | High | High | Manual weekly reporting via spreadsheets (current state) — significant labor overhead and 3-4 week detection lag |
| Inability to detect data quality issues across the portfolio until database lock preparation | High | High | Periodic manual data review sprints — costly and retrospective rather than proactive |
| Sponsor dissatisfaction due to lack of transparency, potentially leading to CRO contract loss | Medium | High | Ad-hoc reporting by study teams — inconsistent quality and format |
| Regulatory scrutiny during inspection if sponsor cannot demonstrate active trial oversight | Medium | Medium | Binder-based documentation of oversight activities — labor-intensive and difficult to verify completeness |

### 11. Assumptions

- Source systems (EDC, IWRS, Safety DB) expose data via APIs or batch extract mechanisms that CDOS can consume with latency no greater than 15 minutes
- Milestone definitions and planned dates are entered by study teams during study setup and are kept current
- Metric threshold values are agreed upon by sponsor and CRO stakeholders during study configuration and are not changed without documented approval
- The initial dashboard release covers the five stated metric categories; additional metrics (e.g., site activation timelines, protocol deviation rates) may be added in subsequent releases
- Users have reliable network connectivity to access the web-based dashboard; offline caching is not in scope for the initial release

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | VP, Clinical Operations | Pending |
| CRO | Director, Clinical Trial Management | Pending |
| Site | Site Monitor Lead | Pending |
| Data Management | Head of Data Management | Pending |
| IT/Engineering | Platform Architect | Pending |

---

## BR-013: Risk-Based Monitoring Indicators

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-013 |
| **Title** | Risk-Based Monitoring Indicators |
| **Priority** | P1 |
| **Category** | Analytics |
| **Source Stakeholder Need(s)** | SN-005, SN-008 |
| **Regulatory Basis** | ICH E6(R2) Section 5.18.3 (risk-based monitoring); FDA Guidance "Oversight of Clinical Investigations" (2013); EMA Reflection Paper on Risk-Based Quality Management (2013) |
| **Status** | Draft |

### 2. Business Rationale

ICH E6(R2) explicitly requires sponsors to implement a risk-based approach to clinical trial monitoring, focusing resources on critical data and processes where risks to subject safety and data integrity are highest. However, most organizations today rely on static, visit-based monitoring schedules and manual review of site performance data to identify monitoring priorities. This approach is both resource-intensive (on-site monitoring visits cost $3,000-$8,000 each) and reactive — sites with emerging data quality issues are often not identified until after a pattern of errors has already impacted data integrity. Studies show that approximately 20-30% of monitoring visits target low-risk sites that would benefit from reduced oversight, while 10-15% of high-risk sites go undetected until a critical audit finding. Automated, data-driven risk indicators at the site level would enable CROs and sponsors to dynamically allocate monitoring effort where it is most needed, reduce unnecessary on-site visits by 30-40%, and detect emerging site-level issues 2-4 weeks earlier than current practices allow.

### 3. Detailed Description

The CDOS shall compute, display, and continuously update a set of site-level risk indicators that support risk-based monitoring (RBM) strategies as defined in the study's monitoring plan. The system shall ingest operational data from EDC, IWRS, and related systems to calculate three core indicator categories for every active site in every active study: (a) enrollment velocity — comparing each site's actual enrollment rate against its planned enrollment curve, expressed as a percentage of target and as a rolling 4-week velocity trend; (b) data completeness — measuring the percentage of expected CRF pages that have been entered (not necessarily resolved) for scheduled visits, broken down by form type and visit, with particular attention to critical data points (primary endpoints, safety assessments, eligibility criteria); and (c) query resolution time — tracking the median and 90th-percentile time from query issuance to resolution for each site, compared against the study-level benchmark.

For each indicator, the system shall compute a normalized risk score on a 0-100 scale, where higher scores indicate higher risk. The scoring algorithm shall be configurable per study to allow weight adjustments based on the study's specific risk assessment. The system shall combine individual indicator scores into a composite site risk score using configurable weights. Sites shall be automatically classified into risk tiers (e.g., Low < 30, Medium 30-60, High 60-80, Critical > 80) based on their composite score.

The system shall provide a dedicated Risk Indicators view accessible to monitors, clinical research associates (CRAs), study managers, and sponsor oversight personnel. This view shall display a sortable, filterable table of all sites with their risk scores and tier classifications, supporting drill-down to individual indicator detail and historical trend charts (minimum 12-week lookback). The system shall generate automated alerts when a site's composite risk score crosses a tier threshold (e.g., moves from Medium to High), sending notifications to the assigned CRA and study manager via in-app notification and email. Alert rules and notification recipients shall be configurable per study. All risk score calculations, threshold crossings, and alerts shall be logged in an immutable audit trail for regulatory inspection readiness.

### 4. Preconditions

- [ ] The study's monitoring plan, including risk categories and critical data/process definitions, has been documented and approved
- [ ] Target enrollment curves and site-level enrollment plans have been configured for each site
- [ ] CRF visit schedules and form expectations have been defined in the EDC or CDOS study configuration
- [ ] EDC data feeds are operational and delivering data with latency no greater than 6 hours
- [ ] Risk indicator weights and threshold values have been configured by the study team per the study risk assessment
- [ ] CRA-to-site assignments have been entered into the system for alert routing

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-013-AC01 | Enrollment velocity calculation | Site 101 has enrolled 8 subjects in 4 weeks against a plan of 12 | The system computes the enrollment velocity indicator | Site 101 shows 67% of target enrollment velocity; the indicator trend shows a declining trajectory compared to the prior 4-week period |
| BR-013-AC02 | Data completeness measurement | Site 205 has 45 expected CRF pages for completed visits; 38 have been entered, 7 are missing (2 are primary endpoint pages) | The system computes the data completeness indicator | Site 205 shows 84% overall completeness; the 2 missing primary endpoint pages are flagged as critical gaps, elevating the weighted completeness risk score |
| BR-013-AC03 | Query resolution time tracking | Site 310 has a median query resolution time of 18 days, compared to the study benchmark of 10 days | The system computes the query resolution time indicator | Site 310's query resolution indicator shows 180% of benchmark; the risk score for this indicator is elevated into the High tier |
| BR-013-AC04 | Composite risk score and tier assignment | Site 101 has indicator scores of: enrollment velocity = 45, data completeness = 70, query resolution = 55. Configured weights are 30%, 40%, 30% respectively | The system computes the composite risk score | Site 101 composite score = (45×0.3) + (70×0.4) + (55×0.3) = 13.5 + 28.0 + 16.5 = 58.0, classified as Medium tier |
| BR-013-AC05 | Threshold crossing alert | Site 205's composite risk score increases from 55 (Medium) to 62 (High) due to new data completeness issues | The system recalculates risk scores | An automated alert is sent to the assigned CRA and study manager via in-app notification and email within 15 minutes of the score crossing the 60-point threshold |
| BR-013-AC06 | Risk indicator drill-down and trend | The CRA selects Site 310 from the risk indicators table | The CRA clicks on the enrollment velocity indicator for Site 310 | A 12-week trend chart is displayed showing weekly enrollment counts vs. planned, with the velocity ratio plotted over time; the CRA can identify when the deviation began |
| BR-013-AC07 | Audit trail for risk score changes | The study manager reviews risk score history for Site 101 | The study manager opens the audit trail for Site 101 | The audit trail shows every score recalculation with timestamp, input data snapshot, and the resulting tier classification — all immutable and exportable |
| BR-013-AC08 | Configurable weights per study | Study ABC has a different risk weighting (enrollment = 20%, data completeness = 50%, query resolution = 30%) than the default | The study manager configures Study ABC's weights | All subsequent risk score calculations for Study ABC use the updated weights; previously calculated scores are not retroactively changed but are marked with the weight version that was in effect |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-012 (Cross-Study Dashboard) | Related | Risk indicator summaries should be embeddable as a widget within the cross-study dashboard; shared data model for site-level metrics |
| BR-001 (Data Integration Hub) | Blocks | Risk indicators require timely, normalized data from EDC and IWRS; the integration hub must be operational |
| BR-002 (CDISC Data Mapping) | Related | Critical data point identification for data completeness relies on CDISC domain and variable metadata to classify fields as primary endpoints, safety assessments, etc. |
| BR-005 (Audit Trail) | Blocks | Immutable logging of risk score calculations, threshold crossings, and alert events is required for regulatory compliance |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC (e.g., Medidata Rave, Oracle InForm) | Reads from | CRF entry timestamps, query metadata, visit completion dates, form-level data for completeness calculations |
| IWRS/RTSM | Reads from | Site-level randomization and enrollment data for enrollment velocity calculations |
| CDOS Analytics Engine | Writes to | Risk score computation, trend analysis, threshold evaluation, composite scoring logic |
| CDOS Alerting Service | Writes to | Threshold crossing notifications, alert routing to CRA and study manager |
| CDOS Presentation Layer | Writes to | Risk indicator views, sortable tables, trend charts, drill-down detail panels |
| CDOS Audit Service | Writes to | Immutable logging of all risk score calculations and alert events |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Site | Read | Site metadata, CRA assignment, enrollment plan, site activation date |
| Subject | Read | Per-site enrollment counts, visit schedules, visit completion status |
| CRFPage | Read | Form-level data entry status (entered, incomplete, missing) for completeness calculation |
| Query | Read | Query open/close timestamps per site for resolution time calculation |
| RiskIndicatorConfig | Create, Read, Update | Per-study configuration of indicator weights, thresholds, scoring parameters |
| RiskScore | Create, Read | Computed risk scores per site per indicator and composite; includes timestamp, input snapshot, and tier classification |
| RiskAlert | Create, Read | Threshold crossing events with affected site, indicator, old/new tier, notification recipients, and delivery status |
| MonitoringPlan | Read | Study-level monitoring plan defining critical data points, risk categories, and monitoring strategy |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Site has been activated but has zero subjects enrolled | Enrollment velocity indicator shows 0% of target with a "No Enrollment" flag; composite risk score applies maximum risk weight to the enrollment indicator to flag the site for review |
| Site is on administrative hold (e.g., pending contract renewal) | The site is excluded from active risk scoring while on hold; a visual indicator shows the site is in hold status; risk scoring resumes automatically when the hold is lifted |
| EDC data feed is delayed beyond the 6-hour SLA | Risk indicators for affected studies display a "Data Feed Delayed" warning; scores are calculated on the most recent available data with a staleness flag; no alerts are suppressed — they fire based on available data with a delay advisory |
| A critical data point is added to the CRF after study start | The data completeness algorithm detects the new field on the next calculation cycle; historical completeness scores are not retroactively recalculated, but future scores include the new field |
| Two sites have identical composite scores but different indicator profiles | The risk indicator table sorts by composite score as primary key and allows secondary sort by any individual indicator; drill-down reveals the different indicator profiles for informed prioritization |
| A site's risk score fluctuates rapidly around a tier threshold | The alerting system implements a hysteresis mechanism — an alert fires only when the score crosses a threshold and remains above it for two consecutive calculation cycles (configurable); this prevents alert fatigue from oscillating scores |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Non-compliance with ICH E6(R2) risk-based monitoring requirements, leading to regulatory findings during inspection | High | High | Maintain manual risk assessment spreadsheets and static monitoring visit schedules — accepted by some regulators but increasingly questioned |
| Over-allocation of monitoring resources to low-risk sites while high-risk sites receive insufficient attention | High | Medium | Rely on CRA experience and intuition to prioritize site visits — inconsistent and not scalable |
| Late detection of site-level data quality issues, resulting in costly data cleaning at database lock | Medium | High | Conduct periodic centralized monitoring sprints — labor-intensive and retrospective |
| Inability to demonstrate a systematic, data-driven approach to monitoring to sponsors and regulators | Medium | Medium | Document risk assessments in static plans without real-time data linkage — difficult to defend during inspection |

### 11. Assumptions

- Each site has a defined enrollment target and timeline, entered during study setup, which serves as the baseline for enrollment velocity calculations
- The EDC system exposes form-level entry status (entered vs. not entered) at a granularity sufficient to compute data completeness per CRF page per visit
- Query metadata (open date, close date, status) is available from the EDC system via API or data feed with latency no greater than 6 hours
- The study team will define and maintain a list of critical data points (primary endpoints, key safety assessments, eligibility criteria) during study setup, which the system uses to weight data completeness calculations
- Risk indicator weights and thresholds are set during study setup based on the protocol risk assessment and are not modified without documented approval from the study medical monitor and sponsor
- CRA-to-site assignments are maintained in the system and updated within 5 business days of any personnel change

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | Director, Clinical Monitoring Oversight | Pending |
| CRO | Head of Risk-Based Monitoring | Pending |
| Site | Lead CRA | Pending |
| Regulatory Affairs | VP, Regulatory Strategy | Pending |
| Quality Assurance | Director, GCP Compliance | Pending |
| IT/Engineering | Data Platform Lead | Pending |


---

# Business Requirements: BR-014 and BR-015

---

## BR-014: Enrollment Forecasting

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-014 |
| **Title** | Enrollment Forecasting |
| **Priority** | P1 |
| **Category** | Analytics |
| **Source Stakeholder Need(s)** | SN-003 (Cost and Timeline Predictability), SN-008 (Operational Dashboards) |
| **Regulatory Basis** | ICH E6(R2) §5.0 — Sponsor responsibility to ensure adequate enrollment to meet study objectives |
| **Status** | Draft |

### 2. Business Rationale

Enrollment delays are the single largest driver of clinical trial cost overruns and timeline slippage, accounting for nearly 80% of trials failing to meet original enrollment timelines. Sponsors currently rely on manual spreadsheet-based forecasting that is updated infrequently and fails to account for site-level variability, screening pipeline dynamics, or seasonal patterns such as holidays and disease-seasonality effects. Without an automated, data-driven forecasting capability, sponsors cannot proactively identify under-enrolling sites, reallocate resources, or provide accurate timeline estimates to internal governance boards and external partners. This lack of predictability erodes stakeholder confidence and delays critical go/no-go decisions for downstream development activities.

### 3. Detailed Description

The CDOS shall provide an automated enrollment forecasting engine that generates rolling predictions of cumulative and per-site enrollment over the remaining life of each study. The system shall ingest historical enrollment performance data from completed and ongoing studies, current screening pipeline data (pre-screened, screened, screen-failed, enrolled, withdrawn), and known seasonal or calendar-based modifiers (holiday periods, disease-seasonality curves, site vacation schedules). When a study is activated or when new enrollment data is received (daily batch or near-real-time via EDC integration), the forecasting model shall regenerate predictions. The system shall produce forecasts at multiple levels of granularity: per-study aggregate, per-site, per-region, and per-treatment arm. Forecasts shall be presented as point estimates with confidence intervals (80% and 95%) and shall flag sites or studies where the predicted enrollment trajectory falls below the enrollment target by more than 15%. The system shall also support scenario-based forecasting, allowing users to adjust assumptions (e.g., adding a new site, modifying inclusion/exclusion criteria) and see the projected impact on enrollment timelines. All forecasts shall be versioned and logged so that forecast accuracy can be retrospectively evaluated and model performance improved over time.

### 4. Preconditions

- [ ] Study has been activated in the CDOS study configuration module with enrollment targets and timelines defined
- [ ] At least one site has begun screening activities and is transmitting screening pipeline data to CDOS
- [ ] Historical enrollment data from at least two comparable completed studies is available in the CDOS data warehouse for model training and calibration
- [ ] Site metadata (country, region, site type, PI experience level) is populated in the CDOS master data

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-014-AC01 | Initial forecast generation | A study is activated with enrollment targets, and screening data is flowing from at least 5 sites | The forecasting engine runs its first scheduled cycle | A per-site and aggregate enrollment forecast is generated with point estimates and 80%/95% confidence intervals, displayed on the enrollment dashboard within 15 minutes of data refresh |
| BR-014-AC02 | Under-enrollment alert | A study has 20 active sites with historical and current screening data | The forecasting model predicts cumulative enrollment will fall below the study target by more than 15% at the current trajectory | The system generates a high-priority alert to the study manager and sponsor dashboard, including the projected shortfall, contributing factors (e.g., slow sites, high screen-failure rate), and recommended corrective actions |
| BR-014-AC03 | Scenario-based what-if analysis | A study manager is viewing the enrollment forecast for an ongoing study | The manager adds a hypothetical new site with specified expected performance and re-runs the forecast | The system recalculates the enrollment trajectory within 5 minutes, showing the delta from the baseline forecast and updated confidence intervals |
| BR-014-AC04 | Forecast accuracy tracking | A study has been enrolling for at least 6 months with monthly forecasts generated | A data manager requests a forecast accuracy report for the study | The system produces a report comparing each historical forecast against actual enrollment, showing mean absolute percentage error (MAPE) and bias metrics, stratified by site and time horizon |
| BR-014-AC05 | Seasonal pattern recognition | Historical enrollment data spans multiple calendar years with observable holiday and disease-seasonality dips | The forecasting engine generates a 12-month forward forecast | The model incorporates seasonal adjustment factors derived from historical patterns, and the forecast visualization clearly annotates predicted seasonal dips |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (Unified Data Integration Layer) | Blocks | The forecasting engine requires normalized screening and enrollment data from the canonical data model |
| BR-003 (Operational Dashboard Framework) | Enables | Forecast visualizations and alerts are rendered within the existing dashboard infrastructure |
| BR-005 (Study Configuration and Metadata Management) | Related | Study enrollment targets, timelines, and site metadata must be configured before forecasting can operate |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC | Reads from | Ingests screening and enrollment data (screened, enrolled, screen-failed, withdrawn timestamps) |
| CDOS Analytics Engine | Writes to | Stores forecast outputs, confidence intervals, accuracy metrics, and scenario results |
| CDOS Operational Dashboard | Writes to | Pushes forecast visualizations, alerts, and trend charts to the sponsor and CRO dashboards |
| IWRS / RTSM | Reads from | Reads randomization and drug assignment data to align enrollment forecasts with treatment arm capacity |
| CDOS Alerting Service | Writes to | Triggers notifications when enrollment trajectory deviates from targets |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| EnrollmentForecast | Create, Read | Predicted enrollment trajectory per study/site with confidence intervals |
| EnrollmentForecastScenario | Create, Read | What-if scenario inputs and outputs for alternative enrollment assumptions |
| ScreeningPipeline | Read | Current state of subjects in the screening funnel (pre-screened, screened, screen-failed, enrolled) |
| SitePerformance | Read | Historical and current site enrollment rates, screen-failure rates, and activation timelines |
| StudyEnrollmentTarget | Read | Approved enrollment targets, timelines, and treatment arm quotas |
| ForecastAccuracyReport | Create, Read | Retrospective comparison of forecasted vs. actual enrollment with error metrics |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A site has zero screening activity for 30+ consecutive days | The system flags the site as inactive, excludes it from the active forecast, and notifies the study manager. The site is re-included automatically upon data resumption. |
| Protocol amendment changes eligibility criteria mid-study | The system detects the amendment date, applies a structural break in the forecasting model, and generates separate pre- and post-amendment forecasts with a transition period |
| A new site is added with no historical data in CDOS | The system uses a Bayesian prior derived from the mean and variance of comparable existing sites in the same region and therapeutic area |
| External event causes a sudden enrollment spike (e.g., media coverage of the disease) | The system detects an outlier in the screening data trend and flags it as an anomalous event rather than smoothing it into the baseline forecast, prompting manual review |
| Forecast model produces conflicting signals (e.g., improving site-level rates but declining aggregate due to site closures) | The system presents decomposed forecast contributions (site additions, site closures, rate changes) as a waterfall chart in the dashboard |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Continued reliance on manual spreadsheets leads to inaccurate enrollment projections and budget overruns | High | High | Maintain current manual process with quarterly external reviews |
| Sponsors cannot make timely decisions about site remediation or study rescue, leading to extended enrollment periods | High | High | Implement basic trend reporting without predictive modeling |
| Loss of competitive advantage as industry moves toward AI-driven trial management | Medium | Medium | Partner with third-party forecasting vendors |
| Regulatory agencies question enrollment feasibility in IND/CTA submissions without data-driven projections | Medium | Medium | Provide narrative justifications in regulatory submissions |

### 11. Assumptions

- Historical enrollment data from at least two comparable studies is available to train and validate the forecasting model; if not, the system will operate in a limited "trend extrapolation" mode until sufficient data accumulates
- Screening pipeline data from EDC systems is accurate and arrives within 24 hours of site entry
- Site performance characteristics (PI experience, patient pool size) are reasonably stable over the enrollment period; major site-level disruptions will be handled as edge cases
- The organization accepts that forecasting accuracy will improve over time as more data accumulates and models are retrained, and initial forecasts may have wider confidence intervals

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | TBD | Pending |
| CRO | TBD | Pending |
| Site | TBD | Pending |
| Data Management / Biostatistics | TBD | Pending |

---

## BR-015: Regulatory Submission Package Assembly

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-015 |
| **Title** | Regulatory Submission Package Assembly |
| **Priority** | P1 |
| **Category** | Compliance |
| **Source Stakeholder Need(s)** | SN-002 (Regulatory Submission Readiness), SN-015 (Standards-Compliant Submissions) |
| **Regulatory Basis** | ICH M8 (eCTD v4.0), FDA 21 CFR Part 312/314, EMA eCTD guidance, CDISC SDTM/ADaM Implementation Guides, Define-XML v2.1 specification |
| **Status** | Draft |

### 2. Business Rationale

Regulatory submission preparation is one of the most resource-intensive and error-prone activities in clinical development, typically consuming 3-6 months of dedicated effort by data management, biostatistics, and regulatory affairs teams at the end of each study phase. The process involves manually assembling SDTM and ADaM datasets, generating Define-XML metadata files, compiling analysis results documents, and restructuring all of these into the XML-based eCTD (electronic Common Technical Document) format mandated by FDA, EMA, PMDA, and other agencies. Manual assembly introduces significant risk of formatting errors, metadata inconsistencies, and broken hyperlinks that can lead to technical rejection letters from regulatory agencies, delaying review timelines by weeks or months. An automated submission package assembly capability within CDOS would reduce assembly time by an estimated 60-70%, eliminate entire classes of structural and metadata errors, and ensure that every study database lock can be rapidly followed by a submission-ready package.

### 3. Detailed Description

The CDOS shall provide a regulatory submission package assembly module that takes validated SDTM and ADaM datasets, associated Define-XML metadata files, analysis result documents (tables, listings, and figures — TLFs), and study-level documentation (protocol, SAP, ICF) and assembles them into eCTD-compliant folder structures with correctly generated XML backbone files. The system shall support configurable submission package templates for different regulatory agencies (FDA, EMA, PMDA, PMDA, Health Canada, etc.) and submission types (IND, NDA/BLA, CTA, MAA, CSR supplements). Upon initiation by a regulatory affairs user, the system shall: (1) validate that all required SDTM/ADaM domains are present and pass CDISC conformance checks; (2) verify that Define-XML files are complete and cross-reference all dataset and variable metadata; (3) collect all TLFs and supporting documents referenced in the submission plan; (4) generate the eCTD XML backbone (index.xml and regional XML files) with correct node references, leaf titles, and operation attributes; (5) organize all files into the prescribed eCTD folder hierarchy (m1-m5 modules); and (6) produce a submission readiness report that flags any missing documents, metadata gaps, or conformance failures. The assembled package shall be versioned, immutable once locked, and available for download as a compressed archive or for direct transfer to electronic submission gateways (FDA ESG, EMA CESP/Common European Submission Portal). The system shall maintain a complete audit trail of who initiated the assembly, what was included, and any warnings or overrides applied during the process.

### 4. Preconditions

- [ ] The study database has been locked and SDTM/ADaM datasets have been finalized and passed CDISC validation
- [ ] Define-XML metadata files have been generated and reviewed by the data management team
- [ ] All analysis results documents (TLFs) have been finalized and approved by the biostatistics team
- [ ] A submission plan exists that specifies which documents and datasets are required for the specific submission type and target agency
- [ ] Regulatory affairs has configured the target agency template and eCTD module requirements in the CDOS submission module

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-015-AC01 | Automated eCTD structure generation | Validated SDTM datasets, ADaM datasets, Define-XML files, and approved TLFs are available for a completed Phase III study | A regulatory affairs user initiates package assembly for an FDA NDA submission | The system generates a complete eCTD folder structure (modules 1-5) within 60 minutes, including the XML backbone with correct leaf titles, operation attributes, and file references, ready for human review |
| BR-015-AC02 | Submission readiness validation | An eCTD package has been assembled | The system performs its pre-submission validation check | A submission readiness report is generated that identifies all missing required documents, Define-XML conformance issues (e.g., missing codelist references, undefined variables), CDISC validation failures, and broken document cross-references, with each issue classified as error (blocking) or warning (non-blocking) |
| BR-015-AC03 | Agency-specific template support | The same study data package needs to be submitted to both FDA and EMA | The user selects the EMA MAA template after previously generating an FDA NDA package | The system restructures the package to conform to EMA-specific eCTD requirements (different Module 1 structure, EU regional XML, any EMA-specific document requirements) without requiring manual re-entry of metadata or re-assignment of documents to nodes |
| BR-015-AC04 | Package versioning and immutability | An eCTD package has been assembled and locked for review | A biostatistics user updates an ADaM dataset after the lock | The system preserves the original locked package as an immutable version (v1.0) and requires the user to create a new version (v1.1) for any changes. Both versions are retained with full audit trails, and the diff between versions is logged |
| BR-015-AC05 | Electronic submission gateway integration | An eCTD package has been validated and approved | A regulatory affairs user initiates submission via the FDA Electronic Submissions Gateway (ESG) | The system transfers the compressed, validated eCTD archive to the ESG via the configured secure channel, logs the transmission with a timestamp and confirmation receipt, and updates the submission status tracker |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (Unified Data Integration Layer) | Blocks | Requires access to finalized SDTM/ADaM datasets through the canonical data model |
| BR-008 (CDISC Mapping and Validation) | Blocks | SDTM/ADaM datasets must pass CDISC conformance checks before assembly |
| BR-010 (Define-XML Generation) | Blocks | Define-XML metadata files must be available and validated before package assembly |
| BR-012 (Audit Trail and Electronic Signatures) | Related | Package lock, versioning, and submission actions require 21 CFR Part 11 compliant audit trails and e-signatures |
| BR-014 (Enrollment Forecasting) | Related | Enrollment forecast data may be included in CSR or regulatory briefing documents within the submission package |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS Data Repository | Reads from | Retrieves finalized SDTM/ADaM datasets, Define-XML files, and TLFs |
| CDOS Document Management | Reads from | Retrieves study documents (protocol, SAP, ICF, CSR) for inclusion in the submission package |
| CDOS CDISC Validation Engine | Reads from | Invokes CDISC conformance checks as part of the pre-assembly validation workflow |
| Electronic Submission Gateway (FDA ESG, EMA CESP) | Writes to | Transmits the assembled and validated eCTD package to the target regulatory agency portal |
| CDOS Regulatory Affairs Dashboard | Writes to | Updates submission status, readiness scores, and version history for regulatory tracking |
| CDOS Audit Trail Service | Writes to | Logs all assembly, lock, override, and submission actions with user attribution and timestamps |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| SubmissionPackage | Create, Read, Update | The assembled eCTD package with version, status, agency template, and file manifest |
| ECTDXmlBackbone | Create, Read | Generated XML backbone files (index.xml, regional XML) with node hierarchy and leaf references |
| SubmissionReadinessReport | Create, Read | Validation report listing errors, warnings, and document coverage for a submission package |
| SDTMDataset | Read | Finalized SDTM domain datasets for inclusion in the submission |
| ADaMDataset | Read | Finalized ADaM analysis datasets for inclusion in the submission |
| DefineXML | Read | Define-XML v2.1 metadata documents describing SDTM/ADaM structure and codelists |
| AnalysisResultDocument | Read | Tables, listings, and figures (TLFs) produced by biostatistics for the submission |
| SubmissionPlan | Read, Update | Document mapping required documents and datasets to eCTD module nodes for a given submission type |
| SubmissionAuditEntry | Create | Immutable audit records for every assembly, lock, version, and transmission event |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Define-XML references a dataset or variable that does not exist in the finalized SDTM/ADaM packages | The system generates a blocking error in the readiness report identifying the orphan reference, and prevents package lock until resolved |
| A study requires a sequence of submissions (e.g., original NDA followed by an amendment) | The system supports eCTD sequence numbering, generating the correct sequence folder (e.g., sequence 0001 for original, 0002 for amendment) with operation attributes (new, append, replace) for each leaf |
| The target agency requires a document format not available in the study repository (e.g., a pediatric investigation plan for EMA) | The system flags the missing document as a warning in the readiness report and allows the user to manually upload the document or mark it as "not applicable" with a justification that is recorded in the audit trail |
| An agency rejects the submission package due to a technical formatting error | The system logs the rejection feedback, reopens the package version, and presents a guided remediation workflow that highlights the specific files or XML nodes requiring correction |
| Multiple sponsors or CROs contribute to different sections of the same submission package | The system supports multi-party access with role-based permissions, where each party can only modify sections they own, and the system performs cross-section consistency checks before final assembly |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Manual eCTD assembly continues to consume 3-6 months per submission cycle, delaying time-to-market | High | High | Continue outsourcing eCTD assembly to specialized vendors at $150K-$300K per submission |
| Formatting and metadata errors lead to regulatory agency technical rejection letters | Medium | High | Implement manual double-review processes with checklists |
| Inconsistent submission quality across studies managed by different CROs or teams | Medium | Medium | Establish SOPs and provide eCTD assembly training |
| Competitors with automated submission capabilities achieve faster regulatory timelines | Medium | Medium | No mitigation; accept timeline disadvantage |

### 11. Assumptions

- All SDTM/ADaM datasets are finalized and CDISC-validated before submission assembly is initiated; the system does not perform data transformation, only assembly and validation
- Define-XML files are generated by a separate CDOS module (BR-010) and are assumed to conform to Define-XML v2.1 specification
- The organization has existing electronic submission gateway credentials (FDA ESG account, EMA CESP account) and the system is configured with the necessary digital certificates and credentials for automated transmission
- Agency-specific eCTD templates and validation rules are maintained by the CDOS platform team and updated within 30 business days of any published regulatory guidance changes

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor (Regulatory Affairs) | TBD | Pending |
| Sponsor (Data Management) | TBD | Pending |
| CRO | TBD | Pending |
| Quality Assurance | TBD | Pending |


---

# Business Requirements: BR-016 through BR-018

---

## BR-016: Metadata-Driven Study Configuration

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-016 |
| **Title** | Metadata-Driven Study Configuration |
| **Priority** | P0 |
| **Category** | Workflow |
| **Source Stakeholder Need(s)** | SN-010, SN-006 |
| **Regulatory Basis** | ICH E6(R2) Section 5.0 — Sponsor responsibilities for trial design and conduct |
| **Status** | Draft |

### 2. Business Rationale

CROs currently spend 4–8 weeks provisioning each new clinical study, involving manual configuration of data models, visit schedules, edit checks, workflow rules, and user roles across multiple disconnected systems. This provisioning bottleneck delays study start-up, increases labor costs estimated at $150,000–$300,000 per study, and introduces configuration errors that propagate into data quality issues downstream. Additionally, CROs running trials for multiple sponsors (SN-006) face compounded complexity because each sponsor's systems require bespoke integration logic. Without metadata-driven configuration, the CDOS platform cannot scale to support the CRO's portfolio of concurrent studies or deliver the rapid onboarding that sponsors expect. A centralized, metadata-driven approach eliminates redundant setup work, ensures consistency across studies, and enables reusable templates that reduce time-to-first-patient-in by 50% or more.

### 3. Detailed Description

The system shall provide a metadata-driven study configuration module that allows authorized users (study builders, data managers, CRO administrators) to define and provision new clinical studies using declarative metadata rather than custom code or manual system setup. When a new study is initiated, the system shall present a guided configuration workflow where the user selects or imports a study protocol definition, including study phases (Phase I–IV), therapeutic area, number of arms, visit schema, and target geography.

Upon import or manual entry of protocol metadata, the system shall automatically generate the corresponding data model (CRF structures, form layouts, field definitions), visit schedule, edit check rules, user role assignments, and workflow state machines. The configuration shall be stored as version-controlled metadata objects that can be reviewed, approved, and promoted through a configuration lifecycle (Draft → Reviewed → Approved → Active → Archived). The system shall support reusable study templates — pre-configured metadata packages for common study designs (e.g., oncology Phase III, vaccine Phase II/III) — that can be cloned and customized for new studies.

For CRO interoperability (SN-006), the metadata layer shall abstract sponsor-specific system details so that a single CDOS instance can serve multiple sponsors without per-sponsor custom integration. Sponsor connectivity configurations (EDC endpoints, lab vendor interfaces, IWRS links) shall be defined as metadata profiles that are composable with study-level configurations. The system shall expose a configuration validation engine that checks metadata completeness, consistency, and regulatory compliance (e.g., CDISC domain coverage, required fields for SDTM mapping) before a study can be promoted to Active status. All configuration changes shall be captured in an immutable audit trail with timestamps, user identity, and change rationale.

### 4. Preconditions

- [ ] CDOS platform tenant and organization hierarchy is established for the CRO and its sponsor clients
- [ ] At least one study template library has been seeded with baseline configurations for common study designs
- [ ] Sponsor connectivity profiles (EDC, LIMS, IWRS endpoints) have been defined and validated
- [ ] User roles for Study Builder, Data Manager, and CRO Administrator have been configured with appropriate permissions
- [ ] CDISC controlled terminology packages (MedDRA, SNOMED CT, CDASH) are loaded and versioned in the metadata repository

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-016-AC01 | Study creation from template | A CRO administrator has access to an approved oncology Phase III study template | The administrator selects the template and initiates a new study with protocol-specific parameters (arms, visits, regions) | The system generates a complete study configuration draft within 5 minutes, including CRF definitions, visit schedule, edit checks, role mappings, and CDISC domain stubs, ready for review |
| BR-016-AC02 | Configuration validation before activation | A study configuration draft is complete but has a missing required field in the AE (Adverse Events) CRF definition | The study builder attempts to promote the configuration from Draft to Active status | The validation engine blocks promotion, returns a detailed error report listing the missing field with CDISC reference, and the configuration remains in Draft until the issue is resolved |
| BR-016-AC03 | Multi-sponsor reuse | A CRO manages studies for Sponsor A (using Medidata Rave EDC) and Sponsor B (using Oracle InForm EDC) | The CRO creates a new study for Sponsor A by cloning a template originally built for Sponsor B | The system automatically applies Sponsor A's connectivity profile (EDC endpoint, API credentials, field mappings) while preserving the study design metadata, producing a valid configuration without manual re-entry of sponsor-specific integration details |
| BR-016-AC04 | Configuration audit trail | An approved study configuration for Study XYZ-101 is in Active status | A data manager modifies an edit check rule to add a new range check for a vital signs field | The system records the change in the immutable audit trail with the user's identity, timestamp, previous value, new value, and a mandatory change reason, and the modified rule is version-incremented |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (CDISC Canonical Data Model) | Blocks | The metadata-driven configuration must generate data models aligned with the canonical CDISC model; BR-001 defines that model |
| BR-005 (Role-Based Access Control) | Enables | Study configuration requires granular role definitions and permissions; BR-005 provides the RBAC framework |
| BR-017 (Automated Query Generation) | Related | Edit check rules configured via metadata drive automated query generation; the two BRs share the rule definition metadata |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC (Medidata Rave, Oracle InForm, Veeva Vault CDMS) | Syncs with | Study configuration metadata must be synchronized to EDC systems to create matching CRF definitions and edit checks |
| CDOS Configuration Management Module | Reads from / Writes to | Core module for storing, versioning, and validating study metadata |
| CDOS Workflow Engine | Writes to | Configuration metadata drives workflow state machine instantiation for each study |
| CDISC Mapping Service | Reads from | Validations reference CDISC controlled terminology and domain specifications |
| IWRS / RTSM | Syncs with | Study arm and randomization metadata from configuration must be synchronized with IWRS for randomization setup |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Study | Create, Read, Update | Top-level study definition including protocol metadata, phases, and status |
| StudyTemplate | Create, Read, Clone | Reusable configuration templates for common study designs |
| CRFDefinition | Create, Read, Update | Form and field definitions generated from protocol metadata |
| VisitSchedule | Create, Read, Update | Visit windows, intervals, and associated procedures |
| EditCheckRule | Create, Read, Update | Data validation rules (range checks, cross-field checks, conditional logic) |
| SponsorProfile | Read | Sponsor-specific connectivity and system configuration metadata |
| ConfigurationAuditEntry | Create, Read | Immutable audit log of all configuration changes |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Template references a deprecated CDISC terminology version | The validation engine flags the deprecated terms, suggests current equivalents, and blocks promotion until resolved or explicitly overridden with documented justification |
| Sponsor profile is incomplete (missing EDC endpoint) | The system allows study design configuration to proceed in Draft but blocks any data integration setup until the sponsor profile is complete |
| Two users simultaneously edit the same configuration | The system implements optimistic concurrency control; the second user receives a conflict notification with the option to review the first user's changes before merging or overwriting |
| Protocol amendment requires mid-study configuration changes | The system supports configuration versioning with amendment tracking; changes are applied as a new version with a change log, and the impact on existing data (e.g., affected CRFs, subjects in flight) is flagged for review |
| Study template from a different regulatory region (e.g., FDA vs. EMA) | The system applies region-specific validation rules and flags any regulatory gaps (e.g., missing EMA-required fields) when the template is cloned to a study targeting a different region |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Study start-up delays averaging 4–8 weeks per study persist, impacting CRO capacity and sponsor satisfaction | High | High | Manual configuration with spreadsheet-based checklists as interim measure, but this does not scale |
| Configuration errors propagate into data quality issues, increasing query volume and database lock delays | High | High | Rely on post-hoc data review processes, which are costly and slower |
| CROs cannot serve multiple sponsors from a single CDOS instance without custom integrations per engagement | High | Medium | Maintain separate CDOS instances per sponsor, increasing infrastructure and maintenance costs |
| Regulatory audit findings related to inconsistent or undocumented study configurations | Medium | High | Maintain manual configuration documentation with periodic QA reviews |

### 11. Assumptions

- Sponsors will provide protocol documents in a structured or semi-structured format (e.g., Protocol Schema Definition, FHIR-based protocol representation) that the system can parse; fully unstructured PDF-only protocols may require manual metadata entry
- CROs will designate trained Study Builder roles responsible for configuration; the system will not allow untrained users to create or modify study configurations
- CDISC terminology packages are maintained centrally and updated at least quarterly by a terminology governance body
- The initial release supports CDASH/SDTM-aligned data models; ADaM-ready configuration support is planned for a subsequent release

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [TBD — Sponsor Clinical Operations Lead] | Pending |
| CRO | [TBD — CRO Data Management Director] | Pending |
| Site | [TBD — Site Principal Investigator representative] | Pending |

---

## BR-017: Automated Query Generation

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-017 |
| **Title** | Automated Query Generation |
| **Priority** | P0 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-013, SN-025 |
| **Regulatory Basis** | ICH E6(R2) Section 5.5 — Data handling and quality assurance; 21 CFR Part 11 (electronic records integrity) |
| **Status** | Draft |

### 2. Business Rationale

Manual query generation is one of the most time-consuming and error-prone activities in clinical data management. Data managers currently spend 30–40% of their time reviewing data listings, identifying discrepancies, and manually drafting queries for site resolution. Across a typical Phase III study with 150 sites and 2,000 subjects, this translates to 6,000–12,000 queries per study, with an average resolution cycle time of 14–21 days per query. The cost of manual query management is estimated at $50–$80 per query, representing $300,000–$960,000 per study. Furthermore, manual query generation introduces inconsistency — different data managers may phrase similar queries differently, leading to site confusion and inconsistent resolution approaches (SN-013). Automated query generation, driven by the edit check rules defined in metadata-driven study configuration (BR-016), can reduce query cycle time by 60%, eliminate inconsistency, and free data managers to focus on complex medical and scientific data review rather than routine discrepancy identification (SN-025).

### 3. Detailed Description

The system shall automatically generate queries when clinical data entered at sites fails to satisfy predefined edit check rules. Edit check rules shall be defined as part of the study configuration (BR-016) and may include range checks (e.g., systolic blood pressure must be between 60 and 250 mmHg), cross-field consistency checks (e.g., date of death must be after date of enrollment), cross-form checks (e.g., concomitant medication start date must fall within the study participation window), and conditional logic checks (e.g., if pregnancy status is "Yes," then the subject must be female and of childbearing potential age).

When data is submitted or saved in the EDC system, the query engine shall evaluate all applicable edit check rules against the submitted data in real time. If a rule is violated, the system shall automatically generate a query with a standardized, context-rich message that includes: the specific rule violated, the actual value entered, the expected value or range, the field and form location, and a suggested resolution action. Queries shall be categorized by severity — Informational (no action required), Warning (site should review), and Mandatory (data cannot proceed until resolved) — based on the edit check rule configuration.

For site efficiency (SN-013), the system shall support batch query resolution where sites can address multiple related queries in a single action (e.g., resolving all date-related queries for a single subject in one transaction). The system shall provide auto-suggestion functionality that, based on historical resolution patterns and rule context, suggests likely correct values or resolution actions to site users. All auto-generated queries shall be routed to the appropriate site user based on role-based query assignment rules. Data managers shall have the ability to review, modify, suppress, or escalate auto-generated queries before or after they are sent to sites. The system shall track full query lifecycle metrics — generation time, assignment time, first response time, resolution time, and closure time — for operational dashboards (BR-018).

### 4. Preconditions

- [ ] Study configuration (BR-016) has been completed and approved with at least a baseline set of edit check rules
- [ ] EDC system integration is active and data is flowing into the CDOS data pipeline
- [ ] Site user roles and query assignment rules have been configured
- [ ] Query message templates have been defined for each edit check rule category
- [ ] Historical resolution data from prior studies is available for auto-suggestion model training (optional but recommended)

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-017-AC01 | Automatic query on range check violation | A study has an edit check rule: "Systolic BP must be between 60 and 250 mmHg" | A site user enters a systolic BP value of 310 mmHg and saves the form | The system generates a Mandatory-severity query within 5 seconds, displaying: "Systolic blood pressure value 310 mmHg exceeds the allowed range (60–250 mmHg). Please verify the value and correct or add a comment explaining the deviation." The query is assigned to the site's data entry user and the form cannot be marked complete until resolved |
| BR-017-AC02 | Batch query resolution | A subject has 8 open queries across 3 different CRF forms, all related to date inconsistencies | A site user navigates to the subject's query dashboard and selects "Resolve Batch" | The system presents all 8 queries in a single resolution interface, allows the user to enter corrected dates or explanatory comments in one transaction, and closes all 8 queries with a single submission, recording each resolution in the audit trail |
| BR-017-AC03 | Data manager query suppression | An auto-generated query flags a lab value as out of range, but the data manager has prior knowledge that the site's lab uses a different reference range | The data manager reviews the query and selects "Suppress with justification" | The query is marked as suppressed, the justification is recorded in the audit trail, the query is not sent to the site, and a suppression report is available for QA review |
| BR-017-AC04 | Cross-form consistency check | A study has a rule: "Concomitant medication start date must be on or after informed consent date" | A site enters a concomitant medication start date that is 30 days before the informed consent date | The system generates a Warning-severity query referencing both the concomitant medication form and the consent form by subject ID, displaying the conflicting dates and asking the site to verify or correct |
| BR-017-AC05 | Query metrics for operational dashboard | A study has been active for 60 days with 2,500 queries generated across 50 sites | A CRO data manager opens the query analytics dashboard | The dashboard displays real-time metrics: total queries (2,500), queries by severity (Mandatory: 800, Warning: 1,200, Informational: 500), average resolution time (11.2 days), queries by site (with top 5 slowest sites highlighted), and query aging distribution |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-016 (Metadata-Driven Study Configuration) | Blocks | Edit check rules that drive query generation are defined as part of study configuration metadata |
| BR-001 (CDISC Canonical Data Model) | Related | Query context must reference canonical data entities (Subject, Visit, CRF Form) to ensure consistent identification |
| BR-018 (Visit Scheduling and Calendar Management) | Related | Query metrics feed into operational dashboards; visit schedule context is needed for date-based cross-form checks |
| BR-005 (Role-Based Access Control) | Enables | Query assignment and data manager review permissions depend on RBAC |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC (Medidata Rave, Oracle InForm, Veeva Vault CDMS) | Reads from / Writes to | Reads submitted data for rule evaluation; writes generated queries back to EDC for site visibility |
| CDOS Query Management Module | Reads from / Writes to | Core module for query lifecycle management, metrics, and resolution workflows |
| CDOS Configuration Management Module | Reads from | Reads edit check rules from study configuration metadata |
| CDOS Operational Dashboard | Writes to | Publishes query metrics and analytics for CRO and sponsor visibility |
| Safety Database (Argus, ArisGlobal) | Reads from | Cross-references safety data to suppress false-positive queries on known adverse events |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Query | Create, Read, Update | The generated query record including severity, message, status, assignments, and resolution |
| EditCheckRule | Read | The rule definition that triggered the query |
| DataPoint | Read | The specific data value that violated the rule |
| QueryResolution | Create, Update | Resolution action taken by site or data manager, including comments and corrected values |
| QueryMetrics | Read, Create | Aggregated metrics for operational dashboards |
| QueryTemplate | Read | Standardized message templates for query text |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Multiple rules fire on the same data point simultaneously | The system deduplicates queries, merging related rule violations into a single query with a composite message listing all violated rules, avoiding query fatigue at the site |
| Edit check rule is modified while queries generated from the prior rule version are still open | Existing open queries remain linked to the original rule version; the system flags them for data manager review and generates a notification that the rule has changed |
| Site user repeatedly enters the same out-of-range value after query resolution | The system escalates the second recurrence to a Mandatory query assigned to the data manager, with a flag indicating repeated violation |
| Auto-suggestion model has insufficient historical data for a new study type | The system falls back to template-based suggestions (standard resolution language) and disables ML-based suggestions until a minimum threshold of resolved queries (e.g., 500) is reached |
| Query generation service experiences latency > 10 seconds | The system queues the query for asynchronous generation, notifies the site that a data review is pending, and guarantees query delivery within 60 seconds with a system health alert to the CRO administrator |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Manual query generation continues to consume 30–40% of data management resources | High | High | No automated mitigation; continue with manual query processes using data listings and spreadsheets |
| Inconsistent query phrasing across sites and studies leads to site confusion and longer resolution cycles | High | Medium | Implement standardized query text templates manually, but enforcement is difficult without automation |
| Delayed identification of data quality issues extends database lock timelines by 2–4 weeks | High | High | Increase data review frequency manually, at significant additional labor cost |
| Regulatory findings during inspection for inadequate data quality oversight | Medium | High | Document manual query processes thoroughly, but risk remains due to human error rates |

### 11. Assumptions

- Edit check rules are comprehensive and maintained by qualified data managers; the system does not generate rules autonomously but executes rules defined by humans or derived from CDISC/CDASH standards
- EDC systems support API-based bidirectional data exchange for real-time query generation and resolution
- Sites have network connectivity sufficient for real-time query delivery; offline scenarios are handled by queuing and eventual delivery
- Auto-suggestion accuracy will improve over time as the model learns from resolution patterns; initial accuracy is expected to be 40–60%, improving to 75–85% after 6 months of operation across multiple studies

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [TBD — Sponsor Data Management Lead] | Pending |
| CRO | [TBD — CRO Clinical Data Manager] | Pending |
| Site | [TBD — Site Data Entry Coordinator] | Pending |

---

## BR-018: Visit Scheduling and Calendar Management

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-018 |
| **Title** | Visit Scheduling and Calendar Management |
| **Priority** | P1 |
| **Category** | Site Experience |
| **Source Stakeholder Need(s)** | SN-012, SN-008 |
| **Regulatory Basis** | ICH E6(R2) Section 4.5 — Compliance with protocol; Section 5.14 — Supplying and handling investigational product |
| **Status** | Draft |

### 2. Business Rationale

Missed visits and schedule deviations are among the most common protocol violations in clinical trials, affecting approximately 15–25% of all scheduled visits industry-wide. Each missed visit can result in a protocol deviation report, loss of evaluable data, reduced statistical power, and potential regulatory scrutiny. For a Phase III study with 2,000 subjects and an average of 12 visits per subject, even a 10% miss rate translates to 2,400 affected visits, each costing an estimated $500–$1,200 in staff time, rescheduling effort, and data remediation — representing $1.2M–$2.9M in avoidable costs per study. Sites (SN-012) currently manage visit schedules using a combination of paper calendars, EDC system visit windows, and manual spreadsheets, leading to fragmented visibility and missed reminders. CRO operational dashboards (SN-008) lack real-time visit compliance metrics, making it difficult to identify struggling sites early. An integrated visit scheduling and calendar management capability within CDOS would centralize visit planning, automate reminders, surface deviations proactively, and feed real-time compliance metrics into operational dashboards.

### 3. Detailed Description

The system shall provide an integrated visit scheduling and calendar management module that enables sites to plan, track, and manage subject visit schedules derived directly from the study protocol configuration (BR-016). When a subject is enrolled in a study, the system shall automatically generate a personalized visit calendar based on the study's visit schedule definition, including visit windows (e.g., Day 1 ± 3 days, Week 4 ± 7 days), required procedures per visit, fasting requirements, and any conditional visits (e.g., Unscheduled Visit triggered by an adverse event).

The system shall display the visit calendar in multiple views — daily, weekly, monthly, and per-subject timeline — accessible to site coordinators, principal investigators, and CRO monitors. For each upcoming visit, the system shall send automated reminders to site staff at configurable intervals (e.g., 7 days, 3 days, and 1 day before the visit window opens) via in-app notification, email, or SMS, based on site preference. When a visit window is approaching closure and no visit has been recorded, the system shall escalate the alert to the site administrator and CRO monitoring team.

The system shall track visit compliance in real time, categorizing each visit as: On Time (within the protocol-defined window), Early (before the window opens), Late (within an acceptable deviation range after the window closes), or Missed (outside all acceptable ranges). Visit compliance metrics shall be aggregated and published to the CRO operational dashboard (SN-008), including site-level compliance rates, subject-level visit adherence timelines, and trend analysis showing whether compliance is improving or deteriorating over time. The system shall support protocol deviation auto-flagging — when a visit is classified as Missed or a critical visit procedure is skipped, the system shall automatically generate a protocol deviation record and route it to the appropriate clinical operations workflow for review and reporting.

Sites shall have the ability to reschedule visits within protocol-defined constraints, with the system enforcing window boundaries and flagging requests that require medical monitor approval (e.g., visits outside the allowed window). All scheduling actions, reschedules, and deviations shall be recorded in an immutable audit trail.

### 4. Preconditions

- [ ] Study configuration (BR-016) includes a complete visit schedule definition with visit windows, procedures, and conditional logic
- [ ] At least one subject has been enrolled and randomized in the study
- [ ] Site staff user accounts with appropriate roles (Coordinator, PI, Administrator) are active
- [ ] Notification delivery channels (email, SMS, in-app) are configured and operational for the site
- [ ] CRO operational dashboard (SN-008) is deployed and connected to the CDOS data pipeline

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-018-AC01 | Automatic visit calendar generation | Subject SUBJ-0042 is enrolled in Study XYZ-101 with a 12-visit protocol (Visits 1–12 over 48 weeks) | The enrollment event is recorded in the system | The system generates a personalized visit calendar for SUBJ-0042 within 30 seconds, listing all 12 visits with dates, visit windows, required procedures, and fasting instructions, visible to the site coordinator and PI |
| BR-018-AC02 | Automated visit reminders | Subject SUBJ-0042 has Visit 4 scheduled for June 15, 2026 (window: June 12–18) | The system date reaches June 8 (7 days before window opens) | The site coordinator receives an in-app notification and email: "Visit 4 for Subject SUBJ-0042 opens in 4 days (June 12–18). Required procedures: Physical exam, ECG, PK blood draw. Fasting: 8 hours." Additional reminders fire on June 12 and June 14 |
| BR-018-AC03 | Visit window escalation | Subject SUBJ-0042's Visit 4 window closes on June 18 and no visit has been recorded | The system date reaches June 18 and the visit status is still "Scheduled" | The system escalates to the site administrator and CRO monitoring lead with an alert: "Visit 4 for SUBJ-0042 window closes today — no visit recorded. Action required." The visit status changes to "At Risk — Missed" at midnight |
| BR-018-AC04 | Protocol deviation auto-flagging | A subject's Week 24 visit (critical for efficacy assessment) is missed entirely | The visit window closes without a recorded visit or approved reschedule | The system automatically creates a protocol deviation record categorized as "Major" per the study's deviation classification, assigns it to the site PI for review, and routes a notification to the CRO clinical operations manager |
| BR-018-AC05 | Operational dashboard visit compliance metrics | Study XYZ-101 has been active for 90 days with 150 enrolled subjects across 20 sites | A CRO clinical operations manager opens the operational dashboard | The dashboard displays: overall visit compliance rate (87.3%), compliance by site (with 3 sites below 80% flagged in red), compliance trend line showing improvement from 82% in Month 1 to 91% in Month 3, and a drill-down table listing the 45 most recently missed visits with subject IDs, visit numbers, and sites |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-016 (Metadata-Driven Study Configuration) | Blocks | Visit schedule definitions are generated from study configuration metadata |
| BR-005 (Role-Based Access Control) | Enables | Calendar access and reschedule permissions depend on role definitions |
| BR-017 (Automated Query Generation) | Related | Date-based cross-form edit checks may reference visit schedule windows for context |
| BR-003 (Operational Dashboard) | Enables | Visit compliance metrics must be published to the CRO operational dashboard |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS Visit Management Module | Reads from / Writes to | Core module for calendar generation, tracking, reminders, and compliance scoring |
| CDOS Configuration Management Module | Reads from | Reads visit schedule definitions from study configuration |
| EDC (Medidata Rave, Oracle InForm, Veeva Vault CDMS) | Reads from | Reads visit completion data recorded by site to update calendar status |
| CDOS Operational Dashboard | Writes to | Publishes visit compliance metrics, trend analysis, and site-level scores |
| CDOS Protocol Deviation Module | Writes to | Creates deviation records for missed or out-of-window visits |
| Notification Service (Email, SMS, In-App) | Writes to | Delivers automated visit reminders and escalation alerts |
| CDOS Audit Trail Service | Writes to | Records all scheduling, rescheduling, and compliance actions |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| SubjectVisitSchedule | Create, Read, Update | Per-subject visit calendar with dates, windows, procedures, and status |
| VisitReminder | Create, Read | Scheduled and delivered reminder notifications |
| VisitComplianceRecord | Create, Read | Compliance classification per visit (On Time, Early, Late, Missed) |
| ProtocolDeviation | Create, Read, Update | Auto-generated deviation records for missed or out-of-window visits |
| VisitRescheduleRequest | Create, Read, Update | Reschedule requests with approval workflow |
| VisitComplianceMetrics | Read | Aggregated metrics for operational dashboards |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Subject withdraws consent mid-study | All future scheduled visits are automatically cancelled, a withdrawal event is recorded, and the compliance calculation excludes the withdrawn subject from the denominator |
| Protocol amendment changes the visit schedule (e.g., adds a new visit, changes a window) | The system regenerates affected subject calendars, notifies site staff of changes, and maintains a record of the pre-amendment and post-amendment schedules |
| Site reschedules a visit outside the protocol-defined window | The system requires medical monitor approval, generates a protocol deviation record if approved, and updates the visit compliance status to "Late — Approved Deviation" |
| Two sites share a coordinator who manages overlapping visit schedules | The system presents a consolidated calendar view for the coordinator across all assigned sites, with conflict detection when two visits are scheduled at overlapping times |
| Subject is hospitalized unexpectedly and cannot attend a scheduled visit | The site records the hospitalization as the reason for the missed visit, the system creates an "Excused Missed Visit" status (not counted against compliance), and reschedules based on the subject's recovery timeline |
| Network outage at the site prevents reminder delivery | The system queues reminders and delivers them when connectivity is restored; the compliance clock continues based on the protocol window, not the reminder delivery time |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Visit miss rates remain at 15–25%, causing protocol deviations and data loss | High | High | Sites continue using paper calendars and manual reminders with no centralized tracking |
| CRO operational dashboards lack visit compliance visibility, delaying intervention at struggling sites | High | Medium | CRO monitors rely on periodic site visits and manual data pulls, which occur monthly at best |
| Protocol deviations from missed visits increase regulatory risk and audit findings | Medium | High | Increase source data verification (SDV) frequency at additional monitoring cost |
| Missed critical visits (e.g., efficacy endpoints) reduce evaluable subject count and statistical power | Medium | High | Increase sample size to compensate for expected data loss, increasing study cost by 10–20% |

### 11. Assumptions

- Study protocols define visit windows in a machine-readable format (e.g., days relative to first dose or enrollment); the system derives absolute dates from the subject's enrollment or first-dose date
- Sites have at least one staff member designated as the visit scheduling coordinator for each study
- Notification delivery (email, SMS) is reliable and sites have procedures to monitor notifications; the system is not responsible for site staff acknowledging reminders
- Protocol deviation classification rules (Major vs. Minor) are defined in the study configuration and vary by study; the system applies rules as configured but does not make medical judgments
- Visit compliance metrics are primarily for operational management and do not replace medical or statistical assessments of data quality

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [TBD — Sponsor Clinical Operations Director] | Pending |
| CRO | [TBD — CRO Clinical Operations Manager] | Pending |
| Site | [TBD — Site Study Coordinator Lead] | Pending |


---

# Business Requirements BR-019 through BR-021

---

## BR-019: Role-Based Access Control

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-019 |
| **Title** | Role-Based Access Control |
| **Priority** | P0 |
| **Category** | Workflow / Compliance |
| **Source Stakeholder Need(s)** | SN-014, SN-009, SN-028 |
| **Regulatory Basis** | 21 CFR Part 11 (electronic signatures and access controls), ICH E6(R2) (investigator and sponsor responsibilities), GDPR Article 32 (security of processing) |
| **Status** | Draft |

### 2. Business Rationale

Clinical trials involve dozens of distinct user personas across sponsors, CROs, and investigative sites, each requiring precisely scoped access to sensitive patient data and operational systems. Without a robust RBAC framework, organizations rely on ad-hoc permission grants managed in spreadsheets or disconnected identity systems, leading to over-provisioned accounts, audit findings, and potential HIPAA/GCP violations. A single unauthorized data access incident can trigger a regulatory warning letter, delay a submission by months, and cost upwards of $500,000 in remediation. Furthermore, periodic access reviews mandated by QA (SN-028) are impractical without a centralized role-to-permission mapping. RBAC is therefore a foundational P0 requirement that underpins every other CDOS capability.

### 3. Detailed Description

The CDOS platform must implement a comprehensive role-based access control system that governs what actions every authenticated user can perform. When a user is provisioned in the system, they are assigned one or more predefined roles — Sponsor Admin, CRA (Clinical Research Associate), Data Manager, Investigator, Coordinator, Monitor, Biostatistician, or QA Auditor — and those roles are scoped to specific studies, sites, and data domains (e.g., adverse events, lab data, demographics). The system must evaluate the user's role, study assignment, and site assignment at every access request and enforce permissions deterministically. Permissions are additive when a user holds multiple roles; however, the system must prevent conflicting permission combinations (e.g., a user cannot be both Data Entry and QA Auditor on the same study). The permission model must be configurable at the study level so that sponsors can tighten or relax access for specific protocols without modifying the global role definitions. When a user's role or study assignment changes, the permission change must take effect within 60 seconds across all CDOS components. The system must also support temporary elevated access (e.g., a Monitor granted write access to a specific site for a defined audit window) with automatic expiration and full audit logging. All access decisions must be recorded in an immutable audit trail for 21 CFR Part 11 compliance.

### 4. Preconditions

- [ ] CDOS identity provider (IdP) integration is operational and users can authenticate via SSO
- [ ] Canonical study, site, and data domain metadata is loaded into CDOS
- [ ] At least the eight predefined roles are defined in the system configuration
- [ ] Audit logging infrastructure is deployed and validated

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-019-AC01 | Role assignment enforces permissions | A user is provisioned with the "CRA" role scoped to Study ABC, Site 001 | The user attempts to view adverse event data for Study ABC, Site 001 | Access is granted and the action is logged in the audit trail |
| BR-019-AC02 | Cross-study access denied | A user is provisioned with the "CRA" role scoped to Study ABC only | The user attempts to view data for Study XYZ | Access is denied and the attempt is logged |
| BR-019-AC03 | Conflicting role prevention | A user already holds the "Data Entry" role on Study ABC | An admin attempts to assign the "QA Auditor" role on the same study | The system rejects the assignment with a clear error explaining the conflict |
| BR-019-AC04 | Temporary elevated access expires | A Monitor is granted temporary write access to Site 002 for 48 hours | 48 hours elapse | Write access is automatically revoked and the expiration is logged |
| BR-019-AC05 | Periodic access review support | QA initiates a quarterly access review for Study ABC | The review report is generated | All users with active roles on Study ABC are listed with their permissions, last login date, and any dormant accounts (no login in 90+ days) are flagged |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (Unified Trial Metadata) | Blocks | Study and site metadata must exist before roles can be scoped to them |
| BR-010 (Audit Trail) | Enables | RBAC access decisions must be recorded in the immutable audit trail |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS Identity Service | Writes to | Role and permission assignments are stored and evaluated |
| CDOS Data Access Layer | Reads from | Every data query checks RBAC permissions before returning results |
| CDOS Audit Service | Writes to | All access grants, denials, and role changes are logged |
| EDC | Syncs with | User roles must propagate to EDC modules for form-level access control |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| User | Read | User identity and authentication status |
| Role | Create, Read, Update | Predefined and custom role definitions with permission sets |
| UserStudyAssignment | Create, Read, Update, Delete | Mapping of users to roles scoped to studies |
| UserSiteAssignment | Create, Read, Update, Delete | Mapping of users to roles scoped to specific sites within studies |
| Permission | Read | Granular permission definitions (view, create, edit, delete, approve, export) per data domain |
| AccessAuditLog | Create | Immutable record of every access decision |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| User has roles across 10+ studies | System must resolve permissions within 200ms; no performance degradation |
| Sponsor Admin role conflicts with site-level Coordinator role | Sponsor Admin permissions take precedence; conflict is logged but access is not blocked |
| User account is deactivated mid-session | Active session is terminated within 30 seconds; in-flight data edits are saved as draft |
| Study is locked or archived | All users except Sponsor Admin and QA Auditor lose write access; read access remains for authorized roles |
| LDAP/IdP group sync removes a user's group membership | CDOS revokes corresponding role assignments within the next sync cycle (max 15 minutes) |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Unauthorized access to PHI triggers HIPAA breach notification | Medium | High | Manual access reviews using spreadsheets (error-prone, not scalable) |
| Regulatory audit finding for 21 CFR Part 11 non-compliance | High | High | No practical mitigation without centralized RBAC |
| Over-provisioned accounts lead to data integrity concerns | High | Medium | Quarterly manual recertification by site managers |

### 11. Assumptions

- The CDOS platform integrates with the organization's existing SSO/IdP (e.g., Azure AD, Okta) for primary authentication
- The eight predefined roles are sufficient for initial deployment; custom roles may be added in a future release
- Study and site metadata are maintained by a Sponsor Admin and are assumed to be accurate at the time of role assignment
- GDPR data subject access requests are handled by a separate privacy module and do not directly impact RBAC logic

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | TBD | Pending |
| CRO | TBD | Pending |
| Site | TBD | Pending |
| QA/Compliance | TBD | Pending |

---

## BR-020: eTMF Document Integration

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-020 |
| **Title** | eTMF Document Integration |
| **Priority** | P2 |
| **Category** | Data Integration / Compliance |
| **Source Stakeholder Need(s)** | SN-027, SN-018 |
| **Regulatory Basis** | ICH E6(R2) (essential documents), 21 CFR Part 312 (IND content and format), GDPR Article 30 (records of processing activities) |
| **Status** | Draft |

### 2. Business Rationale

Essential trial documents — protocol amendments, IRB/IEC approvals, investigator CVs and medical licenses, informed consent forms, and monitoring visit reports — must be maintained in an electronic Trial Master File (eTMF) to satisfy ICH E6(R2) requirements for inspection readiness. Today, these documents reside in disconnected systems: the eTMF (e.g., Veeva Vault, MasterControl), the EDC, and shared drives. Sponsors and CROs spend an estimated 3–5 hours per study per week reconciling document versions between systems, and during regulatory inspections, the inability to instantly link a protocol amendment to its corresponding study configuration changes is a common finding. Integrating CDOS with eTMF systems eliminates this reconciliation burden and ensures that every study-level configuration change in CDOS is traceable to its authoritative document source.

### 3. Detailed Description

The CDOS platform must establish bidirectional integration with one or more eTMF systems to synchronize essential trial documents and maintain traceability between documents and CDOS study/site configurations. When a new document is approved in the eTMF (e.g., a protocol amendment v2.0 receives IRB approval), the integration must detect the event via webhook or polling, retrieve the document metadata and content reference, and create or update a corresponding link in CDOS. The system must support document classification aligned with the DIA TMF Reference Model (zone/section/artifact) so that documents are consistently categorized regardless of the source eTMF. Conversely, when a study configuration change is made in CDOS (e.g., a new data collection form is activated per a protocol amendment), CDOS must push an event to the eTMF indicating the change and its linked document reference. Document links must be searchable within CDOS — for example, a user viewing a site's profile should be able to see the current IRB approval letter, the principal investigator's CV, and the site's delegation log without leaving CDOS. The integration must support document versioning: when a new version of a document is approved, the old link is superseded and the new version becomes active, with full version history preserved. All document access and link operations must be logged in the CDOS audit trail for inspection readiness.

### 4. Preconditions

- [ ] An eTMF system (e.g., Veeva Vault, MasterControl, Florence eBinders) is deployed and accessible via API
- [ ] DIA TMF Reference Model taxonomy is configured in CDOS for document classification
- [ ] CDOS study and site metadata is loaded (depends on BR-001)
- [ ] OAuth2 or API key credentials for the eTMF system are provisioned

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-020-AC01 | Protocol amendment link creation | A protocol amendment v3.0 is approved in the eTMF for Study ABC | The eTMF webhook fires or CDOS polls the eTMF | CDOS creates a document link record associating the amendment with Study ABC, classifies it under TMF section 01.05, and notifies the Study Lead |
| BR-020-AC02 | Investigator CV site linkage | An investigator CV is uploaded and approved in the eTMF for Site 001, Study ABC | The integration event is processed | The CV is linked to Site 001 in CDOS and visible in the site profile with document version, approval date, and expiration date |
| BR-020-AC03 | Version supersession | A new IRB approval letter (v2) replaces v1 for Site 002 | CDOS receives the update from the eTMF | The old link is marked as superseded; the new version is active; both versions remain viewable with their respective dates |
| BR-020-AC04 | Bidirectional event | A new eCRF is activated in CDOS per protocol amendment v3.0 | The activation is saved | CDOS pushes a configuration change event to the eTMF referencing the linked amendment document |
| BR-020-AC05 | Search and retrieval | A CRA is viewing Site 003 in CDOS | They click "Essential Documents" | A list of all linked eTMF documents for that site is displayed, filtered by TMF section, with status (active, superseded, expired) |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (Unified Trial Metadata) | Blocks | Study and site records must exist to link documents |
| BR-019 (Role-Based Access Control) | Enables | Document access must respect RBAC permissions (e.g., only Monitors and Sponsor Admins can view certain TMF sections) |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| eTMF System (e.g., Veeva Vault) | Syncs with | Bidirectional document metadata and event exchange |
| CDOS Study Configuration | Reads from | Study and site metadata used for document linking |
| CDOS Document Link Service | Writes to | Stores document links, versions, and classification |
| CDOS Audit Service | Writes to | Logs all document link operations |
| CDOS Notification Service | Writes to | Alerts users when new documents are linked or versions change |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| DocumentLink | Create, Read, Update | Association between an eTMF document and a CDOS study/site |
| DocumentVersion | Create, Read | Version history for linked documents |
| Study | Read | Study metadata for linking |
| Site | Read | Site metadata for linking |
| TMFClassification | Read | DIA TMF Reference Model taxonomy for document categorization |
| DocumentAuditEvent | Create | Immutable log of all document link and access operations |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| eTMF system is temporarily unavailable | CDOS queues outbound events and retries on a configurable schedule (default: every 15 minutes for 24 hours); no data loss |
| Duplicate document detected (same document ID from eTMF) | CDOS deduplicates and updates the existing link rather than creating a duplicate |
| Document is retracted or deleted in the eTMF | CDOS marks the link as "Retracted" with a reason code; the link is hidden from default views but retained for audit |
| TMF classification does not match CDOS taxonomy | The document is linked with a "Pending Classification" flag; an admin is notified to manually classify it |
| Multi-language documents | CDOS stores the primary language reference; language metadata from the eTMF is preserved on the link record |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Regulatory inspection finding for missing or outdated essential documents | High | High | Manual document reconciliation (3–5 hours/week/study, error-prone) |
| Protocol deviation due to site using outdated consent form version | Medium | High | Email-based document distribution (no automated version tracking) |
| Change control gaps — CDOS config changes not linked to source documents | High | Medium | Manual traceability matrix maintained in Excel |

### 11. Assumptions

- The eTMF system exposes a REST API with webhook support or a polling endpoint for document events
- DIA TMF Reference Model v3.x is the standard taxonomy used by the organization
- Documents stored in the eTMF are the system of record; CDOS stores links and metadata, not document copies
- A maximum of 50,000 document links per study is expected; larger studies may require architectural review

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | TBD | Pending |
| CRO | TBD | Pending |
| QA/Compliance | TBD | Pending |
| Regulatory | TBD | Pending |

---

## BR-021: Electronic Informed Consent

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-021 |
| **Title** | Electronic Informed Consent |
| **Priority** | P1 |
| **Category** | Compliance / Workflow |
| **Source Stakeholder Need(s)** | SN-019, SN-009 |
| **Regulatory Basis** | 21 CFR Part 11 (electronic records and signatures), ICH E6(R2) Section 4.8 (informed consent), FDA Guidance on Electronic Informed Consent (2016), GDPR Article 7 (conditions for consent) |
| **Status** | Draft |

### 2. Business Rationale

Paper-based informed consent processes are a leading source of protocol deviations and inspection findings in clinical trials. Sites report that 15–20% of consent-related queries involve missing signatures, undated forms, or use of outdated consent versions. Each such query requires investigator review, corrective action, and documentation — costing an average of $150–$300 per incident. Beyond operational cost, patients increasingly expect digital experiences: a 2023 industry survey found that 72% of trial participants preferred electronic consent review over paper. An eConsent capability in CDOS addresses both operational efficiency and patient experience while ensuring full 21 CFR Part 11 compliance through electronic signatures, version-controlled consent forms, and immutable audit trails.

### 3. Detailed Description

The CDOS Electronic Informed Consent module must enable the complete consent lifecycle — from consent form authoring and version management through subject review, Q&A, signature capture, and long-term archival — in a digital, compliant workflow. When a sponsor or study team creates a new consent form (or updates an existing version), the system must enforce version control: each version has a unique identifier, effective date, expiration date (optional), and approval status. Only the currently approved version is presented to subjects for review. The subject accesses the consent form via a secure link (sent via email or SMS) and can review the form at their own pace, on any device (desktop, tablet, mobile). The system must support multimedia content within the consent form (e.g., embedded videos explaining procedures, glossary pop-ups for medical terms) to improve comprehension. During review, the subject may submit questions to the study team via an integrated Q&A workflow; the questions are routed to the Coordinator or Investigator, and responses are logged and visible to the subject. When the subject is ready to consent, they apply an electronic signature — either a typed name with date, a drawn signature, or a biometric signature (fingerprint/face) depending on site configuration and device capability. The system must capture the signer's identity (authenticated via the CDOS IdP or a one-time passcode), the exact timestamp, the document version signed, and the IP address or device identifier. If the consent form is amended during a trial, the system must present the new version to already-consented subjects for re-consent, tracking the relationship between the original and updated consent. All consent events — creation, review start, question asked, question answered, signature applied, re-consent, withdrawal — must be recorded in an immutable audit trail that satisfies 21 CFR Part 11 requirements for electronic records. The audit trail must be exportable in PDF format for regulatory inspection.

### 4. Preconditions

- [ ] A consent form template library is available and approved by the sponsor's medical/legal team
- [ ] 21 CFR Part 11 electronic signature policies are documented and approved by QA
- [ ] CDOS identity provider integration is operational for subject authentication (or one-time passcode mechanism is configured)
- [ ] CDOS notification service (email/SMS) is configured and tested
- [ ] Study metadata and site assignments are loaded in CDOS

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-021-AC01 | Consent form versioning | Consent form v1.0 is active for Study ABC; v2.0 is uploaded and approved | A new subject navigates to the consent page | They see only v2.0; v1.0 is no longer available for new consents but remains viewable in the audit history |
| BR-021-AC02 | Electronic signature capture | A subject has reviewed the consent form and clicks "I Consent" | They authenticate via one-time passcode and apply their typed signature | The system records the signature with timestamp, consent version, subject ID, authentication method, and IP address in the immutable audit trail |
| BR-021-AC03 | Q&A workflow | A subject has a question about a study procedure during consent review | They submit the question via the in-app Q&A form | The question is routed to the site Coordinator; the subject receives a notification when answered; both the question and answer are logged with timestamps |
| BR-021-AC04 | Re-consent on amendment | Consent form v2.0 is activated to replace v1.0 for Study ABC | Subjects who previously signed v1.0 log in | They are prompted to review v2.0; a new signature is captured; the system links the re-consent to the original consent record |
| BR-021-AC05 | Consent withdrawal | A subject decides to withdraw consent | They click "Withdraw Consent" and confirm | Consent status changes to "Withdrawn" with timestamp and reason; the Investigator and Coordinator are notified; no further data collection occurs for that subject unless re-consent is obtained |
| BR-021-AC06 | Audit trail export | A regulatory inspector requests consent records for Site 005 | An authorized user (Sponsor Admin or QA Auditor) exports the audit trail | A PDF is generated containing all consent events for Site 005, with timestamps, signatures, version history, and Q&A logs, digitally signed by the system |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-019 (Role-Based Access Control) | Blocks | Consent form authoring, approval, and audit export must be restricted to authorized roles |
| BR-010 (Audit Trail) | Enables | Electronic consent events must be recorded in the immutable audit trail |
| BR-020 (eTMF Document Integration) | Related | Approved consent form versions should be linked as essential documents in the eTMF |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS eConsent Module | Writes to | Core consent workflow engine — form management, Q&A, signature capture |
| CDOS Identity Service | Reads from | Subject authentication for signature verification |
| CDOS Notification Service | Writes to | Email/SMS delivery of consent links, Q&A responses, and re-consent prompts |
| CDOS Audit Service | Writes to | Immutable logging of all consent lifecycle events |
| eTMF | Syncs with | Approved consent form versions pushed as essential documents |
| CDOS Subject Management | Writes to | Consent status (consented, withdrawn) updates the subject's enrollment status |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| ConsentForm | Create, Read, Update | Consent form content, version metadata, and approval status |
| ConsentFormVersion | Create, Read | Individual versions with effective dates and content snapshots |
| ConsentEvent | Create, Read | Immutable record of every consent lifecycle event (review, sign, withdraw) |
| ElectronicSignature | Create, Read | Signature capture with authentication method, timestamp, and signer identity |
| ConsentQA | Create, Read | Questions submitted by subjects and responses from the study team |
| Subject | Read, Update | Subject enrollment status affected by consent/withdrawal |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Subject lacks email or mobile phone | Site Coordinator generates an in-person eConsent session on a site tablet; the subject signs on-device; the Coordinator witnesses and countersigns |
| Subject is a minor (assent + parental consent) | System supports dual-signature workflow: parent/guardian signs consent, minor signs assent (age-appropriate form); both signatures are captured independently |
| Consent form includes site-specific addenda | System supports a base consent form with optional site-specific sections; the applicable addendum is determined by the subject's site assignment |
| Network interruption during signature | Signature data is cached locally on the device and submitted when connectivity is restored; the audit trail records the actual signing time (device clock) and the submission time |
| Subject withdraws consent but later reconsents | A new consent record is created linked to the original; the subject's enrollment status is updated to "Re-consented"; data collection resumes |
| Multiple languages required | Consent forms are authored in multiple languages; the subject is presented the form in their preferred language (configured in subject profile); all language versions are linked to the same consent form version |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Protocol deviations from paper consent errors (missing signatures, wrong versions) | High | Medium | Site-level paper consent SOPs with double-verification (labor-intensive) |
| 21 CFR Part 11 audit finding for lack of electronic signature controls | High | High | No practical mitigation; paper consent does not provide the required audit trail for electronic records |
| Poor patient comprehension leading to higher dropout rates | Medium | Medium | In-person consent education sessions (not scalable for decentralized trials) |
| Delayed re-consent tracking for protocol amendments | Medium | Medium | Manual tracking spreadsheet (error-prone, ~2 hours/week/study) |

### 11. Assumptions

- Subjects have access to a device (smartphone, tablet, or computer) with a modern web browser; a native mobile app is not required for MVP
- Electronic signature policies compliant with 21 CFR Part 11 are defined and approved before eConsent deployment
- Consent form content is authored and reviewed outside of CDOS (e.g., in a document management system) and imported into CDOS in a structured format (PDF or HTML)
- The system supports up to 10,000 active consent events per study; capacity planning for larger studies will be addressed in the architecture phase
- Regulatory requirements for eConsent vary by country; the initial release targets US (FDA) and EU (EMA) requirements; additional country support will be added iteratively

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | TBD | Pending |
| CRO | TBD | Pending |
| Site | TBD | Pending |
| Patient Advocacy | TBD | Pending |
| QA/Compliance | TBD | Pending |


---

# Business Requirements: BR-022 through BR-024

---

## BR-022: Subject Data Portability

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-022 |
| **Title** | Subject Data Portability |
| **Priority** | P1 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-004, SN-006 |
| **Regulatory Basis** | 21 CFR Part 11 (data integrity during transfer), GDPR Article 20 (data portability), ICH E6(R2) Section 5.5 (trial data transfer obligations) |
| **Status** | Draft |

### 2. Business Rationale

Sponsors retain legal ownership of all clinical trial data, yet many EDC and clinical platforms create vendor lock-in through proprietary data formats, restricted APIs, and contractual barriers to data extraction. When a sponsor transitions a study from one CRO to another — whether due to performance issues, cost optimization, or portfolio reshuffling — data migration can take 3–6 months and cost $200K–$500K per study in manual reconciliation and re-validation effort. SN-004 explicitly requires that sponsors retain full portability of all trial data, and SN-006 requires CROs to interoperate without custom integrations per engagement. Without this requirement, sponsors face unacceptable switching costs and operational risk during CRO transitions, potentially delaying critical milestones and regulatory submissions.

### 3. Detailed Description

The CDOS must provide a comprehensive Subject-level data export capability that allows authorized users to extract all data associated with one or more subjects across any study. The system shall support export in three industry-standard formats: ODM (Operational Data Model) v2.0 XML, which is the CDISC standard for clinical data exchange and is widely accepted by regulatory authorities; CSV (Comma-Separated Values), which provides maximum compatibility with downstream analytics tools; and JSON, which supports modern API-driven integrations and data lake architectures.

When an export is initiated, the system must gather all subject-level data including demographic information, visit schedules, form data, query history, audit trail entries, adverse events, concomitant medications, and any associated file attachments. The export must be comprehensive enough that a receiving system can reconstruct the complete subject history without reference to the originating system. The system must support both single-subject and bulk export operations, with configurable filters for study, site, date ranges, and data status (e.g., verified, locked, frozen). Exports must include all associated metadata such as form definitions, code lists, and unit mappings so that the receiving system can interpret the data semantically. The export process must be fully auditable, with each export logged with timestamp, requesting user, scope of data exported, and format used.

### 4. Preconditions

- [ ] Study is registered and active in CDOS with at least one subject enrolled
- [ ] Requesting user has "Data Export" permission for the target study
- [ ] Source system (EDC, eCOA, lab) data has been ingested and mapped to CDOS canonical model
- [ ] Data privacy review completed and any region-specific export restrictions configured

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-022-AC01 | ODM v2.0 export | A study has 50 subjects with complete data across 5 visits | An authorized user requests a full study export in ODM v2.0 format | The system produces a valid ODM v2.0 XML file that passes CDISC ODM validation and contains all subject, study event, form, item group, and item data with associated audit trails |
| BR-022-AC02 | Multi-format parity | Subject data exists with forms, queries, AE records, and audit trails | The same data is exported in ODM v2.0, CSV, and JSON formats | All three exports contain semantically equivalent data with no information loss; a round-trip comparison confirms field-level parity |
| BR-022-AC03 | Export audit trail | A data manager initiates a bulk export of 200 subjects | The export completes successfully | An immutable audit log entry is created recording the user ID, timestamp, study ID, subject count, format, and data scope exported |
| BR-022-AC04 | CRO transition scenario | A sponsor is transferring study ABC-101 from CRO-A to CRO-B | CRO-B imports the CDOS export into their system | All subject data, visit schedules, query history, and audit trails are fully reconstructable without manual data entry or reconciliation |
| BR-022-AC05 | Filtered export | A study has subjects across 10 sites | A user exports only Site 003 subjects enrolled after 2025-01-01 in CSV format | The export contains only subjects matching the filter criteria with no data leakage from other sites or date ranges |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (CDOS Canonical Data Model) | Blocks | Subject data must be mapped to a canonical model before export can aggregate across sources |
| BR-003 (Audit Trail Infrastructure) | Enables | Export audit entries require the immutable audit trail system |
| BR-024 (Cross-Study Data Harmonization) | Related | Harmonized code lists and variable definitions improve export consistency |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC | Reads from | Extracts subject form data, queries, and visit schedules |
| eCOA | Reads from | Extracts patient-reported outcome data |
| CDOS Data Repository | Reads from | Aggregates canonical subject data from all integrated sources |
| CDOS Export Engine | Writes to | Generates ODM, CSV, and JSON export packages |
| CDOS Audit Service | Writes to | Logs all export operations |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| Subject | Read | Subject demographics, enrollment, and status data |
| StudyEvent | Read | Visit-level data including dates, forms, and statuses |
| FormData | Read | All CRF/EDC form field values and associated metadata |
| Query | Read | Data query history including open, answered, and closed queries |
| AuditEntry | Read, Create | Audit trail data for export; new entries created for export operations |
| AdverseEvent | Read | Adverse event records associated with exported subjects |
| CodeList | Read | Code lists and controlled terminology for inclusion in exports |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Subject has partially entered data for an in-progress visit | Export includes all available data with a status indicator showing the visit is incomplete |
| Subject withdrew consent and data must be excluded per GDPR | System respects data exclusion flags and omits excluded subjects unless explicitly overridden by a user with "Data Privacy Override" permission |
| Export request includes 10,000+ subjects | System processes the export asynchronously, notifies the user upon completion, and provides a download link valid for 72 hours |
| ODM export encounters an unmapped custom field | System includes the field in a supplemental ODM extension namespace with a warning annotation rather than silently dropping it |
| Network interruption during export | System preserves partial export state, allows resumption from last checkpoint, and logs the interruption event |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Sponsor locked into a single CRO, increasing costs by 30–50% on contract renewals | High | High | Manual data extraction scripts as interim measure (costly, error-prone) |
| CRO transition delays of 3–6 months due to manual data migration | Medium | High | Bilateral data-sharing agreements with file-based transfers |
| Regulatory submission delays if data cannot be exported in CDISC-compliant format | Medium | Critical | Post-hoc SDTM mapping by third-party vendors |
| Loss of audit trail integrity during data transfers | Medium | High | Paper-based audit trail reconstruction (labor-intensive, non-compliant risk) |

### 11. Assumptions

- All integrated source systems (EDC, eCOA, IWRS, lab) expose data through APIs or standardized file interfaces that CDOS can read
- ODM v2.0 is the accepted exchange standard between the sponsor and their CRO partners
- Subject consent status is maintained in the CDOS canonical model and can be used to enforce data exclusion rules during export
- Network bandwidth is sufficient to support bulk exports of up to 50 GB per operation

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | TBD | Pending |
| CRO | TBD | Pending |
| Data Management | TBD | Pending |
| Regulatory Affairs | TBD | Pending |

---

## BR-023: Adverse Event Reporting Interface

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-023 |
| **Title** | Adverse Event Reporting Interface |
| **Priority** | P0 |
| **Category** | Workflow |
| **Source Stakeholder Need(s)** | SN-017, SN-020 |
| **Regulatory Basis** | ICH E2A (Clinical Safety Data Management), ICH E6(R2) Section 4.11 (Safety Reporting), 21 CFR 312.32 (IND Safety Reports), EU CTR 536/2014 Article 42 (SUSAR Reporting), MedDRA Usage Guidelines |
| **Status** | Draft |

### 2. Business Rationale

Adverse event (AE) reporting is the single most time-sensitive and regulatorily consequential workflow in clinical trials. Late or inaccurate safety reporting can trigger clinical holds, warning letters, and patient harm. SN-017 requires regulators to receive timely, structured safety data with clear causality assessments and MedDRA coding. SN-020 requires patients to have easy mechanisms to report adverse events, including via mobile devices. Currently, AE data is often entered in free-text fields within EDC systems, manually coded to MedDRA by data managers, and then re-keyed into safety databases — a process that takes 3–5 business days per event and introduces transcription errors in approximately 8–12% of cases. SAE and SUSAR escalation to regulatory authorities within the mandated 24-hour (fatal/life-threatening) and 15-day (other SAEs) timelines is frequently at risk due to fragmented workflows. This requirement establishes a structured, automated, and auditable AE reporting interface that is foundational to patient safety and regulatory compliance.

### 3. Detailed Description

The CDOS must provide a structured Adverse Event entry interface that captures all required safety data elements in a standardized, validated format. When a site investigator, study coordinator, or patient (via an approved ePRO/mobile interface) initiates an AE report, the system must present a guided entry form that captures: event description (verbatim term), onset date and time, resolution date and time, severity (mild/moderate/severe per CTCAE grading), seriousness criteria (hospitalization, life-threatening, death, disability, congenital anomaly, medically important event), causality assessment (related/unrelated to study drug, with investigator rationale), expectedness against the Investigator's Brochure, outcome (recovered, recovering, not recovered, fatal, unknown), and any actions taken (dose modified, drug withdrawn, concomitant medication, other treatment).

Upon submission of the verbatim event term, the system must automatically query an integrated MedDRA dictionary (current version) and present the investigator with a ranked list of candidate Lowest Level Terms (LLTs) and Preferred Terms (PTs) for selection. The system must store both the verbatim term and the coded MedDRA term(s) with version identification. If the event meets predefined SAE criteria (configurable per study protocol), the system must immediately trigger an escalation workflow that notifies the Sponsor safety team, the CRO pharmacovigilance group, and — for SUSARs — generates a pre-populated ICSR (Individual Case Safety Report) for regulatory submission. The escalation must occur within 15 minutes of SAE classification for fatal/life-threatening events and within 4 hours for other SAEs. All AE entries and subsequent updates must be immutably audited with electronic signatures per 21 CFR Part 11.

### 4. Preconditions

- [ ] Study protocol is configured with SAE criteria, seriousness classifications, and reporting timelines
- [ ] MedDRA dictionary (current version) is loaded and indexed in CDOS
- [ ] Site investigators and coordinators have completed AE reporting training and have appropriate role-based access
- [ ] Notification routing rules for SAE/SUSAR escalation are configured per study
- [ ] ePRO/mobile AE reporting module is approved by IRB/Ethics Committee (if patient-facing reporting is enabled)

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-023-AC01 | Structured AE entry | A site investigator is logged into CDOS at a study site | The investigator creates a new AE and enters verbatim term "headache", onset date, severity "moderate", and causality "possibly related" | The system validates all required fields, auto-codes the verbatim term to MedDRA LLT "Headache" / PT "Headache", stores both verbatim and coded terms, and creates an immutable audit trail entry with the investigator's electronic signature |
| BR-023-AC02 | SAE escalation | A subject is hospitalized due to an adverse event | The site coordinator enters the AE with seriousness criterion "requires hospitalization" and marks it as an SAE | The system triggers SAE escalation within 4 hours: notifies sponsor safety team and CRO PV group via configured channels (email, in-app alert, webhook), generates a pre-populated ICSR draft, and logs the escalation timestamp |
| BR-023-AC03 | SUSAR fast-track | A subject experiences an unexpected, life-threatening reaction to study drug | The investigator enters the event as life-threatening, unexpected, and related | The system classifies it as a SUSAR, triggers immediate escalation within 15 minutes, generates a pre-populated ICSR for regulatory submission, and notifies the sponsor Medical Monitor directly via priority alert |
| BR-023-AC04 | MedDRA auto-coding accuracy | An investigator enters 50 different verbatim AE terms | The system auto-suggests MedDRA codes for each | At least 90% of suggested PTs are accepted by the investigator without manual override; all overrides are captured for coding quality review |
| BR-023-AC05 | Patient mobile AE reporting | A study subject is using the approved ePRO mobile app | The subject reports "feeling dizzy since yesterday" through the simplified symptom reporting interface | The report is captured with timestamp, linked to the subject's study record, flagged for investigator review and medical assessment, and routed to the site coordinator for causality determination within 24 hours |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (CDOS Canonical Data Model) | Blocks | AE data model must align with CDOS canonical entities |
| BR-003 (Audit Trail Infrastructure) | Blocks | AE entries require immutable, e-signature-protected audit trails |
| BR-005 (Role-Based Access Control) | Blocks | AE entry and escalation require role-based permissions |
| BR-022 (Subject Data Portability) | Related | AE data must be included in subject data exports |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC | Reads from, Writes to | Receives AE data entered via EDC; writes coded AE data back |
| ePRO/Mobile | Reads from | Receives patient-reported AE symptoms for investigator review |
| CDOS Safety Module | Writes to | Core AE entry, coding, and escalation engine |
| MedDRA Dictionary Service | Reads from | Auto-coding queries against current MedDRA version |
| CDOS Notification Service | Writes to | Triggers SAE/SUSAR escalation alerts |
| ICSR Generator | Writes to | Produces pre-populated ICSR reports for regulatory submission |
| CDOS Audit Service | Writes to | Logs all AE entry, modification, and escalation events |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| AdverseEvent | Create, Read, Update | Core AE record with all structured fields |
| MedDRACoding | Create, Read | Auto-coded MedDRA terms (LLT, PT, HLT, HLGT, SOC) linked to AE |
| SeriousAdverseEvent | Create, Read | SAE subclass with escalation status and ICSR linkage |
| CausalityAssessment | Create, Read | Investigator causality determination with rationale |
| ICSR | Create, Read | Individual Case Safety Report for regulatory submission |
| Subject | Read | Subject demographics and study drug exposure for ICSR population |
| AuditEntry | Create | Immutable audit trail for all AE lifecycle events |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Investigator enters an AE with a verbatim term that has no MedDRA match | System flags the term for manual coding by the data management team, assigns a temporary internal code, and queues it for MedDRA review |
| Multiple investigators update the same AE concurrently | System applies last-write-wins with full conflict detection; both updates are preserved in the audit trail, and a reconciliation query is generated |
| AE is initially classified as non-SAE but later upgraded to SAE upon new information | System re-triggers the SAE escalation workflow from the upgrade timestamp, recalculates reporting timelines, and notifies all configured recipients |
| Patient reports an AE via mobile but the report is incomplete | System captures the partial report, flags it as "Incomplete — Pending Site Review", and sends a reminder to the site coordinator to complete the assessment within 24 hours |
| MedDRA dictionary is updated mid-study | System retains original coding version for existing AEs, applies new version for newly entered AEs, and provides a recoding utility for optional migration with full version traceability |
| SAE notification recipient is unreachable | System retries notification up to 3 times at 15-minute intervals, escalates to backup recipient after 3 failures, and logs all retry attempts |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Regulatory non-compliance due to missed SAE/SUSAR reporting timelines | High | Critical | Manual email-based SAE reporting with tracked deadlines (error-prone, not auditable) |
| Transcription errors in manual MedDRA coding lead to inaccurate safety signals | High | High | Dedicated coding team with dual data entry (increases cost by 2 FTEs per study) |
| Inability to generate timely ICSRs delays regulatory submissions | Medium | Critical | Outsourced pharmacovigilance to third-party vendor |
| Patient-reported events not captured in a timely manner | Medium | High | Paper diary collection with delayed transcription (compromises data quality) |

### 11. Assumptions

- MedDRA licensing is in place and the current version of the dictionary is available for integration
- Study protocols define SAE criteria and reporting timelines that can be configured per study in CDOS
- ICSR templates are defined per regulatory authority (FDA, EMA, PMDA) and can be generated programmatically
- Patient-facing ePRO/mobile AE reporting has been approved by relevant IRBs/Ethics Committees
- Sponsor and CRO pharmacovigilance teams provide escalation contacts and backup coverage schedules

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor (Medical Monitor) | TBD | Pending |
| CRO (Pharmacovigilance) | TBD | Pending |
| Site (Investigator) | TBD | Pending |
| Regulatory Affairs | TBD | Pending |
| Quality Assurance | TBD | Pending |

---

## BR-024: Cross-Study Data Harmonization

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-024 |
| **Title** | Cross-Study Data Harmonization |
| **Priority** | P2 |
| **Category** | Data Integration |
| **Source Stakeholder Need(s)** | SN-024, SN-023 |
| **Regulatory Basis** | ICH E9(R1) (Statistical Principles — estimands and pooled analyses), CDISC CDASH/SDTM Implementation Guides (cross-study consistency), FDA Guidance on Integrated Summaries of Safety and Efficacy |
| **Status** | Draft |

### 2. Business Rationale

Pharmaceutical sponsors routinely conduct pooled analyses across multiple studies — for integrated summaries of safety (ISS) and efficacy (ISE) in regulatory submissions, for meta-analyses supporting label expansions, and for internal portfolio-level decision-making. SN-024 explicitly requires consistent data definitions, code lists, and mappings across studies to enable these pooled analyses. SN-023 requires clean, analysis-ready data. Currently, each study is often configured independently with different variable naming conventions, differing code lists for the same concepts (e.g., "Yes/No" vs. "Y/N" vs. "1/0"), and inconsistent CDISC mappings. This forces biostatistics teams to spend 4–8 weeks per pooled analysis on data harmonization — manually reconciling variable definitions, remapping code lists, and resolving semantic conflicts — at a cost of approximately $80K–$150K per analysis. Without centralized harmonization, these costs compound linearly with each additional study, and the risk of mapping errors introduces data integrity concerns in regulatory submissions.

### 3. Detailed Description

The CDOS must provide a central data dictionary service that serves as the single source of truth for variable definitions, code lists, mapping rules, and naming conventions across all studies managed within the platform. When a new study is provisioned, the system must enforce the use of standardized variable definitions from the central dictionary unless a study-specific deviation is explicitly justified, documented, and approved by the Data Management Lead. The data dictionary must include: canonical variable names and descriptions aligned to CDISC CDASH and SDTM standards; controlled terminology and code lists (including CDISC, MedDRA, WHO Drug, and sponsor-specific lists); unit of measure standardizations; derivation rules for computed variables; and mapping rules that translate source system fields to CDISC domains and variables.

The system must support a governance workflow where data stewards can propose new variable definitions, request modifications to existing ones, and deprecate obsolete entries. All changes must go through an approval workflow with impact analysis that identifies which active studies would be affected. When a study uses a variable that differs from the central dictionary standard, the system must flag the deviation and require a mapping rule that translates the study-specific value to the canonical definition for cross-study analysis. The harmonization engine must be able to generate a cross-study mapping matrix that shows, for any set of selected studies, which variables are fully harmonized, which have deviations with documented mappings, and which have unresolved conflicts. This matrix feeds directly into pooled analysis programming by providing biostatisticians with a pre-reconciled view of data consistency across studies.

### 4. Preconditions

- [ ] CDISC CDASH and SDTM controlled terminology packages are loaded into the central dictionary
- [ ] At least one study has been provisioned and is using the central dictionary for variable definitions
- [ ] Data steward roles are defined and assigned with governance authority over the dictionary
- [ ] Existing studies' variable definitions have been inventoried and mapped to the central dictionary (initial migration)

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-024-AC01 | Central dictionary enforcement | A data manager is provisioning a new study | They configure a CRF form and select variables | The system presents canonical variable definitions from the central dictionary; any deviation from the standard triggers a mandatory justification workflow with Data Steward approval |
| BR-024-AC02 | Cross-study mapping matrix | Three studies (Study A, B, C) are configured in CDOS with partially overlapping CRFs | A biostatistician requests a harmonization report for "AE severity" across all three studies | The system generates a mapping matrix showing: Study A uses CTCAE v5.0 grades (fully harmonized), Study B uses a custom 4-point scale with a documented mapping rule, Study C uses CTCAE v4.0 with a version-bridging mapping; the matrix includes confidence scores for each mapping |
| BR-024-AC03 | Code list harmonization | Two studies use different code lists for "Race" — Study A uses CDISC 2023 and Study B uses CDISC 2024 | A pooled analysis is initiated for both studies | The system applies version-bridging rules, maps all race values to the superset of both code lists, flags any unmappable values for manual review, and produces a reconciliation log |
| BR-024-AC04 | Dictionary change impact analysis | A data steward proposes deprecating a code list value in the "AE Outcome" code list | The change is submitted for approval | The system produces an impact report listing all 12 active studies using that code list, the number of affected records (2,347 AEs), and recommended migration actions |
| BR-024-AC05 | Deviation tracking | A study PI insists on using a non-standard vital sign variable name | The data manager creates a deviation mapping from the study-specific name to the canonical dictionary entry | The deviation is documented with justification, approved by the Data Steward, and the mapping is applied during export and pooled analysis so that the data is seamlessly harmonized |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (CDOS Canonical Data Model) | Blocks | The central dictionary extends and governs the canonical data model |
| BR-009 (Study Provisioning) | Enables | New studies must be provisioned through a dictionary-aware workflow |
| BR-022 (Subject Data Portability) | Related | Exports must use harmonized definitions for cross-system consistency |
| BR-002 (CDISC SDTM/ADaM Mapping) | Related | CDISC mappings are a subset of the broader harmonization dictionary |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS Central Dictionary | Writes to, Reads from | Core service hosting variable definitions, code lists, and mapping rules |
| Study Configuration Module | Reads from | Pulls dictionary definitions when provisioning new studies |
| EDC | Reads from | CRF field definitions must align with dictionary variables |
| CDOS Export Engine | Reads from | Uses dictionary mappings to ensure export consistency |
| CDOS Analytics / Reporting | Reads from | Pooled analysis queries reference harmonized definitions |
| CDOS Governance Workflow | Writes to | Manages dictionary change proposals, approvals, and impact analyses |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| VariableDefinition | Create, Read, Update | Canonical variable name, description, data type, allowed values |
| CodeList | Create, Read, Update | Controlled terminology sets with versioning |
| MappingRule | Create, Read | Rules translating study-specific values to canonical definitions |
| StudyDeviation | Create, Read | Documented deviations from dictionary standards with justification |
| ChangeRequest | Create, Read, Update | Governance workflow for dictionary modifications |
| ImpactAnalysis | Create, Read | Automated impact assessment for proposed dictionary changes |
| HarmonizationReport | Read | Cross-study consistency matrices and reconciliation logs |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| A legacy study has variable definitions that cannot be cleanly mapped to the central dictionary | System allows "unmapped" classification with a mandatory data steward review; the legacy study data is still exportable but flagged as non-harmonized in pooled analysis reports |
| Two studies use the same variable name but with different semantic meanings (e.g., "WEIGHT" as kg in one study and lbs in another) | System detects the semantic conflict through unit-of-measure metadata, flags it as a critical deviation, and applies a unit conversion rule during harmonization |
| A code list is updated in the central dictionary but 5 active studies are mid-stream | System applies the update only to newly entered data, preserves original coding for existing records, and provides a version-bridging mapping for cross-study analysis |
| A sponsor acquires a study from another sponsor with entirely different naming conventions | System creates a comprehensive mapping table from the external convention to the CDOS dictionary, requires Data Steward approval, and applies the mapping during data ingestion |
| Two data stewards propose conflicting definitions for the same variable | System detects the conflict during the governance workflow, routes both proposals for joint review, and requires resolution before either can be approved |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Pooled analyses require 4–8 weeks of manual data reconciliation per analysis | High | High | Dedicated harmonization team as a shared service (adds $500K+ annually) |
| Inconsistent variable definitions lead to mapping errors in ISS/ISE submissions | Medium | Critical | Triple-verification by independent statistical programmers (increases timelines by 2–4 weeks) |
| Regulatory authority questions cross-study consistency during review | Medium | High | Post-hoc Define-XML amendments with documented deviations |
| Sponsor unable to perform rapid portfolio-level safety analyses | Medium | High | Ad hoc database solutions managed by individual teams (siloed, not auditable) |

### 11. Assumptions

- CDISC CDASH and SDTM standards are the baseline for all variable definitions in the central dictionary
- A Data Governance Committee exists (or will be established) with authority to approve dictionary changes
- Existing studies can be inventoried and mapped to the central dictionary within a defined migration window
- Biostatistics teams will adopt harmonized definitions for new studies without resistance once governance processes are in place
- The central dictionary supports versioning so that historical studies retain their original definitions while new studies use current standards

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor (Data Management) | TBD | Pending |
| CRO (Data Management) | TBD | Pending |
| Biostatistics | TBD | Pending |
| Regulatory Affairs | TBD | Pending |
| Quality Assurance | TBD | Pending |


---

# Business Requirements: BR-025 and BR-026

---

## BR-025: Audit Trail and Compliance Reporting

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-025 |
| **Title** | Audit Trail and Compliance Reporting |
| **Priority** | P0 |
| **Category** | Compliance |
| **Source Stakeholder Need(s)** | SN-009, SN-016, SN-018, SN-027 |
| **Regulatory Basis** | 21 CFR Part 11 (Electronic Records; Electronic Signatures), ICH E6(R2) Section 5.5 (Trial Management, Data Handling, and Record Keeping), EU Annex 11 (Computerised Systems) |
| **Status** | Draft |

### 2. Business Rationale

Clinical trials are subject to rigorous regulatory scrutiny, and regulators such as the FDA and EMA can initiate inspections at any point during or after a trial. Currently, assembling audit trail evidence for a regulatory inspection requires CRO and sponsor teams to manually extract change logs from multiple siloed systems — EDC, CTMS, safety databases — a process that can take 3–6 weeks and costs upwards of $150,000 per inspection cycle in labor alone. Incomplete or fragmented audit trails have been cited in FDA Warning Letters and EMA GCP inspection findings, directly threatening marketing application timelines. Without a unified, on-demand audit trail reporting capability, CDOS cannot provide the data integrity assurance that regulators, sponsors, and QA teams demand, and the organization remains exposed to compliance risk across every active study.

### 3. Detailed Description

The CDOS platform must provide a comprehensive, on-demand audit trail and compliance reporting capability that captures every data change across all integrated clinical systems. Whenever a record is created, updated, or deleted — whether by a human user, a system integration, or an automated process — the system must record the identity of the actor (user ID, service account, or system component), the exact timestamp (UTC with timezone offset), the field or entity changed, the previous value, the new value, and the reason for change (selected from a controlled vocabulary or free-text comment where permitted).

Users with the appropriate role (e.g., Data Manager, QA Auditor, Sponsor Viewer) can access the audit trail reporting interface from the CDOS compliance module. The interface allows filtering by study protocol, investigative site, individual subject, date range (absolute or relative), change type (create, update, delete, query, signature), and actor. Results are presented in a paginated, sortable table with drill-down capability to view the full change history of any individual record. Users can save filter configurations as named report templates for recurring compliance needs such as "Study Close-Out Audit Package" or "Regulatory Inspection Response."

All audit trail reports can be exported in multiple formats — PDF for human-readable inspection packages, CSV/Excel for further analysis, and XML/JSON for system-to-system integration with eTMF or regulatory submission platforms. Exported reports must include a digital hash (SHA-256) and timestamp to prove the report has not been tampered with after generation. The audit trail itself is append-only and immutable; no user, including system administrators, can modify or delete audit records. Data retention for audit trails must comply with the longest applicable regulatory retention period (typically 15–25 years post-trial completion depending on jurisdiction).

### 4. Preconditions

- [ ] CDOS data integration layer is operational and receiving data from EDC, CTMS, IWRS, and safety systems
- [ ] User authentication and role-based access control (RBAC) are implemented and enforced
- [ ] All data entities in the CDOS canonical model have change-tracking metadata fields defined
- [ ] Controlled vocabulary for "reason for change" codes is defined and published
- [ ] Data retention policies have been approved by Legal and QA

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-025-AC01 | Complete change capture | A user updates a subject's date of birth in the EDC system | The change is synchronized to CDOS | The audit trail records the actor, timestamp, field name, previous value, new value, and reason for change |
| BR-025-AC02 | Multi-dimensional filtering | A QA auditor opens the audit trail report for Study ABC-101 | They filter by Site 005, Subject 005-003, date range Jan–Mar 2026, and change type "Update" | Only matching audit records are displayed; all other records are excluded |
| BR-025-AC03 | Tamper-evident export | A data manager generates an audit trail export for regulatory submission | They select PDF format and click Export | The exported PDF includes a SHA-256 hash, generation timestamp, and is digitally signed by the system |
| BR-025-AC04 | Immutability enforcement | A system administrator attempts to delete an audit trail record via API or database | The delete request is submitted | The request is rejected with an error; the audit record remains unchanged and the attempt itself is logged |
| BR-025-AC05 | Saved report templates | A CRO data manager configures filters for a recurring monthly compliance review | They save the filter set as "Monthly DSMB Audit Package" | The template is available to all authorized users and can be re-run with updated date ranges |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-001 (CDOS Canonical Data Model) | Blocks | Audit trail entities must align with the canonical model's change-tracking schema |
| BR-005 (RBAC Implementation) | Blocks | Actor identity in audit records depends on authenticated user sessions |
| BR-010 (EDC Integration) | Related | Primary source of clinical data changes that must be audited |
| BR-026 (Periodic Access Review) | Related | Access review reports reference audit trail data (last login, activity) |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS Audit Service | Writes to | All change events are persisted to the immutable audit store |
| EDC | Reads from | Source of clinical data change events streamed to CDOS |
| CTMS | Reads from | Source of study management change events |
| eTMF | Syncs with | Audit trail exports may be filed to the electronic Trial Master File |
| CDOS Reporting UI | Writes to | User-facing report builder and export interface |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| AuditEvent | Create, Read | Immutable record of every data change: actor, timestamp, entity, field, old/new values, reason |
| AuditReport | Create, Read | A generated report instance with filters, format, hash, and generation metadata |
| AuditReportTemplate | Create, Read, Update | Saved filter configurations for recurring compliance reports |
| User | Read | User identity referenced in audit events (actor field) |
| Study | Read | Study context for filtering audit events |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| Bulk data import creates 50,000+ audit events at once | System records all events; report pagination handles large result sets without timeout (response < 30s for up to 100K records) |
| User changes their own role or permissions | The audit event records the change; the user cannot suppress or alter the audit record even for their own actions |
| Source system is temporarily unavailable | Change events are queued and processed when connectivity resumes; no events are lost |
| Regulatory inspector requests audit trail for a study completed 10 years ago | System retrieves archived audit data from long-term storage within SLA (< 4 hours) |
| A change is made by an automated system process (e.g., data reconciliation script) | Actor is recorded as the service account or process ID, not a human user |
| Reason for change field is left blank by user | System enforces mandatory reason-for-change on all updates; blank submissions are rejected |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Regulatory inspection findings (483 observations, Warning Letters) due to incomplete audit trails | High | High | Manual audit log extraction from source systems as interim measure (costly, error-prone) |
| Sponsor dissatisfaction and potential CRO contract loss due to inability to demonstrate data integrity | High | High | None — this is a competitive differentiator requirement |
| Data integrity questions during marketing application review delay approval | Medium | High | Retroactive audit trail assembly (6+ month effort per application) |
| GDPR/HIPAA non-compliance if data changes cannot be traced for data subject rights requests | Medium | Medium | Manual log review per incident |

### 11. Assumptions

- All source systems (EDC, CTMS, IWRS, safety) provide change event data via standardized APIs or event streams
- The CDOS platform will be validated per GAMP 5 / 21 CFR Part 11 as part of overall system validation
- Audit trail retention will follow the sponsor's validated retention policy (minimum 15 years)
- Digital signature infrastructure (PKI or equivalent) is available for tamper-evident exports

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [TBD — VP Clinical Operations] | Pending |
| CRO | [TBD — Head of Data Management] | Pending |
| QA/Compliance | [TBD — Director of Quality Assurance] | Pending |
| Regulatory | [TBD — Regulatory Affairs Lead] | Pending |

---

## BR-026: Periodic Access Review Automation

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-026 |
| **Title** | Periodic Access Review Automation |
| **Priority** | P2 |
| **Category** | Compliance |
| **Source Stakeholder Need(s)** | SN-028, SN-014 |
| **Regulatory Basis** | 21 CFR Part 11 §11.10(d) (Limiting system access to authorized individuals), ICH E6(R2) §5.5.3 (Access Control), GDPR Article 32 (Security of Processing), SOC 2 Type II Trust Services Criteria (CC6.1 — Logical Access) |
| **Status** | Draft |

### 2. Business Rationale

Regulatory frameworks and GxP guidelines require that access to clinical systems be limited to authorized individuals and reviewed periodically. In practice, most organizations perform these reviews manually — QA teams export user lists from each system, circulate spreadsheets to study leads for attestation, and reconcile responses. This process typically takes 4–8 weeks per review cycle, is error-prone, and frequently results in dormant or over-privileged accounts remaining active for months after personnel changes. An internal audit of CDOS predecessor systems found that 12% of active accounts belonged to personnel who had left the organization or changed roles, and 8% of accounts had privileges exceeding their current responsibilities. Over-privileged or orphaned accounts represent a material security risk and a direct violation of least-privilege principles mandated by 21 CFR Part 11 and GDPR. Automating periodic access reviews reduces review cycle time from weeks to hours, eliminates manual reconciliation errors, and provides auditable evidence of compliance.

### 3. Detailed Description

The CDOS platform must provide an automated periodic access review capability that generates comprehensive reports of all user accounts, their current status, role assignments, last login timestamps, and privilege levels across all CDOS components. On a configurable schedule (default: quarterly, but adjustable per study or organizational policy), the system automatically generates an access review report and distributes it to designated reviewers (e.g., Study Leads, Site Managers, QA Managers).

The report must clearly identify accounts that require attention: dormant accounts (no login within a configurable threshold, default 90 days), accounts belonging to personnel whose employment or contract status has changed (if integrated with HR/identity provider), accounts with privileges that exceed their assigned role (over-privileged), and accounts that have not been reviewed in the prior cycle. Each flagged account is presented with a recommended action (disable, downgrade privileges, re-attest) and a link for the reviewer to take immediate action directly from the report interface.

Reviewers can attest to the appropriateness of each account's access level, request privilege changes, or flag accounts for removal — all within the CDOS interface. The system tracks attestation status (pending, attested, action-taken) and escalates to QA management if attestations are not completed within the configurable deadline (default: 14 days). A complete audit trail of every access review cycle — including who reviewed, what decisions were made, and when actions were taken — is maintained as part of the system's compliance record.

### 4. Preconditions

- [ ] CDOS user authentication and RBAC system is implemented (dependency on BR-005)
- [ ] User accounts are provisioned via an identity provider (e.g., Okta, Azure AD) or CDOS-native directory
- [ ] Role definitions and privilege mappings are documented and approved by QA
- [ ] Reviewer assignment rules are configured (e.g., Study Lead reviews site users, QA reviews admin accounts)
- [ ] Configurable thresholds for dormant account detection and review cycle frequency are defined

### 5. Acceptance Criteria

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-026-AC01 | Automated report generation | The quarterly access review schedule is configured | The scheduled date arrives | The system generates an access review report listing all active user accounts, their roles, last login dates, and privilege levels |
| BR-026-AC02 | Dormant account flagging | A user account has had no login activity for 92 days and the dormant threshold is set to 90 days | The access review report is generated | The account is flagged as "Dormant" with a recommended action of "Disable" |
| BR-026-AC03 | Over-privileged account detection | A Clinical Research Associate account has been granted Site Admin privileges inconsistent with their role | The access review report is generated | The account is flagged as "Over-Privileged" with a recommended action of "Downgrade Privileges" |
| BR-026-AC04 | Reviewer attestation workflow | A Study Lead receives their quarterly access review report | They review the flagged accounts | They can attest to appropriate access, request changes, or flag for removal; attestation status is tracked and timestamped |
| BR-026-AC05 | Escalation on missed deadline | A reviewer has not completed attestation within the 14-day deadline | The deadline passes | The system automatically escalates the review to QA management with a notification and the report moves to "Overdue" status |

### 6. Dependencies

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-005 (RBAC Implementation) | Blocks | Role definitions and user-account-role mappings must exist before access can be reviewed |
| BR-025 (Audit Trail and Compliance Reporting) | Related | Access review audit trail leverages the same immutable audit infrastructure; dormant account data references login audit events |
| BR-001 (CDOS Canonical Data Model) | Related | User and role entities must be defined in the canonical model |

### 7. Impacted Systems

| System | Impact Type | Description |
|--------|-----------|-------------|
| CDOS Identity & Access Service | Reads from | Source of user accounts, role assignments, and authentication logs |
| CDOS Audit Service | Reads from | Provides last-login and activity data for dormant account detection |
| CDOS Notification Service | Writes to | Sends review assignment and escalation notifications |
| CDOS Reporting UI | Writes to | Access review dashboard and attestation interface |
| HR / Identity Provider (e.g., Okta, Azure AD) | Reads from | Employment status and organizational changes for cross-referencing active accounts |

### 8. Data Entities Involved

| Entity | Operation | Description |
|--------|----------|-------------|
| User | Read | All user account records with status, roles, and last login |
| UserRole | Read | Role-to-privilege mappings for each user |
| AccessReviewCycle | Create, Read | A scheduled review instance (quarterly or ad-hoc) with metadata |
| AccessReviewItem | Create, Read, Update | Per-account review line item with flag, recommendation, and attestation status |
| AuditEvent | Read, Create | Login activity data consumed; review actions recorded as new audit events |

### 9. Edge Cases and Exceptions

| Scenario | Expected Behavior |
|----------|------------------|
| User is on approved leave (e.g., parental leave, sabbatical) during review period | System allows reviewers to mark an account as "Approved Leave — Retain" with an expected return date; account is excluded from dormant flagging until return date passes |
| Identity provider integration is unavailable during scheduled review | System generates report from last-known user data and flags all entries as "Source Unverified"; review proceeds and a supplementary report is generated when integration recovers |
| A user has multiple roles across different studies | Each role assignment is reviewed independently; removing one role does not affect others |
| All accounts at a site are dormant (site closure) | Bulk action capability allows reviewer to disable all accounts with a single attestation; individual rationale can be documented |
| A reviewer leaves the organization mid-cycle | System reassigns pending review items to the reviewer's manager (determined from org hierarchy) and sends notification |
| Emergency access (break-glass) was used | Break-glass access events are flagged prominently in the review with a mandatory attestation requirement |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Dormant or orphaned accounts exploited for unauthorized data access | High | High | Continue manual quarterly spreadsheet-based reviews (current state) |
| Regulatory finding for non-compliance with 21 CFR Part 11 §11.10(d) access controls | High | Medium | Document manual review process as compensating control |
| GDPR violation if accounts of departed employees retain access to personal data | Medium | High | Implement immediate deprovisioning via HR/IdP integration as partial mitigation |
| Increased audit scope and findings due to lack of evidence of periodic reviews | Medium | Medium | Manual evidence collection from each system per audit cycle |

### 11. Assumptions

- The CDOS identity provider integration (e.g., SCIM, SAML) will supply employment status and organizational hierarchy data
- Reviewer assignment can be derived from the CDOS study organizational structure (Study Lead → Site, QA Manager → Admin roles)
- Quarterly review frequency satisfies most sponsor and regulatory expectations; studies with heightened risk may require monthly reviews
- Break-glass (emergency access) events are already captured by the CDOS audit trail (BR-025)

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [TBD — VP Clinical Operations] | Pending |
| CRO | [TBD — Head of IT Security] | Pending |
| QA/Compliance | [TBD — Director of Quality Assurance] | Pending |
| Site | [TBD — Site Management Lead] | Pending |


---

