# CDOS Acceptance Criteria

## Document Metadata

| Field | Value |
|-------|-------|
| Document ID | CDOS-AC-001 |
| Version | 1.0 |
| Author | Agent-FR |
| Date | 2026-05-29 |
| Status | Draft |

---

## FR-001: Study Creation

**AC-001: Create a new Study with valid metadata**

Given a user with Sponsor role is authenticated
When the user submits a Study creation request with protocol ID, title, phase, therapeutic area, and sponsor name
Then a new Study record is created with status DRAFT
And a unique study_id is returned
And an audit trail entry is recorded with the creating user and timestamp

---

## FR-002: Study Versioning

**AC-002: Create a new Protocol version on amendment**

Given an existing Study with Protocol version 1.0
When a protocol amendment is submitted
Then Protocol version 1.1 is created
And the prior version 1.0 is preserved with status SUPERSEDED
And the version history is queryable

---

## FR-003: Site Configuration

**AC-003: Add a Site to a Study**

Given an existing Study in DRAFT status
When a user adds a Site with number, address, principal Investigator, and activation date
Then the Site is linked to the Study with status PENDING_ACTIVATION
And the Site record is visible in the CTMS site list

---

## FR-004: Study Milestone Tracking

**AC-004: Track enrollment milestone**

Given a Study with 5 Sites and a planned first-subject-enrolled date of 2026-06-01
When the first Subject is enrolled at any Site
Then the FSE milestone status changes to ACHIEVED
And the actual date is recorded
And the variance from plan is calculated

---

## FR-005: Visit Schedule Definition

**AC-005: Define a Visit with window parameters**

Given a Study in DRAFT status
When a user defines Visit V2 with window -3/+7 days and procedures [vitals, ECG, labs]
Then the Visit schedule entry is persisted
And the window is enforced during Visit scheduling in Subject management

---

## FR-006: Subject Screening

**AC-006: Screen a Subject and assign screening number**

Given a Study with active Sites
When a Site User initiates screening for a new Subject at Site S001
Then the Subject is assigned a screening number (e.g., S001-001)
And Subject status is set to SCREENED
And informed consent date is recorded

---

## FR-007: Subject Enrollment

**AC-007: Enroll a Subject after eligibility and randomization**

Given a screened Subject with passing eligibility (AC-009 satisfied)
When IWRS returns a treatment assignment
Then Subject status transitions from SCREENED to ENROLLED
And the randomization number, treatment arm, and kit number are recorded
And a subject.enrolled event is published

---

## FR-008: Subject Withdrawal

**AC-008: Withdraw a Subject with cascading updates**

Given an enrolled Subject with 3 completed Visits
When a user records withdrawal with reason "Adverse Event" and date 2026-07-15
Then Subject status changes to WITHDRAWN
And all future Visit records are updated to CANCELLED
And the withdrawal reason and date are stored

---

## FR-009: Eligibility Assessment

**AC-009: Evaluate eligibility criteria automatically**

Given a screened Subject with recorded inclusion/exclusion criteria data
When eligibility assessment is triggered
Then the system evaluates each criterion against the Subject data
And returns a result of PASS or FAIL with the list of failing criteria if FAIL

---

## FR-010: Consent Tracking

**AC-010: Record informed consent for a Subject**

Given a Subject at Site S001
When the Site User records consent with version 2.0, date 2026-06-01, and Site attestation
Then the consent record is linked to the Subject and Protocol version 2.0
And the consent is visible in the Subject's consent history

---

## FR-011: EDC CRF Data Ingestion

**AC-011: Ingest CRF data from EDC**

Given EDC has new CRFPage data for Subject S001-001 Visit V1
When the EDC adapter receives the data via REST API
Then the data is validated against CDASH conventions
And stored in the canonical data model
And an audit trail entry records the data source as EDC

---

## FR-012: EDC Query Synchronization

**AC-012: Synchronize an EDC Query**

Given an open Query in EDC for Subject S001-001 CRFPage DM
When the Query sync job runs
Then the Query record is created/updated in CDOS with status OPEN
And the Query is visible in the CTMS monitoring dashboard

---

## FR-013: EDC Data Reconciliation

**AC-013: Reconcile Subject counts between EDC and CDOS**

Given EDC reports 150 enrolled Subjects and CDOS has 148
When the daily reconciliation job runs
Then a discrepancy report is generated showing 2 missing Subjects
And the report is sent to the Data Manager role

---

## FR-014: CTMS Site Activation Sync

**AC-014: Sync Site activation from CTMS**

Given a Site S002 with PENDING_ACTIVATION status in CDOS
When CTMS updates Site S002 to ACTIVE with initiation visit completed
Then CDOS updates Site S002 status to ACTIVE
And the activation date is recorded

---

## FR-015: CTMS Monitoring Visit Reports

**AC-015: Ingest a monitoring visit report**

Given a CRA completes a monitoring visit at Site S001
When the visit report is submitted in CTMS
Then CDOS creates a monitoring_visit record linked to Site S001
And extracts issue count and critical finding count

---

## FR-016: CTMS Investigator Profile Sync

**AC-016: Flag a non-compliant Investigator**

Given an Investigator with CV expiry date of 2026-05-01 (expired)
When the Investigator sync job runs
Then the Investigator is flagged as NON_COMPLIANT
And a notification is sent to the CRA role

---

## FR-017: LIMS Lab Result Ingestion

**AC-017: Ingest lab results from LIMS**

Given LIMS has new LabResult data for Subject S001-001 Sample SB-001
When the LIMS adapter receives the data
Then the LabResult is mapped to SDTM LB domain variables (LBTESTCD, LBORRES, LBORRESU)
And stored with specimen identifier, analyte, result, unit, and normal range

---

## FR-018: LIMS Sample Chain of Custody

**AC-018: Track Sample from collection to LIMS receipt**

Given a Sample collected at Site S001 on 2026-06-01
When the Sample is shipped and received by LIMS
Then the Sample record shows status transitions: COLLECTED → SHIPPED → RECEIVED
And the LIMS accession number is recorded upon receipt

---

## FR-019: LIMS Abnormal Value Flagging

**AC-019: Flag an abnormal lab value**

Given a LabResult for ALT = 150 U/L with upper normal limit = 40 U/L
When the result is ingested from LIMS
Then the LabResult is flagged as HIGH_ABNORMAL
And a Query is automatically generated in EDC for investigator review

---

## FR-020: Safety AE Case Intake

**AC-020: Ingest an AE case from Safety**

Given Safety system has a new AdverseEvent case for Subject S001-001
When the Safety adapter receives the case data
Then the AdverseEvent is classified by severity (MILD/MODERATE/SEVERE), seriousness, and expectedness
And linked to the Subject and Study

---

## FR-021: SAE Expedited Reporting

**AC-021: Generate ICSR for an SAE**

Given an AdverseEvent classified as SERIOUS and SUSAR
When the SAE is processed
Then an ICSR payload is generated within 24 hours
And submitted to the Safety system
And the medical monitor is notified

---

## FR-022: Safety Signal Aggregation

**AC-022: Detect an emerging safety signal**

Given 10 AdverseEvents across 3 Studies for MedDRA PT "Hepatic enzyme increased"
When the signal aggregation job runs
Then the proportional reporting ratio is calculated
And if the threshold is exceeded, a signal alert is generated for pharmacovigilance review

---

## FR-023: IWRS Randomization Request

**AC-023: Randomize a Subject via IWRS**

Given a Subject with eligibility PASS
When a randomization request is sent to IWRS with stratification factors (age group, disease severity)
Then IWRS returns treatment arm (ACTIVE/PLACEBO), kit number, and randomization number
And the response is recorded on the Subject record

---

## FR-024: IWRS Drug Supply Reconciliation

**AC-024: Reconcile dispensing records**

Given IWRS records 50 kits dispensed at Site S001 and EDC records 48 doses administered
When the reconciliation job runs
Then a discrepancy report shows 2 kits dispensed but not recorded as administered
And the report is routed to clinical supply management

---

## FR-025: IWRS Unblinding Request

**AC-025: Process an emergency unblinding request**

Given a medical emergency requiring unblinding of Subject S001-001
When the Medical Monitor submits an unblinding request with justification
Then IWRS returns the treatment assignment
And an audit trail entry records the user, justification, and timestamp
And the medical monitor receives a notification

---

## FR-026: Audit Trail

**AC-026: Record a data change in the audit trail**

Given a Data Manager updates Subject S001-001 status from ENROLLED to COMPLETED
When the change is saved
Then an audit trail entry is created with user, timestamp, old value (ENROLLED), new value (COMPLETED), and reason
And the entry is tamper-evident (hash-chained)

---

## FR-027: Role-Based Access Control

**AC-027: Enforce role-based data visibility**

Given a user with CRA role assigned to Sites S001 and S002
When the user queries Subject data
Then only Subjects from Sites S001 and S002 are returned
And data from other Sites is not visible

---

## FR-028: Electronic Signature

**AC-028: Apply electronic signature to database lock**

Given all data queries are resolved and a Data Manager initiates database lock
When the Data Manager applies an e-signature with meaning "I approve database lock"
Then the database is locked for editing
And an e-signature record is created with user, date/time, and meaning
And the action is recorded in the audit trail

---

## FR-029: Data Validation Rules

**AC-029: Execute edit check on incoming data**

Given a CRFPage with systolic blood pressure = 300 mmHg (outside configured range 60-250)
When the data validation engine processes the CRFPage
Then a Query is generated with severity HIGH
And the Query is linked to the specific data point

---

## FR-030: SDTM Mapping and Export

**AC-030: Export SDTM DM domain**

Given Study CDOS-001 has 100 enrolled Subjects
When the SDTM export is triggered for domain DM
Then a DM.xpt file is produced with USUBJID, SUBJID, SITEID, AGE, SEX, RACE, ARMCD
And a Define-XML v2.1 file is produced documenting the DM domain metadata

---

## FR-031: Study Dashboard

**AC-031: Display enrollment progress on dashboard**

Given Study CDOS-001 with a target enrollment of 200 and 150 enrolled Subjects
When a Sponsor user accesses the dashboard
Then enrollment progress shows 75% (150/200)
And per-Site enrollment rates are displayed

---

## FR-032: Enrollment Forecasting

**AC-032: Forecast enrollment completion date**

Given Study CDOS-001 with current enrollment rate of 5 Subjects/week and 50 remaining
When the forecast is calculated
Then the projected completion date is 10 weeks from today
And the confidence interval is displayed

---

## FR-033: Regulatory Submission Export

**AC-033: Produce eCTD package for submission**

Given Study CDOS-001 SDTM datasets are finalized
When the submission export is triggered
Then an eCTD package is produced with Study data, Define-XML, and validation report
And the package is delivered to RegSubmit

---

## FR-034: Event-Driven Orchestration

**AC-034: Publish and consume domain events**

Given a Subject is enrolled (status changed to ENROLLED)
When the enrollment is saved
Then a subject.enrolled event is published to the event bus
And downstream consumers (CTMS, IWRS, Safety) receive the event within 30 seconds

---

## FR-035: Cross-System Data Reconciliation

**AC-035: Nightly reconciliation produces discrepancy report**

Given EDC, CTMS, LIMS, Safety, and IWRS have data for Study CDOS-001
When the nightly reconciliation job completes
Then a discrepancy report is generated listing mismatches between systems
And the report is emailed to the Data Manager role by 08:00 local time

---

## Summary

| Metric | Count |
|--------|-------|
| Total FRs covered | 35 |
| Total Acceptance Criteria | 35 |
| Format | Given/When/Then |
