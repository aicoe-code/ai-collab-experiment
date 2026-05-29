# CDOS Use Cases

This document defines the use cases for the Clinical Development Operating System (CDOS). Each use case describes a complete interaction scenario between a system actor and CDOS, with main flow, preconditions, postconditions, and alternative flows.

---

## UC-001: Ingest Clinical Data from EDC System

**Actor:** CDOS Integration Service (automated), CRA (trigger/configure)  
**Related BR:** BR-001  
**Preconditions:**
- Study is configured in CDOS with EDC connection parameters
- EDC system is accessible and credentials/tokens are valid
- Canonical data model for the study is defined

**Main Flow:**
1. CRA configures EDC connection for a study (system URL, API credentials, study identifier)
2. CDOS validates connectivity to the EDC system
3. CDOS initiates a scheduled or on-demand data pull from EDC
4. EDC returns CRFPage data for all Subjects at the specified Sites
5. CDOS transforms incoming data from EDC-specific format to the canonical Subject-Visit-CRFPage model
6. CDOS stores canonical data with source provenance metadata (source system, extraction timestamp, record hash)
7. CDOS logs the ingestion event in the audit trail

**Postconditions:**
- EDC data is available in the canonical data model
- Ingestion event is recorded in the audit trail
- Dashboard metrics are updated with latest data entry statistics

**Alternative Flows:**
- **3a.** EDC system is unreachable: CDOS logs a connection error, retries per configured retry policy (exponential backoff, max 5 attempts), and raises an alert to the integration team after exhausting retries
- **5a.** Data validation fails: CDOS quarantines invalid records, generates data quality exceptions, and notifies the Data Manager with details of the validation failures
- **5b.** Duplicate records detected: CDOS applies deduplication logic (matching on Subject ID, Visit, Form, Field) and logs merge decisions

---

## UC-002: Generate SDTM Datasets for Regulatory Submission

**Actor:** Data Manager, Biostatistician  
**Related BR:** BR-007, BR-015  
**Preconditions:**
- Study data has been ingested and is available in the canonical model
- SDTM mapping configuration (domain mappings, controlled terminology, codelist references) is defined for the study
- All data queries are resolved or acknowledged

**Main Flow:**
1. Data Manager selects a study and initiates SDTM dataset generation
2. CDOS retrieves all canonical data for the study
3. CDOS applies SDTM v3.4 mapping rules per the configured mapping specification
4. CDOS generates SDTM domain datasets (DM, AE, LB, EX, CM, etc.)
5. CDOS generates Define-XML v2.1 metadata describing all datasets, variables, and controlled terminology
6. CDOS performs validation checks against SDTM conformance rules
7. CDOS packages datasets and Define-XML for review
8. Data Manager reviews generated datasets, validates against study specifications
9. Data Manager approves and exports the SDTM package

**Postconditions:**
- SDTM datasets and Define-XML are generated and available for download
- Generation metadata (timestamp, data snapshot version, mapping version) is recorded
- Regulatory submission package can be assembled from approved datasets

**Alternative Flows:**
- **3a.** Mapping rule not found for a data element: CDOS flags unmapped elements and generates a mapping gap report for the Data Manager to resolve
- **6a.** SDTM conformance errors detected: CDOS generates a conformance report with error severity (Error, Warning, Notice) and blocks export until errors are resolved or explicitly acknowledged
- **8a.** Data Manager requests revisions: CDOS allows re-generation with modified mapping rules or data corrections, maintaining version history

---

## UC-003: Monitor Cross-Study Enrollment Progress

**Actor:** Sponsor Clinical Operations Lead, CRO Project Manager  
**Related BR:** BR-012, BR-014  
**Preconditions:**
- At least one study is active in CDOS with enrollment targets defined
- Site activation data is synchronized from CTMS
- Subject screening and enrollment events are being ingested

**Main Flow:**
1. Actor logs into CDOS and navigates to the Cross-Study Dashboard
2. CDOS displays a summary view: total active studies, overall enrollment vs. target, sites activated vs. planned
3. Actor drills down into a specific study
4. CDOS displays per-site enrollment metrics: screened, enrolled, withdrawn, screen failure rate
5. CDOS displays enrollment forecast line chart based on historical accrual rates
6. Actor identifies an underperforming site and clicks for details
7. CDOS shows site-level detail: CRA assignments, open queries, protocol deviations, last data entry date
8. Actor exports a PDF/Excel enrollment report for stakeholder distribution

**Postconditions:**
- Actor has actionable enrollment intelligence
- Dashboard view state is saved as a user preference

**Alternative Flows:**
- **2a.** No studies are active: CDOS displays an onboarding prompt to create or import a study
- **5a.** Insufficient data for forecasting: CDOS displays a message indicating minimum data threshold not met and shows current accrual rate without projection
- **6a.** Site has critical flags: CDOS highlights the site with a red indicator and shows a summary of blocking issues (e.g., regulatory hold, staffing gap)

---

## UC-004: Resolve Data Clarification Query

**Actor:** Site Coordinator (Data Entry Person), CRA  
**Related BR:** BR-017, BR-013  
**Preconditions:**
- A CRFPage has been submitted for a Subject
- CDOS edit checks have identified a discrepancy and generated a Query
- Site Coordinator has appropriate role and training status

**Main Flow:**
1. CDOS generates a Query automatically when an edit check fails (e.g., systolic BP > 200 mmHg)
2. CDOS assigns the Query to the Site with full context: Subject ID, Visit, Form, Field, entered value, expected range, edit check rule
3. Site Coordinator receives a Query notification
4. Site Coordinator opens the Query, reviews the context and original source data
5. Site Coordinator either corrects the data entry or provides a clarification comment
6. CDOS re-evaluates the edit check with the updated data
7. If the check passes, CDOS closes the Query with resolution status and timestamp
8. CRA reviews closed Queries during monitoring visit and verifies resolutions

**Postconditions:**
- Query is resolved with full audit trail (who opened, responded, resolved, verified)
- Data is corrected if applicable, with original value preserved in audit trail
- Query metrics are updated in the monitoring dashboard

**Alternative Flows:**
- **5a.** Site Coordinator escalates the Query: CDOS routes the Query to the CRA with escalation reason; CRA investigates and either resolves or escalates further to the Data Manager
- **5b.** Site Coordinator disputes the Query: Site Coordinator marks Query as "disputed" with justification; CRA reviews and either closes as "valid as-is" or reopens with instructions
- **6a.** Edit check still fails after correction: CDOS reopens the Query with updated context showing the new discrepancy

---

## UC-005: Report and Escalate a Serious Adverse Event

**Actor:** Investigator, CRA, Sponsor Safety Officer  
**Related BR:** BR-023, BR-004  
**Preconditions:**
- Subject is enrolled and active in a study
- Site staff have identified a potential AdverseEvent

**Main Flow:**
1. Investigator or Coordinator enters AdverseEvent data: onset date, description, severity, causality assessment, outcome, concomitant medications
2. CDOS applies MedDRA coding suggestions based on the event description
3. Investigator confirms or adjusts the MedDRA preferred term
4. CDOS evaluates the event against SAE criteria (death, life-threatening, hospitalization, disability, congenital anomaly)
5. If SAE criteria are met, CDOS flags the event as an SAE and triggers the SAE workflow
6. CDOS notifies the Sponsor Safety Officer and CRA immediately via configured notification channels
7. CDOS transmits the SAE data to the Safety system (Argus Safety / ArisGlobal) via the safety adapter
8. CDOS tracks regulatory reporting timelines (e.g., 15-day reporting clock for SUSARs) and displays countdown on the safety dashboard
9. Safety Officer reviews, assesses SUSAR status, and completes regulatory filing

**Postconditions:**
- AdverseEvent is recorded in the canonical model with MedDRA coding
- SAE/SUSAR notifications are sent to all required parties
- Safety system has received the Individual Case Safety Report (ICSR)
- Regulatory timeline tracking is active

**Alternative Flows:**
- **4a.** Event does not meet SAE criteria: CDOS records the event as a non-serious AE and monitors for upgrades based on follow-up data
- **7a.** Safety system integration fails: CDOS queues the transmission, retries per policy, and raises an urgent alert to the safety operations team; manual fallback procedures are triggered
- **8a.** SUSAR identified: CDOS applies expedited reporting rules, escalates to the Sponsor Medical Officer, and initiates the 7-day (fatal/life-threatening) or 15-day reporting clock

---

## UC-006: Configure and Provision a New Study

**Actor:** Sponsor Study Lead, CRO Project Manager  
**Related BR:** BR-016, BR-001  
**Preconditions:**
- Protocol is finalized and approved
- Study team members have CDOS accounts with appropriate roles
- Source systems (EDC, LIMS, IWRS) are available

**Main Flow:**
1. Study Lead creates a new Study in CDOS with protocol metadata (protocol number, title, phase, therapeutic area, target enrollment)
2. Study Lead selects a study template (e.g., Phase III, Oncology, Two-Arm)
3. CDOS applies the template, pre-populating visit schedules, form library, and default edit checks
4. Study Lead customizes the study configuration: adds/removes visits, modifies form fields, configures edit check rules, defines code lists
5. Study Lead configures system connections: EDC system URL and study identifier, LIMS study code, IWRS study ID
6. CDOS validates all system connections
7. Study Lead assigns team members to roles (CRA per site, Data Manager, Medical Monitor)
8. Study Lead activates the study
9. CDOS marks the study as active and begins data ingestion from connected systems

**Postconditions:**
- Study is active and configured in CDOS
- All connected systems are validated
- Team members have appropriate access
- Data ingestion has commenced

**Alternative Flows:**
- **3a.** No suitable template exists: Study Lead creates a study from a blank configuration, manually defining all parameters
- **6a.** System connection validation fails: CDOS displays the specific connection error and blocks study activation until all connections are validated
- **8a.** Missing required configuration: CDOS performs a pre-activation validation check and reports all missing required fields; Study Lead must resolve before activation

---

## UC-007: Perform Risk-Based Monitoring Review

**Actor:** Clinical Research Associate (CRA), Sponsor Monitor  
**Related BR:** BR-013, BR-005  
**Preconditions:**
- Study is active with data flowing from multiple sites
- At least 4 weeks of data are available for trend analysis
- Risk thresholds are configured in CDOS

**Main Flow:**
1. CRA navigates to the Risk-Based Monitoring view for their assigned study
2. CDOS displays a site-level risk heatmap: green (low risk), yellow (watch), red (high risk) based on composite indicators
3. CRA clicks on a yellow/red flagged site
4. CDOS displays detailed risk indicators for the site:
   - Enrollment velocity vs. target
   - Data entry timeliness (days from visit to entry)
   - Query rate per CRF page
   - Protocol deviation count and severity
   - Adverse event reporting rate vs. peer sites
   - Missing/late lab results
5. CRA reviews the indicators, adds monitoring notes, and creates action items
6. CRA generates a monitoring visit report with risk assessment findings
7. CDOS logs the monitoring review with timestamp and CRA identity

**Postconditions:**
- Monitoring review is documented in CDOS
- Action items are tracked with due dates and owners
- Risk indicators are recalculated with latest data on next refresh

**Alternative Flows:**
- **2a.** All sites are green: CDOS displays a summary confirmation and allows CRA to proceed with routine remote monitoring activities
- **3a.** Site has multiple red indicators: CDOS triggers an automatic escalation notification to the Sponsor Study Lead and suggests an on-site monitoring visit
- **5a.** CRA identifies a critical finding: CRA initiates a protocol deviation report and escalates to the Medical Monitor through CDOS workflow

---

## UC-008: Manage Electronic Informed Consent

**Actor:** Subject (via portal/app), Investigator, Coordinator  
**Related BR:** BR-021, BR-010  
**Preconditions:**
- Subject is pre-screened and eligible for the study
- eConsent document version is approved and loaded into CDOS
- Subject has access to the eConsent portal (mobile or web)

**Main Flow:**
1. Coordinator invites the Subject to review the informed consent document via the eConsent portal
2. Subject receives a secure link and authenticates with two-factor authentication
3. Subject reviews the consent document section by section; CDOS tracks which sections have been viewed
4. Subject has the option to highlight sections and submit questions to the study team
5. Subject indicates agreement by applying an electronic signature (e-signature compliant with 21 CFR Part 11)
6. CDOS records the consent with full metadata: Subject ID, document version, timestamp, IP address, device info, signature
7. Investigator counter-signs the consent document
8. CDOS stores the signed consent in the eTMF and flags the Subject as consented

**Postconditions:**
- Signed informed consent is stored with immutable audit trail
- Subject status is updated to "Consented" in the canonical model
- Consent document is filed in the eTMF
- Subject is eligible for screening procedures

**Alternative Flows:**
- **4a.** Subject has questions: Questions are routed to the Coordinator/Investigator; consent is held in "Pending Questions" state until resolved; Subject is notified when answers are available
- **5a.** Subject declines to consent: CDOS records the refusal with timestamp and optional reason; Subject status is set to "Refused Consent"; no further study procedures occur
- **5b.** Consent document is outdated: CDOS detects that a newer version exists and prompts the Subject to review the updated version before signing

---

## UC-009: Generate Regulatory Submission Package

**Actor:** Regulatory Affairs Specialist, Data Manager  
**Related BR:** BR-015, BR-007, BR-008  
**Preconditions:**
- SDTM and ADaM datasets have been generated and approved for the study
- Define-XML metadata is available
- Study documentation (protocol, SAP, CSRs) is available in the eTMF

**Main Flow:**
1. Regulatory Specialist initiates a submission package assembly for a study
2. CDOS presents available datasets (SDTM, ADaM), Define-XML, and associated documents
3. Specialist selects the datasets and documents to include in the submission
4. CDOS assembles the package in eCTD-compatible structure:
   - Module 1: Regional administrative information
   - Module 2: Summaries (CSR, tabulations)
   - Module 3-5: Quality, non-clinical, clinical study reports
5. CDOS generates an XML backbone for the eCTD submission
6. Specialist reviews the package structure, validates document references
7. CDOS performs eCTD technical validation (file specifications, hyperlinks, bookmarks)
8. Specialist exports the package or transmits it to the RegSubmit system (Veeva Vault RIM, Lorenz docuBridge)

**Postconditions:**
- eCTD-compatible submission package is assembled
- Package is validated against eCTD technical specifications
- Package is available for transmission to regulatory authority

**Alternative Flows:**
- **3a.** Required datasets are not yet approved: CDOS blocks assembly and lists the unapproved datasets; Specialist must obtain approval before proceeding
- **7a.** eCTD validation errors: CDOS generates a detailed validation report with error locations and descriptions; Specialist corrects issues and re-validates
- **8a.** Direct submission to health authority: CDOS integrates with the regulatory authority's gateway (e.g., FDA ESG) for electronic submission with delivery confirmation

---

## UC-010: Perform Periodic Access Review

**Actor:** QA Auditor, System Administrator  
**Related BR:** BR-026, BR-019  
**Preconditions:**
- CDOS has been in production for at least one review cycle (typically quarterly)
- User accounts and role assignments are active
- Review schedule is configured in CDOS

**Main Flow:**
1. CDOS triggers a periodic access review on the configured schedule (e.g., quarterly)
2. CDOS generates an access review report listing all active users with:
   - User ID, name, role, assigned studies, assigned sites
   - Last login date, last data access date
   - Training completion status
   - Dormant account flags (no login > 60 days)
3. QA Auditor reviews the report
4. For each user, Auditor marks as: Approved, Revoked, or Needs Review
5. For "Revoked" users, CDOS disables access immediately
6. For "Needs Review" users, CDOS routes to the user's manager for justification
7. CDOS records the access review outcome with auditor identity, timestamp, and decisions
8. CDOS generates a compliance report documenting the review for inspection readiness

**Postconditions:**
- Dormant and over-privileged accounts are remediated
- Access review is documented with full audit trail
- Compliance report is available for regulatory inspection

**Alternative Flows:**
- **1a.** Ad-hoc review triggered: QA Auditor can initiate an off-cycle access review for a specific study or site
- **5a.** User has active data entry in progress: CDOS warns the Auditor and suggests deferring revocation until data entry is complete; Auditor can override with justification
- **6a.** Manager does not respond within SLA: CDOS escalates to the QA Director and flags the account for mandatory review

---

## UC-011: Ingest and Process Wearable/IoT Sensor Data

**Actor:** CDOS Integration Service (automated), Data Manager (configure)  
**Related BR:** BR-005  
**Preconditions:**
- Wearable devices are assigned to Subjects in the study
- Device data streaming endpoint is configured in CDOS
- Data mapping from device measurements to canonical model is defined

**Main Flow:**
1. Wearable device transmits sensor data (heart rate, activity, sleep, etc.) to the CDOS ingestion endpoint
2. CDOS validates the incoming data payload against the expected schema
3. CDOS maps device measurements to the canonical data model (Subject, Visit, measurement type, value, unit, timestamp)
4. CDOS applies configurable aggregation rules (e.g., daily averages, hourly summaries)
5. CDOS detects anomalies based on pre-defined thresholds (e.g., heart rate > 180 bpm)
6. CDOS stores processed data and generates anomaly alerts
7. CDOS makes processed wearable data available in the study dashboard and for SDTM mapping

**Postconditions:**
- Wearable data is available in the canonical model
- Anomaly alerts are visible to the monitoring team
- Data is available for SDTM mapping and analysis

**Alternative Flows:**
- **1a.** Device offline or data delayed: CDOS tracks expected data receipt times and alerts the site if data is missing beyond the configured threshold
- **2a.** Schema validation fails: CDOS quarantines the data payload, logs the error, and notifies the integration team
- **5a.** Anomaly detected: CDOS generates an alert to the Medical Monitor with Subject ID, device type, measurement, and threshold breached

---

## UC-012: Export Study Data for CRO Transition

**Actor:** Sponsor Data Manager  
**Related BR:** BR-022, BR-004  
**Preconditions:**
- Study data exists in CDOS from the current CRO engagement
- Sponsor has authorized the data export
- Export format is specified (CDISC ODM, CSV, JSON)

**Main Flow:**
1. Sponsor Data Manager initiates a data export for a study transitioning from one CRO to another
2. Data Manager selects the export scope: full study data or incremental (since last export)
3. Data Manager selects export formats: CDISC ODM v2.0, SDTM datasets, raw canonical data (JSON)
4. CDOS compiles all study data including:
   - All Subject data (demographics, visits, CRF pages, lab results, adverse events)
   - All metadata (study configuration, edit checks, code lists)
   - Audit trail for all records
   - Document references (eTMF links)
5. CDOS generates export packages with manifest files listing all included data and documents
6. CDOS applies final integrity checks (record counts, checksums)
7. Data Manager downloads or transfers the export packages
8. CDOS logs the export event with full provenance (who, when, what scope, format)

**Postconditions:**
- Complete study data package is available for the new CRO
- Export is logged in the audit trail
- Data integrity checksums are available for verification by the receiving party

**Alternative Flows:**
- **2a.** Partial export requested: CDOS allows filtering by date range, Site, or Subject subset for incremental transfers
- **4a.** Sensitive data redaction required: CDOS applies pseudonymization to Subject identifiers per GDPR/data privacy settings before export
- **6a.** Integrity check failure: CDOS alerts the Data Manager and regenerates the affected export files

---

## Use Case Summary

| UC ID | Title | Primary Actor(s) | Related BR(s) |
|-------|-------|-------------------|----------------|
| UC-001 | Ingest Clinical Data from EDC System | CRA, Integration Service | BR-001 |
| UC-002 | Generate SDTM Datasets for Regulatory Submission | Data Manager, Biostatistician | BR-007, BR-015 |
| UC-003 | Monitor Cross-Study Enrollment Progress | Sponsor Ops Lead, CRO PM | BR-012, BR-014 |
| UC-004 | Resolve Data Clarification Query | Site Coordinator, CRA | BR-017, BR-013 |
| UC-005 | Report and Escalate a Serious Adverse Event | Investigator, Safety Officer | BR-023, BR-004 |
| UC-006 | Configure and Provision a New Study | Study Lead, CRO PM | BR-016, BR-001 |
| UC-007 | Perform Risk-Based Monitoring Review | CRA, Sponsor Monitor | BR-013, BR-005 |
| UC-008 | Manage Electronic Informed Consent | Subject, Investigator | BR-021, BR-010 |
| UC-009 | Generate Regulatory Submission Package | Reg Affairs, Data Manager | BR-015, BR-007, BR-008 |
| UC-010 | Perform Periodic Access Review | QA Auditor, Sys Admin | BR-026, BR-019 |
| UC-011 | Ingest and Process Wearable/IoT Sensor Data | Integration Service, Data Manager | BR-005 |
| UC-012 | Export Study Data for CRO Transition | Sponsor Data Manager | BR-022, BR-004 |
