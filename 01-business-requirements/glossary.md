# CDOS Domain Glossary

This glossary defines domain-specific terms used consistently across all CDOS artifacts. Terms marked with [CANONICAL] match the canonical entity names defined in ALIGNMENT_RULES.md.

---

## Clinical Trial Terminology

| Term | Abbreviation | Definition |
|------|-------------|------------|
| Study | study [CANONICAL] | A clinical trial or clinical investigation conducted to evaluate a medical intervention. Each Study has a unique protocol number and is configured in CDOS with metadata, visit schedules, and data collection parameters. |
| Subject | subj [CANONICAL] | A participant enrolled in a clinical study. Also referred to as a patient or volunteer in external contexts. CDOS uses "Subject" as the canonical term per CDISC conventions. |
| Site | site [CANONICAL] | A clinical investigation site — a physical location (hospital, clinic, research center) where study procedures are performed on Subjects. |
| Investigator | inv [CANONICAL] | A Principal Investigator (PI) or Sub-Investigator (Sub-I) responsible for the conduct of a clinical study at a Site. |
| Visit | visit [CANONICAL] | A scheduled study visit where clinical assessments, sample collection, and data recording occur for a Subject. Visits are defined in the protocol with planned windows. |
| Protocol | proto [CANONICAL] | The study protocol — a document that describes the objectives, design, methodology, statistical considerations, and organization of a clinical trial. |
| AdverseEvent | ae [CANONICAL] | Any untoward medical occurrence in a Subject administered a pharmaceutical product, regardless of causal relationship. Includes Serious Adverse Events (SAEs) and non-serious AEs. |
| LabResult | lab [CANONICAL] | A laboratory test result obtained from biological samples collected during a study visit. Includes hematology, chemistry, urinalysis, and biomarker results. |
| Medication | med [CANONICAL] | A concomitant medication (taken alongside the study drug) or study medication (the investigational product). |
| Dose | dose [CANONICAL] | A single administration of the study drug, including dose amount, route, frequency, and date/time. |
| Query | query [CANONICAL] | A data clarification request generated when a data discrepancy is detected (by edit check or manual review). Queries are resolved by Site staff or Data Managers. |
| CRFPage | crf [CANONICAL] | A Case Report Form page — a structured data collection form for recording study data at a Visit. |
| Sample | sample [CANONICAL] | A biological specimen (blood, urine, tissue) collected during a study visit for laboratory analysis or biobanking. |
| Submission | subm [CANONICAL] | A regulatory submission artifact — a package of data, documents, and metadata assembled for submission to a regulatory authority. |

---

## Regulatory and Compliance Terms

| Term | Abbreviation | Definition |
|------|-------------|------------|
| Good Clinical Practice | GCP | An international ethical and scientific quality standard for designing, conducting, recording, and reporting clinical trials. ICH E6(R2) is the current guideline. |
| 21 CFR Part 11 | — | US FDA regulation establishing criteria under which electronic records and electronic signatures are considered trustworthy, reliable, and equivalent to paper records and handwritten signatures. |
| Computer System Validation | CSV | The documented process of ensuring that a computerized system does exactly what it is designed to do in a consistent and reproducible manner, per GAMP 5 guidelines. |
| Serious Adverse Event | SAE | An AdverseEvent that results in death, is life-threatening, requires hospitalization, results in persistent disability, is a congenital anomaly, or is a medically important event. |
| Suspected Unexpected Serious Adverse Reaction | SUSAR | A serious adverse reaction that is both suspected to be related to the study drug and is not consistent with the current Investigator's Brochure. SUSARs require expedited regulatory reporting. |
| Individual Case Safety Report | ICSR | A standardized report of an individual AdverseEvent case submitted to regulatory authorities for pharmacovigilance purposes. |
| Electronic Common Technical Document | eCTD | The internationally agreed format for submitting regulatory applications electronically to health authorities, structured in five modules. |
| Real-World Data / Evidence | RWD/RWE | RWD: Data relating to patient health status and/or healthcare delivery routinely collected from EHRs, claims, registries, wearables. RWE: Clinical evidence derived from RWD analysis. |
| Electronic Health Record | EHR | A digital version of a patient's medical history maintained by healthcare providers, potentially used as a source of clinical trial data. |
| MedDRA | — | Medical Dictionary for Regulatory Activities — a standardized medical terminology used to classify AdverseEvents in regulatory submissions. |
| CDISC | — | Clinical Data Interchange Standards Consortium — the organization that defines data standards for clinical research (SDTM, ADaM, ODM, CDASH, Define-XML). |

---

## CDISC Data Standards

| Term | Abbreviation | Definition |
|------|-------------|------------|
| Study Data Tabulation Model | SDTM v3.4 | The CDISC standard for organizing and formatting data for regulatory submissions. Defines domain datasets (DM, AE, LB, EX, CM) with standardized variable names and structures. |
| Analysis Data Model | ADaM v2.1 | The CDISC standard for analysis-ready datasets. Defines structures (ADSL, ADAE, ADLB) that support traceability from SDTM to statistical analyses. |
| Operational Data Model | ODM v2.0 | The CDISC standard for exchanging clinical trial data and metadata in XML format. Used for data portability and archival. |
| Clinical Data Acquisition Standards | CDASH v2.1 | The CDISC standard for data collection — defines the most common data elements collected in CRFs with standardized names and definitions. |
| Define-XML | Define-XML v2.1 | A CDISC metadata specification that describes the structure, origin, and controlled terminology of SDTM/ADaM datasets in XML format. |
| SDTM Domain | — | A subject-level dataset in SDTM representing a specific category of data (e.g., DM = Demographics, AE = Adverse Events, LB = Lab Results). Identified by 2-character uppercase codes. |

---

## System and Platform Terms

| Term | Abbreviation | Definition |
|------|-------------|------------|
| Clinical Development Operating System | CDOS | The platform being built — a unified integration layer connecting all clinical research systems (EDC, CTMS, LIMS, Safety, IWRS, eCOA, eTMF, RegSubmit) through a canonical data model. |
| Electronic Data Capture | EDC | A system for collecting clinical trial data electronically via CRFs. Examples: Medidata Rave, Oracle InForm, Veeva Vault CDMS, Castor. |
| Clinical Trial Management System | CTMS | A system for managing the operational aspects of clinical trials — site management, enrollment tracking, monitoring visits, document management. |
| Laboratory Information Management System | LIMS | A system for managing laboratory workflows, sample tracking, test results, and reporting in clinical trials. |
| Electronic Trial Master File | eTMF | A system for managing essential trial documents (protocol, IRB approvals, investigator CVs, regulatory correspondence) in electronic format. |
| Interactive Web Response System | IWRS | A system for randomization and drug supply management in clinical trials. Assigns Subjects to treatment arms and manages drug kit allocation. |
| Electronic Clinical Outcome Assessment | eCOA | A system for collecting patient-reported outcomes (PRO), clinician-reported outcomes (ClinRO), and observer-reported outcomes (ObsRO) electronically. |
| Pharmacovigilance System | Safety | A system for detecting, assessing, understanding, and preventing adverse effects of pharmaceutical products. Examples: Argus Safety, ArisGlobal. |
| Regulatory Submission System | RegSubmit | A system for assembling, managing, and submitting regulatory applications. Examples: Veeva Vault RIM, Lorenz docuBridge. |
| Role-Based Access Control | RBAC | A method of restricting system access based on the roles assigned to individual users, ensuring least-privilege access. |
| Canonical Data Model | — | CDOS's unified internal data model that normalizes data from all source systems into a consistent representation. All adapters transform source data into this model. |

---

## Abbreviations

| Abbreviation | Full Form |
|-------------|-----------|
| BR | Business Requirement |
| FR | Functional Requirement |
| TR | Technical Requirement (Non-Functional Requirement) |
| UC | Use Case |
| TC | Test Case |
| CRA | Clinical Research Associate |
| PI | Principal Investigator |
| SAE | Serious Adverse Event |
| SUSAR | Suspected Unexpected Serious Adverse Reaction |
| PRO | Patient-Reported Outcome |
| GDPR | General Data Protection Regulation |
| HIPAA | Health Insurance Portability and Accountability Act |
| GxP | Good Practice (encompassing GCP, GLP, GMP) |
| PK | Pharmacokinetics |
| IRB | Institutional Review Board |
| IEC | Independent Ethics Committee |
