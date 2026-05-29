# CDOS Data Flows

## Document Metadata

| Field | Value |
|-------|-------|
| Document ID | CDOS-DF-001 |
| Version | 1.0 |
| Author | Agent-FR |
| Date | 2026-05-29 |
| Status | Draft |

---

## Data Flow Inventory

| ID | Function Name | Source System | Target System | FR Trace |
|----|--------------|---------------|---------------|----------|
| DF-001 | EDC CRF Data Ingestion | EDC | CDOS | FR-011 |
| DF-002 | EDC Query Synchronization | EDC ↔ CDOS | CDOS ↔ CTMS | FR-012 |
| DF-003 | CTMS Site Activation Sync | CTMS | CDOS | FR-014 |
| DF-004 | CTMS Monitoring Visit Report Ingestion | CTMS | CDOS | FR-015 |
| DF-005 | LIMS Lab Result Ingestion | LIMS | CDOS | FR-017 |
| DF-006 | LIMS Sample Chain of Custody | CDOS → LIMS | LIMS | FR-018 |
| DF-007 | Safety AE Case Intake | Safety | CDOS | FR-020 |
| DF-008 | SAE Expedited Reporting | CDOS | Safety | FR-021 |
| DF-009 | IWRS Randomization Request | CDOS | IWRS | FR-023 |
| DF-010 | IWRS Drug Supply Reconciliation | IWRS ↔ CDOS ↔ EDC | CDOS | FR-024 |
| DF-011 | SDTM Export and Submission | CDOS | RegSubmit | FR-030 |
| DF-012 | Cross-System Reconciliation | EDC, CTMS, LIMS, Safety, IWRS | CDOS | FR-035 |

---

## Detailed Data Flows

### DF-001: EDC CRF Data Ingestion

**Function:** Capture and normalize CRF data from EDC into the CDOS canonical model.

**Input:**
- **Source:** EDC (e.g., Medidata Rave, Veeva Vault CDMS)
- **Data Elements:**
  - CRFPage (form ID, page status, completion date)
  - Subject identifier (screening number, randomization number)
  - Study identifier (protocol ID)
  - Site identifier (site number)
  - Field-level data (variable name, value, data type, collected date)
  - CDASH domain code (DM, AE, CM, EX, LB, VS)

**Process:**
1. EDC adapter polls or receives webhook with new/updated CRFPage data
2. Map incoming field names to CDASH v2.1 standard variable names
3. Validate field data types, ranges, and required-field presence
4. Resolve Subject and Site identifiers against CDOS canonical records
5. Store validated data in the canonical data model
6. Record audit trail entry with source=EDC, timestamp, and user context
7. Publish `crfpage.updated` event to the event bus

**Output:**
- **Target:** CDOS Canonical Data Store
- **Data Elements:**
  - CRFPage (canonical record with CDASH-mapped variables)
  - Subject link (subject_id FK)
  - Visit link (visit_id FK)
  - Audit trail entry
- **Event:** `crfpage.updated` published to event bus

**Systems Involved:** EDC, CDOS API Gateway, CDOS Canonical Data Store, Event Bus

---

### DF-002: EDC Query Synchronization

**Function:** Bidirectional sync of data clarification queries between EDC and CDOS.

**Input:**
- **Source:** EDC
- **Data Elements:**
  - Query (query_id, status [OPEN/ANSWERED/CLOSED], severity)
  - CRFPage reference (form, field, value queried)
  - Subject and Site identifiers
  - Query text and response text
  - Open date, response date, close date

**Process:**
1. EDC adapter receives Query updates via scheduled sync (every 15 minutes)
2. Match incoming queries to existing CDOS query records by query_id
3. Update query status, response text, and dates
4. For queries in OPEN status > 7 days, escalate to CTMS monitoring dashboard
5. For queries closed in EDC, mark resolved in CDOS and remove from escalation queue
6. Record audit trail for each status change

**Output:**
- **Target:** CDOS Query Store, CTMS Monitoring Dashboard
- **Data Elements:**
  - Query record (updated status, dates, response)
  - Escalation flag (for overdue queries)
  - Audit trail entry
- **Event:** `query.status_changed` published to event bus

**Systems Involved:** EDC, CDOS, CTMS, Event Bus

---

### DF-003: CTMS Site Activation Sync

**Function:** Synchronize Site activation milestones from CTMS to CDOS.

**Input:**
- **Source:** CTMS (e.g., Veeva Vault CTMS)
- **Data Elements:**
  - Site (site_id, site_number, status [ACTIVE/INACTIVE])
  - Activation milestones (regulatory_approval_date, site_initiation_visit_date, pharmacy_approval_date)
  - Investigator assignment (investigator_id, role)

**Process:**
1. CTMS adapter polls for Site status changes (hourly)
2. Compare incoming Site status with CDOS Site record
3. If status changed to ACTIVE, update CDOS Site record
4. Link Investigator profile to Site record
5. If Site deactivated, update status and flag for Subject reassignment workflow
6. Publish `site.activated` or `site.deactivated` event

**Output:**
- **Target:** CDOS Site Store
- **Data Elements:**
  - Site record (updated status, activation date, milestones)
  - Investigator-Site link
- **Event:** `site.activated` or `site.deactivated` published

**Systems Involved:** CTMS, CDOS, Event Bus

---

### DF-004: CTMS Monitoring Visit Report Ingestion

**Function:** Ingest monitoring visit reports and extract actionable findings.

**Input:**
- **Source:** CTMS
- **Data Elements:**
  - Monitoring visit (visit_id, visit_type [ROUTINE/TRIGGERED], visit_date)
  - Site reference (site_id)
  - Findings (finding_count, critical_finding_count, action_items)
  - CRA identifier

**Process:**
1. CTMS adapter receives monitoring visit report on submission event
2. Extract visit metadata and findings summary
3. Link monitoring visit to the corresponding Site record in CDOS
4. If critical_finding_count > 0, generate a Site quality alert
5. Update Site performance metrics (findings per visit trend)
6. Publish `monitoring_visit.completed` event

**Output:**
- **Target:** CDOS Monitoring Store, Site Dashboard
- **Data Elements:**
  - Monitoring visit record (linked to Site)
  - Findings summary
  - Site quality alert (if critical findings)
- **Event:** `monitoring_visit.completed` published

**Systems Involved:** CTMS, CDOS, Event Bus

---

### DF-005: LIMS Lab Result Ingestion

**Function:** Receive lab results from LIMS and map to SDTM LB domain.

**Input:**
- **Source:** LIMS (e.g., Covance LIMS, Medidata Rave Lab)
- **Data Elements:**
  - LabResult (analyte_code, result_value, result_unit, normal_range_low, normal_range_high, collection_date)
  - Sample (sample_id, specimen_type, collection_datetime)
  - Subject identifier (subject_number)
  - Study and Site identifiers

**Process:**
1. LIMS adapter receives LabResult batch via HL7 FHIR or REST API
2. Resolve Subject identifier to CDOS subject_id
3. Map analyte code to SDTM LBTESTCD controlled terminology
4. Map result to SDTM LBORRES (original result) and LBSTRESN (standardized numeric)
5. Evaluate normal range: set LBNRIND (normal range indicator) to NORMAL/HIGH/LOW/ABNORMAL
6. Store LabResult in canonical model linked to Subject and Sample
7. If abnormal, trigger FR-019 abnormal value flagging workflow

**Output:**
- **Target:** CDOS Lab Data Store
- **Data Elements:**
  - LabResult (SDTM LB domain mapped: LBTESTCD, LBORRES, LBORRESU, LBSTRESN, LBNRIND)
  - Sample link (sample_id FK)
  - Subject link (subject_id FK)
- **Event:** `lab.result_received` published

**Systems Involved:** LIMS, CDOS API Gateway, CDOS Canonical Data Store, Event Bus

---

### DF-006: LIMS Sample Chain of Custody

**Function:** Track biological specimens from collection through LIMS processing.

**Input:**
- **Source:** CDOS (Site-collected specimen data), LIMS (receipt confirmation)
- **Data Elements:**
  - Sample (sample_id, specimen_type, collection_datetime, collection_site)
  - Shipping (tracking_number, ship_date, temperature_log)
  - LIMS receipt (accession_number, receipt_datetime, condition_on_receipt)

**Process:**
1. Site User records Sample collection in CDOS (status: COLLECTED)
2. Shipping details are recorded when Sample leaves the Site (status: SHIPPED)
3. LIMS adapter receives receipt confirmation (status: RECEIVED)
4. LIMS accession number is recorded on the Sample record
5. If temperature excursion detected, flag Sample as POTENTIALLY_COMPROMISED
6. Record full chain of custody in audit trail

**Output:**
- **Target:** CDOS Sample Store
- **Data Elements:**
  - Sample record (status: COLLECTED → SHIPPED → RECEIVED)
  - LIMS accession number
  - Temperature excursion flag (if applicable)
  - Chain of custody audit entries

**Systems Involved:** CDOS, LIMS

---

### DF-007: Safety AE Case Intake

**Function:** Receive and classify adverse event case data from the Safety system.

**Input:**
- **Source:** Safety (e.g., Argus Safety, ArisGlobal)
- **Data Elements:**
  - AdverseEvent (ae_id, meddra_code, meddra_pt, severity, seriousness, expectedness, onset_date, outcome)
  - Subject identifier
  - Study identifier
  - Reporter (name, role, report_date)

**Process:**
1. Safety adapter receives AE case via ICSR E2B(R3) format or REST API
2. Map MedDRA code to the AdverseEvent canonical model
3. Classify severity (MILD/MODERATE/SEVERE) per CTCAE criteria
4. Determine seriousness (death, life-threatening, hospitalization, disability, congenital anomaly, other)
5. Evaluate expectedness against the Investigator's Brochure (IB) listed events
6. Link AdverseEvent to Subject and Study records
7. Publish `ae.received` event
8. If SAE, trigger DF-008 SAE expedited reporting flow

**Output:**
- **Target:** CDOS Safety Data Store
- **Data Elements:**
  - AdverseEvent record (SDTM AE domain mapped: AETERM, AESEV, AESER, AEACN, AEREL)
  - Subject link (subject_id FK)
  - Study link (study_id FK)
- **Event:** `ae.received` published

**Systems Involved:** Safety, CDOS, Event Bus

---

### DF-008: SAE Expedited Reporting

**Function:** Generate and transmit ICSR for serious adverse events meeting reporting thresholds.

**Input:**
- **Source:** CDOS AdverseEvent store
- **Data Elements:**
  - AdverseEvent (ae_id, seriousness criteria, expectedness, causality)
  - Subject demographics (age, sex, race, medical history)
  - Study drug exposure (dose, route, frequency, start/stop dates)
  - Concomitant Medications
  - LabResult (relevant lab values)
  - Narrative text

**Process:**
1. Event bus receives `ae.received` event for an SAE
2. Medical Monitor reviews and classifies as SUSAR or non-SUSAR
3. Compile ICSR payload in E2B(R3) format with all required data elements
4. Validate ICSR against regulatory completeness rules (FDA 21 CFR 312.32, EU CTR)
5. Transmit ICSR to Safety system for regulatory submission
6. Generate notification to Medical Monitor and Sponsor
7. Record submission timestamp and tracking number in audit trail

**Output:**
- **Target:** Safety system (for regulatory submission)
- **Data Elements:**
  - ICSR payload (E2B(R3) format)
  - Submission confirmation (tracking number, submission timestamp)
  - Notification to Medical Monitor
- **Event:** `sae.reported` published

**Systems Involved:** CDOS, Safety, Event Bus

---

### DF-009: IWRS Randomization Request

**Function:** Request and record treatment randomization from IWRS.

**Input:**
- **Source:** CDOS (Subject eligibility confirmed)
- **Data Elements:**
  - Subject (subject_id, screening_number, site_id)
  - Study (study_id, protocol_id)
  - Stratification factors (age_group, disease_severity, region)
  - Eligibility confirmation (PASS/FAIL)

**Process:**
1. CDOS receives confirmation that Subject eligibility = PASS
2. Compile randomization request with Subject, Study, and stratification factors
3. Send request to IWRS via REST API
4. IWRS returns treatment assignment (treatment_arm, kit_number, randomization_number)
5. Record randomization data on the Subject record
6. Update Subject status to ENROLLED
7. Publish `subject.enrolled` event with treatment arm information
8. Record audit trail entry for randomization

**Output:**
- **Target:** CDOS Subject Store, IWRS
- **Data Elements:**
  - IWRS request (subject_id, study_id, stratification factors)
  - IWRS response (treatment_arm, kit_number, randomization_number)
  - Updated Subject record (status: ENROLLED)
- **Event:** `subject.enrolled` published

**Systems Involved:** CDOS, IWRS, Event Bus

---

### DF-010: IWRS Drug Supply Reconciliation

**Function:** Reconcile drug dispensing records between IWRS and EDC dosing data.

**Input:**
- **Source:** IWRS (dispensing records), EDC (dosing CRFPage data)
- **Data Elements:**
  - IWRS dispensing (kit_number, dispense_date, site_id, subject_id)
  - EDC dosing (dose_date, kit_number, dose_amount, route)
  - Site drug inventory (kits_received, kits_dispensed, kits_returned)

**Process:**
1. Pull dispensing records from IWRS for the reconciliation period
2. Pull dosing records from EDC for the same period
3. Match records by kit_number and subject_id
4. Identify dispensed-but-not-administered (kit dispensed, no EDC dose record)
5. Identify administered-but-not-dispensed (EDC dose record, no IWRS dispensing)
6. Calculate Site-level inventory variance
7. Generate discrepancy report with mismatch details

**Output:**
- **Target:** CDOS Reconciliation Store
- **Data Elements:**
  - Reconciliation report (matched_count, mismatched_records, variance_per_site)
  - Discrepancy list (kit_number, subject_id, mismatch_type, iwrs_value, edc_value)
  - Inventory variance per Site
- **Event:** `reconciliation.drug_supply.completed` published

**Systems Involved:** IWRS, EDC, CDOS

---

### DF-011: SDTM Export and Regulatory Submission

**Function:** Transform canonical data to SDTM domains and produce eCTD submission package.

**Input:**
- **Source:** CDOS Canonical Data Store
- **Data Elements:**
  - Subject demographics (DM domain)
  - AdverseEvent data (AE domain)
  - LabResult data (LB domain)
  - Exposure/Dose data (EX domain)
  - Concomitant Medications (CM domain)
  - Study metadata (Protocol, Sites, Visit schedule)

**Process:**
1. Transform canonical Subject records to SDTM DM domain (USUBJID, SUBJID, SITEID, AGE, SEX, RACE, ARMCD, ARM)
2. Transform canonical AdverseEvent records to SDTM AE domain (AETERM, AESEV, AESER, AESTDTC, AEENDTC)
3. Transform canonical LabResult records to SDTM LB domain (LBTESTCD, LBORRES, LBORRESU, LBSTRESN, LBNRIND)
4. Generate Define-XML v2.1 metadata file documenting all domains, variables, and controlled terminology
5. Run OpenCDISC/CDISC Validator conformance checks
6. Package datasets, Define-XML, and validation report into eCTD structure
7. Transmit package to RegSubmit system

**Output:**
- **Target:** RegSubmit, CDOS Submission Store
- **Data Elements:**
  - SDTM XPT files (DM.xpt, AE.xpt, LB.xpt, EX.xpt, CM.xpt)
  - Define-XML v2.1 file
  - Validation report (errors, warnings, conformance status)
  - eCTD package structure
- **Event:** `submission.export.completed` published

**Systems Involved:** CDOS, RegSubmit

---

### DF-012: Cross-System Nightly Reconciliation

**Function:** Reconcile data across all external systems to identify discrepancies.

**Input:**
- **Source:** EDC, CTMS, LIMS, Safety, IWRS
- **Data Elements:**
  - Subject counts per Study and Site (EDC vs. CDOS)
  - Site activation status (CTMS vs. CDOS)
  - LabResult counts per Subject (LIMS vs. CDOS)
  - AdverseEvent counts per Subject (Safety vs. CDOS)
  - Randomization and dispensing counts (IWRS vs. CDOS)

**Process:**
1. Pull summary counts from each external system via adapter APIs
2. Pull corresponding counts from CDOS canonical data store
3. Compare counts by Study, Site, and Subject
4. Identify mismatches: missing records, status discrepancies, count differences
5. Generate a structured discrepancy report with system pairs, entity type, and variance
6. Email the report to Data Manager role by 08:00 local time
7. Store the report in CDOS for historical trending

**Output:**
- **Target:** CDOS Reconciliation Store, Data Manager email
- **Data Elements:**
  - Discrepancy report (system_pair, entity_type, cdos_count, external_count, variance, severity)
  - Summary statistics (total_discrepancies, by_system, by_severity)
- **Event:** `reconciliation.nightly.completed` published

**Systems Involved:** EDC, CTMS, LIMS, Safety, IWRS, CDOS, Event Bus

---

## Summary

| Metric | Count |
|--------|-------|
| Total Data Flows | 12 |
| Integration Functions (EDC, CTMS, LIMS, Safety, IWRS) | 10 |
| Internal Functions | 2 |
| Systems Involved | EDC, CTMS, LIMS, Safety, IWRS, RegSubmit, CDOS, Event Bus |
