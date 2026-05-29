# CDOS — API Design

## 1. Overview

This document defines the API design for CDOS, covering RESTful resource naming (FastAPI), event topology (Kafka topics), and error modeling (RFC 9457). This design satisfies:
- **04-D**: REST + event-driven design, resource naming, event topology, error model

---

## 2. REST API Design (FastAPI)

### 2.1 Base URL

```
https://api.cdos.io/v1
```

### 2.2 Resource Naming Convention

All resources follow REST conventions:
- Plural nouns for collections
- Nested resources for relationships
- UUID path parameters
- Query parameters for filtering/pagination

### 2.3 Resource Hierarchy

```
/v1
├── /studies
│   ├── /{study_id}
│   │   ├── /subjects
│   │   │   └── /{subject_id}
│   │   │       ├── /adverse-events
│   │   │       │   └── /{adverse_event_id}
│   │   │       ├── /lab-results
│   │   │       │   └── /{lab_result_id}
│   │   │       ├── /medications
│   │   │       │   └── /{medication_id}
│   │   │       ├── /doses
│   │   │       │   └── /{dose_id}
│   │   │       ├── /crf-pages
│   │   │       │   └── /{crf_page_id}
│   │   │       │       └── /queries
│   │   │       │           └── /{query_id}
│   │   │       ├── /samples
│   │   │       │   └── /{sample_id}
│   │   │       └── /visits
│   │   │           └── /{visit_id}
│   │   ├── /sites
│   │   │   └── /{site_id}
│   │   │       └── /investigators
│   │   │           └── /{investigator_id}
│   │   ├── /protocols
│   │   │   └── /{protocol_id}
│   │   ├── /submissions
│   │   │   └── /{submission_id}
│   │   ├── /transform
│   │   └── /pipeline
```

### 2.4 Endpoint Catalog

#### Studies

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies | createStudy | Create a new study |
| GET | /studies | listStudies | List all studies (paginated) |
| GET | /studies/{study_id} | getStudy | Get study details |
| PATCH | /studies/{study_id} | updateStudy | Update study metadata |
| DELETE | /studies/{study_id} | deleteStudy | Soft-delete a study |

#### Subjects

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/subjects | createSubject | Enroll a subject |
| GET | /studies/{study_id}/subjects | listSubjects | List subjects by study |
| GET | /studies/{study_id}/subjects/{subject_id} | getSubject | Get subject details |
| PATCH | /studies/{study_id}/subjects/{subject_id} | updateSubject | Update subject |
| GET | /studies/{study_id}/subjects/{subject_id}/visits | listVisits | List visits |

#### Adverse Events

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/subjects/{subject_id}/adverse-events | createAdverseEvent | Report an AE |
| GET | /studies/{study_id}/subjects/{subject_id}/adverse-events | listAdverseEvents | List AEs |
| GET | /studies/{study_id}/subjects/{subject_id}/adverse-events/{ae_id} | getAdverseEvent | Get AE details |
| PATCH | /studies/{study_id}/subjects/{subject_id}/adverse-events/{ae_id} | updateAdverseEvent | Update AE |

#### Lab Results

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/subjects/{subject_id}/lab-results | createLabResult | Record lab result |
| GET | /studies/{study_id}/subjects/{subject_id}/lab-results | listLabResults | List lab results |
| GET | /studies/{study_id}/subjects/{subject_id}/lab-results/{lab_result_id} | getLabResult | Get lab result |

#### Medications

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/subjects/{subject_id}/medications | createMedication | Record medication |
| GET | /studies/{study_id}/subjects/{subject_id}/medications | listMedications | List medications |
| GET | /studies/{study_id}/subjects/{subject_id}/medications/{medication_id} | getMedication | Get medication |

#### Doses

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/subjects/{subject_id}/doses | createDose | Record dose |
| GET | /studies/{study_id}/subjects/{subject_id}/doses | listDoses | List doses |
| GET | /studies/{study_id}/subjects/{subject_id}/doses/{dose_id} | getDose | Get dose details |

#### CRF Pages & Queries

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/subjects/{subject_id}/crf-pages | createCRFPage | Submit CRF page |
| GET | /studies/{study_id}/subjects/{subject_id}/crf-pages | listCRFPages | List CRF pages |
| GET | /studies/{study_id}/subjects/{subject_id}/crf-pages/{crf_page_id} | getCRFPage | Get CRF page |
| POST | .../crf-pages/{crf_page_id}/queries | createQuery | Raise a query |
| GET | .../crf-pages/{crf_page_id}/queries | listQueries | List queries |
| PATCH | .../queries/{query_id} | updateQuery | Respond/close query |

#### Sites & Investigators

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/sites | createSite | Add site to study |
| GET | /studies/{study_id}/sites | listSites | List sites |
| GET | /studies/{study_id}/sites/{site_id} | getSite | Get site details |
| POST | /studies/{study_id}/sites/{site_id}/investigators | createInvestigator | Add investigator |
| GET | /studies/{study_id}/sites/{site_id}/investigators | listInvestigators | List investigators |

#### Protocols

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/protocols | createProtocol | Create protocol version |
| GET | /studies/{study_id}/protocols | listProtocols | List protocol versions |
| GET | /studies/{study_id}/protocols/{protocol_id} | getProtocol | Get protocol details |

#### Samples

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/subjects/{subject_id}/samples | createSample | Register sample |
| GET | /studies/{study_id}/subjects/{subject_id}/samples | listSamples | List samples |
| GET | /studies/{study_id}/subjects/{subject_id}/samples/{sample_id} | getSample | Get sample |

#### Submissions

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/submissions | createSubmission | Create submission |
| GET | /studies/{study_id}/submissions | listSubmissions | List submissions |
| GET | /studies/{study_id}/submissions/{submission_id} | getSubmission | Get submission status |
| POST | /studies/{study_id}/submissions/{submission_id}/submit | submitSubmission | Submit to agency |

#### Pipeline Operations

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | /studies/{study_id}/transform | triggerTransform | Trigger transformation pipeline |
| GET | /studies/{study_id}/pipeline/status | getPipelineStatus | Get pipeline execution status |

### 2.5 Pagination

```
GET /studies?offset=0&limit=20&sort=created_at&order=desc

Response:
{
  "data": [...],
  "pagination": {
    "total": 150,
    "offset": 0,
    "limit": 20,
    "has_next": true,
    "has_prev": false
  }
}
```

### 2.6 Filtering

```
GET /studies/{study_id}/subjects?status=ENROLLED&site_id={site_id}
GET /studies/{study_id}/subjects/{subject_id}/adverse-events?is_sae=true&severity=SEVERE
GET /studies/{study_id}/subjects/{subject_id}/lab-results?abnormal_flag=ABNORMAL_HIGH
```

### 2.7 Request/Response Example

**POST /studies/{study_id}/subjects**

Request:
```json
{
  "subject_number": "001-001",
  "site_id": "550e8400-e29b-41d4-a716-446655440000",
  "demographics": {
    "age": 45,
    "sex": "F",
    "race": "WHITE",
    "ethnicity": "NOT_HISPANIC"
  }
}
```

Response (201 Created):
```json
{
  "data": {
    "subject_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "study_id": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    "site_id": "550e8400-e29b-41d4-a716-446655440000",
    "subject_number": "001-001",
    "status": "SCREENED",
    "demographics": {
      "age": 45,
      "sex": "F",
      "race": "WHITE",
      "ethnicity": "NOT_HISPANIC"
    },
    "created_at": "2026-05-29T10:30:00Z",
    "updated_at": "2026-05-29T10:30:00Z"
  },
  "links": {
    "self": "/v1/studies/6ba7b811-9dad-11d1-80b4-00c04fd430c8/subjects/6ba7b810-9dad-11d1-80b4-00c04fd430c8"
  }
}
```

---

## 3. Error Model (RFC 9457)

### 3.1 Problem Details Format

All errors use RFC 9457 Problem Details:

```json
{
  "type": "https://api.cdos.io/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Subject subject_number is required",
  "instance": "/v1/studies/{study_id}/subjects",
  "errors": [
    {
      "pointer": "/subject_number",
      "code": "REQUIRED",
      "message": "subject_number is required"
    }
  ],
  "trace_id": "abc123-def456"
}
```

### 3.2 Error Types

| HTTP Status | Type URI | Title | When Used |
|------------|----------|-------|-----------|
| 400 | /errors/bad-request | Bad Request | Malformed request body |
| 401 | /errors/unauthorized | Unauthorized | Missing or invalid token |
| 403 | /errors/forbidden | Forbidden | Insufficient permissions |
| 404 | /errors/not-found | Not Found | Resource doesn't exist |
| 409 | /errors/conflict | Conflict | Duplicate or state conflict |
| 422 | /errors/validation-error | Validation Error | Business rule violation |
| 429 | /errors/rate-limited | Rate Limited | Too many requests |
| 500 | /errors/internal-error | Internal Server Error | Unexpected server error |
| 502 | /errors/bad-gateway | Bad Gateway | External system failure |
| 503 | /errors/service-unavailable | Service Unavailable | System overload |

### 3.3 Validation Error Response

```json
{
  "type": "https://api.cdos.io/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request body contains 2 validation errors",
  "instance": "/v1/studies/{study_id}/subjects",
  "errors": [
    {
      "pointer": "/subject_number",
      "code": "REQUIRED",
      "message": "subject_number is required"
    },
    {
      "pointer": "/demographics/age",
      "code": "INVALID_TYPE",
      "message": "Expected integer, got string"
    }
  ],
  "trace_id": "abc123-def456"
}
```

---

## 4. Event Topology (Kafka)

### 4.1 Topic Naming Convention

```
cdos.{domain}.{entity}.{event_type}
```

### 4.2 Topic Catalog

| Topic | Partitions | Retention | Description |
|-------|-----------|-----------|-------------|
| cdos.study.study.created | 3 | 365 days | Study created |
| cdos.study.study.updated | 3 | 365 days | Study updated |
| cdos.study.study.deleted | 3 | 365 days | Study soft-deleted |
| cdos.clinical.subject.enrolled | 6 | 365 days | Subject enrolled |
| cdos.clinical.subject.withdrawn | 6 | 365 days | Subject withdrawn |
| cdos.clinical.adverse_event.reported | 6 | 365 days | AE reported |
| cdos.clinical.adverse_event.sae_flagged | 6 | 365 days | SAE flagged |
| cdos.clinical.lab_result.received | 6 | 365 days | Lab result received |
| cdos.clinical.dose.administered | 6 | 365 days | Dose administered |
| cdos.clinical.medication.recorded | 6 | 365 days | Medication recorded |
| cdos.clinical.crf_page.submitted | 6 | 365 days | CRF page submitted |
| cdos.clinical.query.raised | 3 | 365 days | Query raised |
| cdos.clinical.query.responded | 3 | 365 days | Query responded |
| cdos.clinical.query.closed | 3 | 365 days | Query closed |
| cdos.clinical.sample.collected | 3 | 365 days | Sample collected |
| cdos.pipeline.raw.ingested | 12 | 90 days | Raw data ingested |
| cdos.pipeline.raw.failed | 12 | 90 days | Raw ingest failed |
| cdos.pipeline.canonical.created | 12 | 90 days | Canonical entity created |
| cdos.pipeline.canonical.updated | 12 | 90 days | Canonical entity updated |
| cdos.pipeline.sdtm.mapped | 6 | 90 days | SDTM mapping complete |
| cdos.pipeline.adam.mapped | 6 | 90 days | ADaM mapping complete |
| cdos.pipeline.submission.ready | 3 | 365 days | Submission packaged |
| cdos.pipeline.submission.submitted | 3 | 365 days | Submission sent to agency |
| cdos.audit.user.action | 3 | 7 years | User action audit (21 CFR 11) |

### 4.3 Event Schema Example

**subject.enrolled event:**

```json
{
  "event_id": "evt-6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "event_type": "cdos.clinical.subject.enrolled",
  "event_version": "1.0.0",
  "timestamp": "2026-05-29T10:30:00Z",
  "source": "cdos-api-gateway",
  "correlation_id": "req-abc123",
  "data": {
    "subject_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "study_id": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    "site_id": "550e8400-e29b-41d4-a716-446655440000",
    "subject_number": "001-001",
    "enrolled_date": "2026-05-29",
    "demographics": {
      "age": 45,
      "sex": "F"
    }
  },
  "metadata": {
    "user_id": "user-xyz",
    "ip_address": "10.0.1.50",
    "session_id": "sess-abc"
  }
}
```

### 4.4 Consumer Groups

| Consumer Group | Topics Consumed | Instances | Purpose |
|---------------|----------------|-----------|---------|
| cdos-transform-engine | cdos.pipeline.raw.ingested | 3 | Trigger canonical normalization |
| cdos-sdtm-mapper | cdos.pipeline.canonical.created, cdos.pipeline.canonical.updated | 2 | Trigger SDTM mapping |
| cdos-safety-notifier | cdos.clinical.adverse_event.reported, cdos.clinical.adverse_event.sae_flagged | 2 | Notify Safety system |
| cdos-iwrs-trigger | cdos.clinical.subject.enrolled | 1 | Trigger IWRS randomization |
| cdos-audit-logger | cdos.audit.* | 2 | 21 CFR Part 11 audit trail |
| cdos-notification | cdos.clinical.query.raised, cdos.clinical.query.responded | 1 | User notifications |

### 4.5 Event-Driven Integration Matrix

| Event | Producer | Consumer(s) | Action |
|-------|----------|-------------|--------|
| subject.enrolled | API Gateway | IWRS Adapter, Audit Logger | Trigger randomization, log |
| adverse_event.reported | API Gateway | Safety Adapter, Audit Logger | Notify safety, log |
| adverse_event.sae_flagged | Transform Engine | Safety Adapter, Notification | SUSAR check, alert |
| crf_page.submitted | API Gateway | Transform Engine | Trigger normalization |
| raw.ingested | Transform Engine | Canonical Normalizer | Stage 2 trigger |
| canonical.created | Transform Engine | SDTM Mapper | Stage 3a trigger |
| sdtm.mapped | Transform Engine | ADaM Mapper | Stage 3b trigger |
| adam.mapped | Transform Engine | Submission Packager | Stage 4 trigger |
| submission.ready | Transform Engine | RegSubmit Adapter | Upload to agency |
| query.raised | API Gateway | Notification Service | Alert assigned user |

---

## 5. Authentication & Headers

### 5.1 Required Headers

| Header | Description | Example |
|--------|-------------|---------|
| Authorization | Bearer token (OAuth2) | Bearer eyJhbGciOi... |
| X-Request-ID | Unique request ID | req-6ba7b810-... |
| X-Correlation-ID | Correlation for tracing | corr-abc123 |
| Content-Type | Always application/json | application/json |
| Accept | application/json | application/json |

### 5.2 Response Headers

| Header | Description | Example |
|--------|-------------|---------|
| X-Request-ID | Echo request ID | req-6ba7b810-... |
| X-RateLimit-Limit | Rate limit ceiling | 1000 |
| X-RateLimit-Remaining | Remaining requests | 999 |
| X-RateLimit-Reset | Reset timestamp | 1622505600 |

---

## 6. API Versioning

- URI path versioning: `/v1/`, `/v2/`
- Deprecation announced via `Deprecation` header
- Minimum 6-month support for deprecated versions
- Breaking changes trigger major version bump
