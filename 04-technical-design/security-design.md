# CDOS — Security Design

## 1. Overview

This document defines the security architecture for CDOS, covering OAuth2/OIDC authentication, field-level encryption, audit trail architecture, and RBAC model. This design satisfies:
- **04-E**: OAuth2/OIDC, field-level encryption, audit trail design

---

## 2. Security Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer 1: Identity & Authentication (Keycloak + OIDC)    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ OAuth2   │  │ OIDC     │  │ MFA      │              │   │
│  │  │ Flows    │  │ Tokens   │  │ (TOTP)   │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer 2: Authorization (RBAC + Policy Engine)           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ Roles    │  │Permissions│  │ Policies │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer 3: Data Protection (Encryption + Masking)         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ Field-   │  │ Transit  │  │ Data     │              │   │
│  │  │ Level    │  │ (mTLS)   │  │ Masking  │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer 4: Audit & Compliance (Immutable Log)             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ Event    │  │ Audit    │  │ 21 CFR   │              │   │
│  │  │ Store    │  │ Trail    │  │ Part 11  │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer 5: Infrastructure Security                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ Network  │  │ Secrets  │  │ Container│              │   │
│  │  │ Policies │  │ (Vault)  │  │ Security │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. OAuth2/OIDC Authentication

### 3.1 Identity Provider

- **Product**: Keycloak 24
- **Protocol**: OpenID Connect (OIDC) 1.0
- **OAuth2 Flows**: Authorization Code + PKCE (web), Client Credentials (service-to-service)

### 3.2 Token Types

| Token | Format | Lifetime | Storage |
|-------|--------|----------|---------|
| Access Token | JWT (RS256) | 15 minutes | Memory (client) |
| Refresh Token | Opaque | 8 hours | HttpOnly cookie |
| ID Token | JWT (RS256) | 15 minutes | Memory (client) |
| Service Token | JWT (RS256) | 1 hour | Environment variable |

### 3.3 JWT Claims

```json
{
  "iss": "https://auth.cdos.io/realms/cdos",
  "sub": "user-6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "aud": "cdos-api",
  "exp": 1622505600,
  "iat": 1622504700,
  "scope": "openid profile email",
  "roles": ["CRA", "DATA_MANAGER"],
  "study_access": ["study-001", "study-002"],
  "site_access": ["site-001", "site-002"],
  "permissions": [
    "subjects:read",
    "subjects:write",
    "adverse_events:read",
    "submissions:read"
  ]
}
```

### 3.4 Authentication Flows

**Web Application (Authorization Code + PKCE):**
```
Browser → Keycloak (authorize) → Auth Code → Browser → API Gateway (token exchange) → JWT
```

**Service-to-Service (Client Credentials):**
```
Service → Keycloak (token) → JWT → API Gateway (validate) → Service
```

**External System Adapter:**
```
Adapter → External System (API Key / OAuth2) → Data → CDOS
```

### 3.5 Multi-Factor Authentication (MFA)

| User Role | MFA Required | Method |
|-----------|-------------|--------|
| Admin | Yes | TOTP (Google Authenticator) |
| Data Manager | Yes | TOTP |
| CRA | Yes | TOTP |
| Read-Only | No | — |
| Service Account | No | Client credentials only |

---

## 4. Role-Based Access Control (RBAC)

### 4.1 Role Hierarchy

```
Admin
  ├── Data Manager
  │     ├── CRA
  │     │     └── Read-Only
  │     └── Medical Monitor
  └── System Admin
        └── Service Account
```

### 4.2 Role Definitions

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| Admin | Full system access | All CRUD, user management, config |
| System Admin | Infrastructure management | Config, monitoring, secrets |
| Data Manager | Data management oversight | All data CRUD, query management, lock/unlock CRFs |
| CRA (Clinical Research Associate) | Site monitoring | Read all data, write monitoring data, raise queries |
| Medical Monitor | Safety oversight | Read all data, flag SAEs/SUSARs, approve safety |
| Read-Only | View access | Read all data, export reports |
| Service Account | System integration | Scoped per service (EDC adapter, LIMS adapter, etc.) |

### 4.3 Permission Matrix

| Resource | Admin | Data Manager | CRA | Medical Monitor | Read-Only |
|----------|-------|-------------|-----|-----------------|-----------|
| Study | CRUD | R | R | R | R |
| Subject | CRUD | CRUD | CRU | R | R |
| Site | CRUD | R | R | R | R |
| Investigator | CRUD | R | R | R | R |
| Visit | CRUD | CRUD | R | R | R |
| AdverseEvent | CRUD | CRUD | CRU | CRUD* | R |
| LabResult | CRUD | CRUD | R | R | R |
| Medication | CRUD | CRUD | R | R | R |
| Dose | CRUD | CRUD | R | R | R |
| Query | CRUD | CRUD | CRU | R | R |
| CRFPage | CRUD | CRUD | R | R | R |
| Sample | CRUD | CRUD | R | R | R |
| Protocol | CRUD | CRU | R | R | R |
| Submission | CRUD | CRU | R | R | R |
| Users | CRUD | — | — | — | — |
| Config | CRUD | — | — | — | — |

*CRUD = Create, Read, Update, Delete; R = Read; CRU = Create, Read, Update*

*Medical Monitor can update AdverseEvent SAE/SUSAR flags only*

### 4.4 Study-Level Access Control

Access is scoped per study. A user with CRA role on Study A cannot access Study B unless explicitly granted.

```json
{
  "user_id": "user-xyz",
  "study_access": [
    {"study_id": "study-001", "role": "CRA", "sites": ["site-001", "site-002"]},
    {"study_id": "study-002", "role": "DATA_MANAGER", "sites": ["*"]}
  ]
}
```

### 4.5 Row-Level Security (PostgreSQL)

```sql
-- Enable RLS on subject table
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;

-- Policy: users can only access subjects in their assigned studies
CREATE POLICY subject_access ON subjects
  USING (study_id IN (
    SELECT study_id FROM user_study_access 
    WHERE user_id = current_setting('app.current_user_id')::uuid
  ));
```

---

## 5. Field-Level Encryption

### 5.1 Encryption Strategy

| Data Category | Fields | Encryption Method | Key |
|--------------|--------|-------------------|-----|
| PII (Subject) | subject_number, demographics (name, DOB, SSN) | AES-256-GCM | Per-study key |
| PHI (Medical) | adverse_event.narrative, lab_result.result_value | AES-256-GCM | Per-study key |
| Credentials | API keys, passwords | AES-256-GCM | Master key (Vault) |
| Audit Logs | user_id, ip_address | AES-256-GCM | System key |

### 5.2 Key Management Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    KEY MANAGEMENT                        │
│                                                          │
│  ┌──────────────────┐     ┌──────────────────────────┐  │
│  │ HashiCorp Vault  │────▶│ Transit Secrets Engine   │  │
│  │ (Key Store)      │     │ (Encryption as Service)  │  │
│  └──────────────────┘     └──────────────────────────┘  │
│           │                        │                     │
│           ▼                        ▼                     │
│  ┌──────────────────┐     ┌──────────────────────────┐  │
│  │ Master Key       │     │ Per-Study Keys           │  │
│  │ (auto-unseal via │     │ (AES-256-GCM)            │  │
│  │  cloud KMS)      │     │ study-001-key            │  │
│  └──────────────────┘     │ study-002-key            │  │
│                           └──────────────────────────┘  │
│                                                          │
│  Key Rotation: Every 90 days                             │
│  Old keys retained for decryption (read-only)            │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Encryption Flow

```
Application → Vault Transit Engine (encrypt) → Ciphertext → PostgreSQL
PostgreSQL → Vault Transit Engine (decrypt) → Plaintext → Application
```

### 5.4 Implementation

```python
class FieldEncryptor:
    """Field-level encryption using Vault Transit Engine."""

    def __init__(self, vault_client: VaultClient, study_id: str):
        self.vault = vault_client
        self.key_name = f"cdos-study-{study_id}"

    def encrypt(self, plaintext: str) -> str:
        """Encrypt field value. Returns base64 ciphertext."""
        response = self.vault.transit.encrypt(
            name=self.key_name,
            plaintext=base64.b64encode(plaintext.encode()).decode()
        )
        return response["data"]["ciphertext"]

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt field value. Returns plaintext."""
        response = self.vault.transit.decrypt(
            name=self.key_name,
            ciphertext=ciphertext
        )
        return base64.b64decode(response["data"]["plaintext"]).decode()
```

### 5.5 Encrypted Column Storage

```sql
CREATE TABLE subjects (
    subject_id UUID PRIMARY KEY,
    study_id UUID NOT NULL,
    subject_number_encrypted BYTEA NOT NULL,  -- AES-256-GCM ciphertext
    subject_number_hash VARCHAR(64) NOT NULL,  -- SHA-256 for lookups
    demographics_encrypted BYTEA,              -- Encrypted JSON
    status VARCHAR(20) NOT NULL,               -- Not encrypted (filterable)
    enrolled_date DATE,                        -- Not encrypted (filterable)
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Index on hash for lookups without decryption
CREATE INDEX idx_subject_number_hash ON subjects(subject_number_hash);
```

---

## 6. Audit Trail Architecture

### 6.1 21 CFR Part 11 Compliance

| Requirement | Implementation |
|-------------|----------------|
| System-generated audit trail | All state changes emit audit events |
| Audit trail cannot be modified | Append-only Kafka topic (cdos.audit.user.action) |
| Audit trail includes who, what, when | Event metadata: user_id, action, timestamp |
| Electronic signatures | Signing ceremony with user authentication |
| Record retention | 7+ years in immutable storage |

### 6.2 Audit Event Structure

```json
{
  "audit_id": "audit-6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "timestamp": "2026-05-29T10:30:00Z",
  "user_id": "user-xyz",
  "user_name": "john.doe@cro.com",
  "user_role": "CRA",
  "action": "UPDATE",
  "resource_type": "Subject",
  "resource_id": "subject-001",
  "study_id": "study-001",
  "ip_address": "10.0.1.50",
  "user_agent": "Mozilla/5.0...",
  "session_id": "sess-abc",
  "changes": {
    "before": {"status": "SCREENED"},
    "after": {"status": "ENROLLED"}
  },
  "reason": "Subject met eligibility criteria",
  "request_id": "req-abc123"
}
```

### 6.3 Audit Storage Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIT TRAIL ARCHITECTURE                      │
│                                                                  │
│  ┌──────────┐     ┌──────────────────┐     ┌──────────────────┐│
│  │ API      │────▶│ Kafka Topic      │────▶│ Audit Consumer   ││
│  │ Gateway  │     │ cdos.audit.*     │     │ (2 instances)    ││
│  └──────────┘     └──────────────────┘     └────────┬─────────┘│
│                                                      │          │
│                      ┌───────────────────────────────┼──────┐   │
│                      │                               │      │   │
│                      ▼                               ▼      │   │
│              ┌──────────────┐              ┌──────────────┐ │   │
│              │ PostgreSQL   │              │ S3/WORM      │ │   │
│              │ audit_events │              │ (Immutable)  │ │   │
│              │ (90 days)    │              │ (7 years)    │ │   │
│              └──────────────┘              └──────────────┘ │   │
│                                                              │   │
│  WORM = Write Once Read Many (cannot be modified/deleted)    │   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.4 Audit Event Types

| Event Type | Description | Retention |
|-----------|-------------|-----------|
| USER_LOGIN | User authentication | 7 years |
| USER_LOGOUT | User session end | 7 years |
| CREATE | Entity creation | 7 years |
| READ | Data access (sensitive fields) | 7 years |
| UPDATE | Entity modification | 7 years |
| DELETE | Soft delete | 7 years |
| EXPORT | Data export | 7 years |
| SIGN | Electronic signature | 7 years |
| SYSTEM | System events (transform, pipeline) | 7 years |
| SECURITY | Security events (failed auth, permission denied) | 7 years |

### 6.5 Electronic Signatures

```python
class ElectronicSignature:
    """
    21 CFR Part 11 compliant electronic signature.
    """

    async def sign(self, user_id: str, resource_type: str, 
                   resource_id: str, meaning: str, 
                   credentials: UserCredentials) -> SignatureRecord:
        """
        1. Re-authenticate user (username + password + MFA)
        2. Record signature meaning (e.g., "I approve this CRF page")
        3. Generate signature record
        4. Emit SIGN audit event
        5. Store signature in signatures table
        """
        ...
```

---

## 7. Transport Security

### 7.1 mTLS Between Services

All internal service-to-service communication uses mutual TLS:

```
Service A ──mTLS──▶ Service B
  Certificate:       Certificate:
  svc-a.cdos.io      svc-b.cdos.io
  Signed by:         Signed by:
  CDOS Internal CA   CDOS Internal CA
```

### 7.2 External TLS

- All external endpoints served via TLS 1.3
- Certificate management via cert-manager (Let's Encrypt)
- HSTS enabled with 1-year max-age

---

## 8. Network Security

### 8.1 Network Policies (Kubernetes)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-gateway-policy
spec:
  podSelector:
    matchLabels:
      app: api-gateway
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: study-service
        - podSelector:
            matchLabels:
              app: subject-service
      ports:
        - port: 8000
    - to:
        - podSelector:
            matchLabels:
              app: kafka
      ports:
        - port: 9092
```

### 8.2 Secrets Management

- All secrets stored in HashiCorp Vault
- Kubernetes secrets synced via External Secrets Operator
- No secrets in environment variables or config files
- Secret rotation automated via Vault policies

---

## 9. Security Monitoring

### 9.1 Security Events

| Event | Severity | Response |
|-------|----------|----------|
| Failed login (3+ attempts) | HIGH | Account lockout, alert |
| Permission denied | MEDIUM | Log, review |
| Unusual data access pattern | HIGH | Alert security team |
| Token theft detected | CRITICAL | Revoke all tokens, alert |
| Encryption key access | HIGH | Log, alert |

### 9.2 Security Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Failed login rate | <1% | >5% in 5 minutes |
| Permission denied rate | <0.1% | >1% in 5 minutes |
| Token refresh failures | <0.01% | >0.1% in 5 minutes |
| Encryption operation latency | <10ms p99 | >50ms p99 |
