# Security and Encryption

## Overview

This document defines the security architecture and encryption standards
for the CDOS platform. All clinical data — at rest, in transit, and at
the field level — must be protected against unauthorized access, disclosure,
modification, and destruction. These controls satisfy the security
requirements of 21 CFR Part 11, GDPR Article 32, and ICH E6(R2).

---

## 1. Encryption at Rest

### Requirement

All data stored on disk (databases, file systems, backups, logs) must be
encrypted using AES-256 or equivalent.

### Specification

| Control | Specification | Systems Affected |
|---------|--------------|-----------------|
| Algorithm | AES-256 (FIPS 197 compliant) | All [System:*] |
| Database encryption | Transparent Data Encryption (TDE) enabled on all database instances | All [System:*] |
| File storage encryption | Volume-level encryption (LUKS for Linux, BitLocker for Windows, APFS encryption for macOS) | All [System:*] |
| Backup encryption | All backups encrypted with AES-256 before storage; backup encryption key distinct from database encryption key | All [System:*] |
| Log encryption | Audit trail logs encrypted at rest; log storage is append-only and tamper-evident | [System:EDC], [System:Safety], [System:CTMS] |

### Per-System Encryption Requirements

| System | Database TDE | File Encryption | Backup Encryption | Log Encryption |
|--------|-------------|----------------|-------------------|---------------|
| [System:EDC] | Required | Required (CRF attachments) | Required | Required |
| [System:CTMS] | Required | Required (documents) | Required | Required |
| [System:LIMS] | Required | Required (lab instrument files) | Required | Required |
| [System:Safety] | Required | Required (safety documents) | Required | Required |
| [System:IWRS] | Required | Required (randomization lists) | Required | Required |
| [System:eCOA] | Required | Required (ePRO data) | Required | Required |
| [System:eTMF] | Required | Required (all documents) | Required | Required |
| [System:Imaging] | Required | Required (DICOM files) | Required | Required |
| [System:Wearables] | Required | Required (raw sensor data) | Required | Required |
| [System:RegSubmit] | Required | Required (eCTD submissions) | Required | Required |

---

## 2. Encryption in Transit

### Requirement

All data transmitted between systems, between client and server, and
across network boundaries must be encrypted using TLS 1.3 or equivalent.

### Specification

| Control | Specification |
|---------|--------------|
| Protocol | TLS 1.3 (RFC 8446) — TLS 1.2 permitted only for legacy vendor connections with documented exception |
| Cipher suites | TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256 (TLS 1.3); ECDHE key exchange only for TLS 1.2 |
| Certificate management | X.509 v3 certificates from a trusted CA; automated rotation 30 days before expiry |
| Certificate pinning | Public key pinning for inter-service communication within the CDOS platform |
| Mutual TLS (mTLS) | Required for all system-to-system API calls (see [System:*] adapter contracts in 04-integrations/) |
| Minimum key size | RSA-2048 minimum; RSA-4096 or ECDSA P-256 preferred |

### Network Segmentation

| Zone | Systems | Access Policy |
|------|---------|--------------|
| DMZ | API gateway, load balancer | Inbound HTTPS only from approved networks |
| Application zone | [System:EDC], [System:CTMS], [System:LIMS], [System:Safety], [System:IWRS], [System:eCOA], [System:eTMF], [System:RegSubmit] | Inbound from DMZ only; mTLS required |
| Data zone | Database servers, encryption key stores | Inbound from application zone only; no direct external access |
| IoT zone | [System:Wearables] device endpoints | Outbound to application zone only; device certificates required |

### Per-System Transit Encryption

| System | TLS Version | mTLS Required | Protocol |
|--------|------------|--------------|----------|
| [System:EDC] | TLS 1.3 | Yes | HTTPS REST API |
| [System:CTMS] | TLS 1.3 | Yes | HTTPS REST API |
| [System:LIMS] | TLS 1.3 | Yes | HTTPS REST API + HL7 FHIR |
| [System:Safety] | TLS 1.3 | Yes | HTTPS REST API |
| [System:IWRS] | TLS 1.3 | Yes | HTTPS REST API |
| [System:eCOA] | TLS 1.3 | Yes | HTTPS REST API |
| [System:eTMF] | TLS 1.3 | Yes | HTTPS REST API |
| [System:Imaging] | TLS 1.3 | Yes | DICOM TLS + HTTPS REST API |
| [System:Wearables] | TLS 1.3 | Device certs | HTTPS + MQTT over TLS |
| [System:RegSubmit] | TLS 1.3 | Yes | HTTPS REST API + AS2 |

---

## 3. Field-Level Encryption

### Requirement

Certain high-sensitivity fields require encryption at the application
layer, independent of database-level encryption. This provides defense-in-depth
and protects against database administrator access to PII.

### Sensitive Fields

| Entity | Field | Encryption | Rationale |
|--------|-------|-----------|-----------|
| [Entity:Subject] | `subject_name` | AES-256-GCM | Direct identifier (PII) |
| [Entity:Subject] | `date_of_birth` | AES-256-GCM | Direct identifier (PII) |
| [Entity:Subject] | `medical_record_number` | AES-256-GCM | Direct identifier (PII) |
| [Entity:Subject] | `national_id` | AES-256-GCM | Direct identifier (PII) |
| [Entity:Subject] | `genetic_markers` | AES-256-GCM | Special category (GDPR Art. 9) |
| [Entity:Investigator] | `license_number` | AES-256-GCM | Professional identifier |
| [Entity:Investigator] | `national_provider_id` | AES-256-GCM | Professional identifier |
| [Entity:Sample] | `barcode` | AES-256-GCM | Links to subject identity |
| [Entity:AdverseEvent] | `narrative` | AES-256-GCM | May contain unstructured PII |

### Encryption Specification

```
ALGORITHM: AES-256-GCM (authenticated encryption)
IV: 96-bit random IV per field encryption operation (never reused)
TAG: 128-bit authentication tag (tamper detection)
KEY_DERIVATION: HKDF-SHA256(master_key, context)
CONTEXT_STRING: "cdos-field-enc-{entity}-{field}-{study_id}"

ENCRYPTED_FIELD_FORMAT:
{
  "algorithm": "AES-256-GCM",
  "iv": "<base64>",
  "tag": "<base64>",
  "ciphertext": "<base64>"
}
```

### Implementation Rules

- Field-level encryption is applied at the application layer before data
  reaches the database.
- Decryption requires the appropriate field-encryption key; database
  administrators cannot read encrypted fields without application-layer access.
- Encrypted fields are stored as JSON objects with algorithm, IV, tag, and
  ciphertext — enabling algorithm agility.
- Key rotation for field-level encryption follows the key management
  schedule (see §4).

---

## 4. Key Management

### Requirement

Encryption keys must be managed through their entire lifecycle — generation,
distribution, storage, rotation, and destruction — using a Hardware Security
Module (HSM) or equivalent key management service (KMS).

### Key Hierarchy

```
Level 1: Root Key (Master Key)
  ├── Stored in HSM (FIPS 140-2 Level 3 minimum)
  ├── Never exported from HSM in plaintext
  └── Recovery: 2-of-3 split-key ceremony (see §4.2)

Level 2: Key Encryption Keys (KEKs)
  ├── One per region/datacenter
  ├── Encrypt Level 3 keys at rest
  └── Rotation: Annually

Level 3: Data Encryption Keys (DEKs)
  ├── One per system per study
  ├── Encrypt application data (field-level, database TDE)
  ├── Rotation: Every 2 years or upon suspected compromise
  └── Revocation: Immediate upon compromise detection

Level 4: Session Keys (TLS)
  ├── Ephemeral, per-connection
  ├── Derived via TLS 1.3 handshake (ECDHE)
  └── Not stored; destroyed on session close
```

### 4.1 Key Generation

| Control | Specification |
|---------|--------------|
| Entropy source | CSPRNG (Cryptographically Secure Pseudo-Random Number Generator) seeded from HSM entropy |
| Key strength | AES-256 keys: 256 bits; RSA keys: 4096 bits; ECDSA keys: P-256 or P-384 |
| Generation ceremony | Root key generated during a documented ceremony with 3 authorized custodians present |
| Documentation | Key generation event logged with date, time, custodians, algorithm, key ID |

### 4.2 Key Custody (2-Person Rule)

| Key Level | Custodian Roles | Minimum Custodians |
|-----------|----------------|-------------------|
| Root Key | Chief Information Security Officer (CISO), Head of QA, IT Director | 2-of-3 for any operation |
| KEK | Security Engineer, QA Lead | 2-of-2 for any operation |
| DEK | Automated via KMS; human intervention only for rotation or revocation | 1 (automated) |

### 4.3 Key Rotation Schedule

| Key Type | Rotation Frequency | Trigger for Emergency Rotation |
|---------|-------------------|-------------------------------|
| Root Key | Every 5 years | HSM compromise, custodian departure |
| KEK | Annually | Suspected KEK compromise |
| DEK | Every 2 years | Suspected DEK compromise, personnel change with access |
| TLS certificates | Annually (30 days before expiry) | Certificate compromise, CA revocation |
| API keys / secrets | Every 90 days | Suspected exposure, employee offboarding |

### 4.4 Key Destruction

- Keys scheduled for rotation are retained in a "retired" state for
  1 year to support decryption of historical data.
- After the retention period, keys are cryptographically erased from the HSM.
- Destruction is documented with date, time, approving authority, and
  confirmation that no data still requires the key.

---

## 5. Role-Based Access Control (RBAC) Model

### Requirement

All system access must be governed by a role-based access control model
that enforces the principle of least privilege.

### Global Roles

| Role ID | Role Name | Description | Systems | Permissions |
|---------|-----------|------------|---------|-------------|
| R001 | System Administrator | Platform infrastructure and user provisioning | All [System:*] | User CRUD, config, no data access |
| R002 | Data Entry | Site-level CRF data entry | [System:EDC], [System:eCOA] | CREATE, READ (own site) |
| R003 | CRA / Monitor | Clinical monitoring and data verification | [System:EDC], [System:CTMS] | READ (assigned sites), CREATE queries |
| R004 | Data Manager | Central data management and query resolution | [System:EDC], [System:CTMS], [System:LIMS] | CREATE, READ, UPDATE, close queries |
| R005 | Medical Monitor | Safety oversight and medical assessment | [System:Safety], [System:EDC] | READ, assess, approve safety records |
| R006 | Biostatistician | Statistical analysis and data extraction | [System:EDC] | READ (blinded/unblinded per assignment) |
| R007 | Lab Director | Laboratory operations oversight | [System:LIMS] | READ, approve, configure lab panels |
| R008 | Pharmacovigilance | Safety case processing and reporting | [System:Safety] | CREATE, READ, UPDATE safety cases |
| R009 | Regulatory Affairs | Submission preparation and tracking | [System:RegSubmit], [System:eTMF] | CREATE, READ, UPDATE submissions |
| R010 | Quality Assurance | Validation oversight and audit | All [System:*] | READ-only to all data + audit trails |
| R011 | Sponsor Executive | Study-level dashboard access | [System:CTMS] | READ aggregated metrics only |
| R012 | Key Custodian | Encryption key management | KMS only | Key generation, rotation, destruction |

### Permission Matrix

| Permission | R001 | R002 | R003 | R004 | R005 | R006 | R007 | R008 | R009 | R010 | R011 | R012 |
|-----------|------|------|------|------|------|------|------|------|------|------|------|------|
| User management | ✓ | — | — | — | — | — | — | — | — | — | — | — |
| System config | ✓ | — | — | — | — | — | — | — | — | — | — | — |
| CRF data entry | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — |
| Query issuance | — | — | ✓ | ✓ | — | — | — | — | — | — | — | — |
| Query resolution | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — |
| Safety assessment | — | — | — | — | ✓ | — | — | ✓ | — | — | — | — |
| Data extraction | — | — | — | — | — | ✓ | — | — | — | — | — | — |
| Lab result approval | — | — | — | — | — | — | ✓ | — | — | — | — | — |
| Submission management | — | — | — | — | — | — | — | — | ✓ | — | — | — |
| Audit trail read | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Dashboard read | — | — | — | — | — | — | — | — | — | — | ✓ | — |
| Key operations | — | — | — | — | — | — | — | — | — | — | — | ✓ |

### Access Control Enforcement

| Control | Specification | Systems |
|---------|--------------|---------|
| Study-level isolation | Users can only access data for [Entity:Study] records they are assigned to | [System:EDC], [System:CTMS], [System:Safety] |
| Site-level isolation | Site staff can only access data for their [Entity:Site] | [System:EDC], [System:eCOA] |
| Blinding enforcement | Blinded [Entity:Subject] treatment data hidden from blinded roles | [System:EDC], [System:IWRS] |
| Temporal access | Access granted for study duration; auto-revoked upon study close or user offboarding | All [System:*] |
| Privileged access review | Quarterly review of all R001 (System Admin) and R012 (Key Custodian) accounts | All [System:*], KMS |

---

## 6. Security Monitoring and Incident Response

### Monitoring Requirements

| Control | Specification |
|---------|--------------|
| Intrusion detection | Network-based IDS/IPS at all zone boundaries |
| Log aggregation | All system logs, audit trails, and security events centralized in SIEM |
| Anomaly detection | Baseline normal access patterns; alert on deviation (unusual time, volume, location) |
| Failed authentication | Alert after 3 failed login attempts from same source within 10 minutes |
| Privilege escalation | Alert on any unauthorized role assignment or permission elevation |
| Data exfiltration | Alert on bulk data exports exceeding study-specific thresholds |

### Incident Response

| Phase | Actions | SLA |
|-------|---------|-----|
| Detection | SIEM alert triaged by Security Operations Center | < 15 minutes |
| Containment | Isolate affected system(s); revoke compromised credentials | < 1 hour |
| Investigation | Root cause analysis; determine scope of breach | < 24 hours |
| Notification | GDPR Art. 33: notify supervisory authority within 72 hours if personal data breach | < 72 hours |
| Remediation | Patch vulnerability, rotate keys, update controls | < 7 days |
| Post-incident | Lessons learned report; update SOPs and training | < 30 days |

---

## Cross-Reference Map

| Security Control | Systems | Entities |
|-----------------|---------|----------|
| Encryption at rest | All [System:*] | All [Entity:*] |
| Encryption in transit | All [System:*] | All [Entity:*] |
| Field-level encryption | [System:EDC], [System:CTMS], [System:LIMS], [System:Safety] | [Entity:Subject], [Entity:Investigator], [Entity:Sample], [Entity:AdverseEvent] |
| Key management | KMS (all [System:*]) | — |
| RBAC | All [System:*] | All [Entity:*] |
| Security monitoring | All [System:*] | All [Entity:*] |
