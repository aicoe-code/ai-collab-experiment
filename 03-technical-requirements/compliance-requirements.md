# CDOS Compliance Requirements

**Document Version:** 1.0
**Author:** Agent-TR
**Last Updated:** 2026-05-29

This document specifies the technical requirements to achieve compliance with
21 CFR Part 11, GDPR, and GxP (GCP, GLP, GMP) regulations applicable to the
CDOS clinical data platform.

---

## 1. 21 CFR Part 11 — Electronic Records; Electronic Signatures

### 1.1 Electronic Records (§11.10)

#### TR-C01: System Validation (§11.10(a))
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS platform SHALL be validated per a documented Computer System Validation (CSV) plan. Validation evidence SHALL include Installation Qualification (IQ), Operational Qualification (OQ), and Performance Qualification (PQ) protocols with documented results. |
| Technical Implementation | Automated regression test suite executed on every release (CI/CD gate). Validation environment (`val`) with locked configuration. Traceability matrix linking requirements to test cases (see `09-sdlc-traceability/`). |
| Acceptance Criteria | 100% of critical and major requirements validated; validation report signed by Quality Assurance |

#### TR-C02: Accurate and Complete Copies (§11.10(b))
| Attribute | Value |
|-----------|-------|
| Requirement | Electronic records SHALL be accurately and completely reproducible as human-readable copies (screen display and printed output). |
| Technical Implementation | PDF export service for all entity records with fields rendered in human-readable format. Print-optimized HTML templates. All timestamps in ISO 8601 format (UTC). |
| Acceptance Criteria | Export any entity to PDF; all fields readable; 100% field parity with on-screen display |

#### TR-C03: Record Retention (§11.10(c))
| Attribute | Value |
|-----------|-------|
| Requirement | Electronic records SHALL be retained for the duration required by applicable regulations (minimum 15 years for clinical trial data, 2 years post-marketing approval). Records SHALL be accessible and readable throughout retention period. |
| Technical Implementation | Object storage lifecycle policy: hot (0-90 days), warm (90-365 days), cold/archive (>365 days). Archive format: Parquet + PDF dual format. Annual integrity verification (checksum validation). |
| Acceptance Criteria | Records retrievable after simulated 15-year archive; checksum integrity verified |

#### TR-C04: Limiting System Access (§11.10(d))
| Attribute | Value |
|-----------|-------|
| Requirement | System access SHALL be limited to authorized individuals. Access controls SHALL enforce role-based permissions at the study, site, and function level. |
| Technical Implementation | RBAC with roles: Study Manager, Data Manager, CRA/Monitor, Investigator, Biostatistician, System Admin, Read-Only. Study-level and site-level data isolation enforced at API gateway and database query layers. MFA required for all user accounts (per TR-015). Session timeout: 15 minutes of inactivity. |
| Acceptance Criteria | Unauthorized access attempt returns 403; session expires after 15 min inactivity; MFA enforced for 100% of users |

#### TR-C05: Audit Trails (§11.10(e))
| Attribute | Value |
|-----------|-------|
| Requirement | Secure, computer-generated, time-stamped audit trails SHALL independently record the date/time of operator entries and actions that create, modify, or delete electronic records. Audit trails SHALL be appended to the record and available for review. |
| Technical Implementation | Append-only `audit_log` table in PostgreSQL (immutable via database-level permissions — no UPDATE/DELETE granted to application role). Audit record fields: `audit_id`, `entity_type`, `entity_id`, `field_name`, `old_value`, `new_value`, `user_id`, `timestamp_utc`, `action_type`, `reason_for_change`, `ip_address`, `user_agent`. Retention: 15 years (same as records). |
| Acceptance Criteria | Every create/update/delete generates audit record; audit records cannot be modified or deleted by any application user; audit trail reviewable via dedicated API endpoint |

#### TR-C06: Operational System Checks (§11.10(f))
| Attribute | Value |
|-----------|-------|
| Requirement | Operational system checks SHALL enforce permitted sequencing of steps and events. |
| Technical Implementation | State machine enforcement on entity workflows (e.g., Subject: SCREENED -> ENROLLED -> COMPLETED/DROPPED). Invalid state transitions rejected with error code. Pre-condition validation on all workflow-triggered API endpoints. |
| Acceptance Criteria | Invalid state transition returns 400 with descriptive error; workflow steps enforced in correct order |

#### TR-C07: Authority Checks (§11.10(g))
| Attribute | Value |
|-----------|-------|
| Requirement | Authority checks SHALL ensure that only authorized individuals can use the system, electronically sign a record, access the operation or device input/output, alter a record, or perform designated operations. |
| Technical Implementation | RBAC policy engine (OPA/Rego) evaluating permissions at API gateway. Permission matrix stored in database with cache (Redis). Permission changes require System Admin role and are audit-logged. |
| Acceptance Criteria | Permission matrix test: each role can only perform permitted actions; unauthorized action returns 403 |

#### TR-C08: Device Checks (§11.10(h))
| Attribute | Value |
|-----------|-------|
| Requirement | Device checks SHALL determine the validity of the source of data input or operational instruction. |
| Technical Implementation | API key validation for system-to-system integrations. Client certificate authentication for EDC, CTMS, LIMS adapters. IP allowlisting for production API access from external systems. |
| Acceptance Criteria | Integration request without valid API key/cert returns 401; IP not on allowlist returns 403 |

#### TR-C09: Training Documentation (§11.10(i))
| Attribute | Value |
|-----------|-------|
| Requirement | Training documentation shall be maintained to ensure individuals are trained before given access to the system. |
| Technical Implementation | User onboarding workflow requires training completion flag before account activation. Training records stored in user profile with completion date and version. System blocks access if training is expired (>12 months). |
| Acceptance Criteria | User account cannot be activated without training flag; expired training blocks access |

#### TR-C10: Written Policies (§11.10(j))
| Attribute | Value |
|-----------|-------|
| Requirement | Written policies shall hold individuals accountable for actions initiated under their electronic signatures. |
| Technical Implementation | Electronic signature acknowledgment screen displayed on first login. Digital acceptance of responsibility policy stored in user profile. Policy version tracked; re-acknowledgment required on policy update. |
| Acceptance Criteria | First login requires policy acceptance; acceptance record stored with timestamp and policy version |

### 1.2 Electronic Signatures (§11.50 - §11.100)

#### TR-C11: Electronic Signature Manifestation (§11.50)
| Attribute | Value |
|-----------|-------|
| Requirement | Electronic signatures SHALL include the printed name of the signer, date/time of signing, and the meaning of the signature (e.g., review, approval, authorship). |
| Technical Implementation | `esignature` table: `esign_id`, `entity_type`, `entity_id`, `user_id`, `signer_name`, `timestamp_utc`, `meaning` (enum: REVIEWED, APPROVED, AUTHORED, ATTESTED), `ip_address`. Signature rendered as banner on record display: "Electronically signed by [Name] on [DateTime] — [Meaning]". |
| Acceptance Criteria | Signature record contains all required fields; signature banner displayed on entity view |

#### TR-C12: Electronic Signature Linking (§11.70)
| Attribute | Value |
|-----------|-------|
| Requirement | Electronic signatures SHALL be linked to their respective electronic records to ensure signatures cannot be excised, copied, or transferred to falsify another electronic record. |
| Technical Implementation | Cryptographic binding: SHA-256 hash of the signed record content stored in `esignature.content_hash`. Any subsequent modification to the record invalidates the signature. Re-signing required after record modification. |
| Acceptance Criteria | Record modification invalidates signature; signature cannot be copied to another record |

#### TR-C13: Electronic Signature Authentication (§11.100)
| Attribute | Value |
|-----------|-------|
| Requirement | Electronic signatures SHALL be unique to one individual and not reused by or reassigned to anyone else. Signatures shall employ at least two distinct identification components (user ID + password, or biometric). |
| Technical Implementation | Two-component signing: user authentication (session token) + re-entry of password at signing time. Optional: MFA challenge at signing. Signature user ID = authenticated user ID (cannot be overridden). |
| Acceptance Criteria | Signing requires password re-entry; signature user ID matches authenticated session; no shared signatures possible |

---

## 2. GDPR — General Data Protection Regulation

#### TR-C14: Lawful Basis and Consent Management
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS platform SHALL record and manage the lawful basis for processing personal data. For consent-based processing, granular consent records SHALL be maintained with withdrawal capability. |
| Technical Implementation | `consent` entity: `consent_id`, `subject_id`, `study_id`, `consent_type`, `version`, `granted_date`, `withdrawn_date`, `lawful_basis`, `purpose`. Consent withdrawal triggers data processing restriction workflow. Consent history immutable (append-only). |
| Acceptance Criteria | Consent record created on enrollment; withdrawal restricts processing within 24 hours; consent history fully auditable |

#### TR-C15: Data Minimization
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS platform SHALL collect and process only the minimum personal data necessary for the defined clinical trial purpose. |
| Technical Implementation | Data collection schema limited to CRF-defined fields. PII fields tagged in data model (`pii: true` metadata). Data exports to analytics exclude PII by default (opt-in required). API responses for non-privileged roles exclude PII fields. |
| Acceptance Criteria | PII field tagging verified across all entities; default exports contain no PII |

#### TR-C16: Right to Erasure and Data Portability (Art. 17, Art. 20)
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS platform SHALL support data subject erasure requests and data portability exports in machine-readable format (JSON/CSV). Exceptions for legal/regulatory retention requirements SHALL be documented. |
| Technical Implementation | Erasure workflow: anonymize PII fields (replace with pseudonymized tokens) while retaining clinical data for regulatory compliance. Portability: export endpoint returning subject's data as JSON or CSV per Art. 20. Anonymization audit-logged with legal basis for partial retention. |
| Acceptance Criteria | Erasure request processed within 30 days; anonymized data non-reversible; portability export available in < 24 hours |

#### TR-C17: Data Protection by Design and Default (Art. 25)
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS platform SHALL implement data protection principles by design and by default, including pseudonymization, encryption, and privacy impact assessments. |
| Technical Implementation | Pseudonymization service: subject identifiers replaced with pseudonymous tokens for analytics pipelines. Field-level encryption on PII (per TR-016). Privacy Impact Assessment (PIA) required before study activation. Default data access = minimum necessary role. |
| Acceptance Criteria | PIA completed for each study; pseudonymization applied to analytics exports; field-level encryption active on all PII fields |

#### TR-C18: Cross-Border Data Transfer (Art. 44-49)
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS platform SHALL enforce data residency requirements. EU subject data SHALL be processed and stored within the EU/EEA unless adequate safeguards (Standard Contractual Clauses, adequacy decision) are documented and active. |
| Technical Implementation | Region-aware data routing: EU data stored in EU-region databases and object stores. Data residency tags on Subject and Site entities. Transfer Impact Assessment (TIA) documented per study region. Geo-fencing enforced at infrastructure level (Terraform region constraints). |
| Acceptance Criteria | EU subject data never stored outside EU-region infrastructure; residency tag present on all Subject entities |

#### TR-C19: Breach Notification (Art. 33-34)
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS platform SHALL detect and log potential data breaches and support notification workflows within 72 hours to supervisory authorities and affected data subjects. |
| Technical Implementation | SIEM integration with automated alerting for: unauthorized data access, bulk data export, anomalous query patterns. Breach incident workflow in CTMS integration: incident creation, impact assessment, notification tracking. Automated logging of all data access for forensic analysis. |
| Acceptance Criteria | Breach detection alert fires within 15 minutes of incident; notification workflow available within 72 hours |

---

## 3. GxP — Good Practice Regulations

### 3.1 Good Clinical Practice (GCP / ICH E6(R3))

#### TR-C20: Data Integrity (ALCOA+ Principles)
| Attribute | Value |
|-----------|-------|
| Requirement | All clinical data managed by CDOS SHALL adhere to ALCOA+ principles: Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, Available. |
| Technical Implementation | **Attributable**: Every record linked to user_id + timestamp. **Legible**: Standardized data formats, no binary opaque fields. **Contemporaneous**: Server-side timestamps (not client-provided). **Original**: First recorded value preserved in audit trail. **Accurate**: Validation rules enforced at API and transform layers. **Complete**: Required fields enforced by schema; missing data flagged. **Consistent**: Canonical entity model across all integrations. **Enduring**: 15-year retention per TR-C03. **Available**: 99.9% uptime per TR-012. |
| Acceptance Criteria | ALCOA+ compliance verified per validation protocol; each principle testable via automated and manual checks |

#### TR-C21: Change Control
| Attribute | Value |
|-----------|-------|
| Requirement | All changes to the validated CDOS system SHALL follow a documented change control process including impact assessment, testing, approval, and deployment verification. |
| Technical Implementation | Git-based version control with branch protection (main branch requires PR + 2 approvals). Automated change impact analysis comparing current vs. proposed validation scope. Change control workflow integrated with CTMS. Post-deployment verification automated in CI/CD pipeline. |
| Acceptance Criteria | Every production change has associated change control record; no direct commits to main branch |

#### TR-C22: Periodic Review
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS system SHALL undergo periodic review (at least annually) to confirm continued validated state and compliance with current regulations. |
| Technical Implementation | Automated validation regression suite scheduled quarterly. Configuration drift detection (Terraform plan in CI). Annual access review workflow (user accounts, roles, permissions). Compliance dashboard showing validation status, open deviations, CAPA items. |
| Acceptance Criteria | Quarterly validation suite passes; annual access review completed; compliance dashboard current |

### 3.2 Data Governance

#### TR-C23: Data Lineage Tracking
| Attribute | Value |
|-----------|-------|
| Requirement | The CDOS platform SHALL maintain end-to-end data lineage from source system ingestion through transformation to regulatory submission format. |
| Technical Implementation | Lineage metadata on every transformed record: `source_system`, `source_record_id`, `transform_id`, `transform_version`, `transform_timestamp`, `target_domain` (SDTM domain code). Lineage graph stored in dedicated `data_lineage` table. Queryable via API for audit and regulatory inspection. |
| Acceptance Criteria | Any SDTM record traceable to source; lineage graph renderable; regulatory inspector can query lineage |

#### TR-C24: Backup and Recovery Validation
| Attribute | Value |
|-----------|-------|
| Requirement | Backup and recovery procedures SHALL be validated and tested at least quarterly. Recovery tests SHALL demonstrate RTO and RPO targets (TR-013) are achievable. |
| Technical Implementation | Automated backup verification (checksum comparison). Quarterly DR drill with documented results. Recovery time measured and reported against RTO target (4 hours). Recovery point measured and reported against RPO target (1 hour). |
| Acceptance Criteria | Quarterly DR drill meets RTO <= 4 hours and RPO <= 1 hour; drill results documented and approved |

---

## Compliance Summary Matrix

| Regulation | Requirement IDs | Key Technical Controls |
|------------|----------------|----------------------|
| 21 CFR Part 11 | TR-C01 through TR-C13 | Audit trail, e-signatures, access control, validation |
| GDPR | TR-C14 through TR-C19 | Consent, encryption, pseudonymization, data residency |
| GxP (GCP) | TR-C20 through TR-C24 | ALCOA+, change control, data lineage, DR validation |
