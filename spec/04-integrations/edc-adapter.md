# Adapter: EDC

Electronic Data Capture system for clinical trial data collection. Manages CRF data entry, edit checks, queries, and data extraction. Referenced products: Medidata Rave, Oracle InForm, Veeva Vault CDMS, Castor.

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /studies/{study_id}/subjects | GET | path: study_id | [Entity:Subject][] | OAuth2 Bearer |
| /subjects | POST | [Entity:Subject] (JSON) | [Entity:Subject] (with subject_id) | OAuth2 Bearer |
| /subjects/{subject_id}/crf-pages | GET | path: subject_id, query: visit_id | [Entity:CRFPage][] | OAuth2 Bearer |
| /crf-pages/{crf_id} | PUT | [Entity:CRFPage] (JSON) | [Entity:CRFPage] (updated) | OAuth2 Bearer |
| /subjects/{subject_id}/queries | GET | path: subject_id | [Entity:Query][] | OAuth2 Bearer |
| /queries | POST | [Entity:Query] (JSON) | [Entity:Query] (with query_id) | OAuth2 Bearer |
| /queries/{query_id}/resolve | PATCH | { resolution, resolved_by } | [Entity:Query] (resolved) | OAuth2 Bearer |
| /studies/{study_id}/adverse-events | GET | path: study_id, query: severity | [Entity:AdverseEvent][] | OAuth2 Bearer |
| /adverse-events | POST | [Entity:AdverseEvent] (JSON) | [Entity:AdverseEvent] (with ae_id) | OAuth2 Bearer |
| /studies/{study_id}/visits | GET | path: study_id | [Entity:Visit][] | OAuth2 Bearer |
| /studies/{study_id}/export/sdtm | GET | path: study_id, query: domain, format | SDTM dataset (XPT/CSV) | OAuth2 Bearer |
| /audit-trail | GET | query: entity_type, entity_id, date_range | AuditEntry[] | OAuth2 Bearer (admin) |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| edc.subject.enrolled | SubjectEnrolledEvent | EDC | CTMS, IWRS, eCOA |
| edc.crfpage.submitted | CRFPageSubmittedEvent | EDC | LIMS |
| edc.query.raised | QueryRaisedEvent | EDC | CTMS |
| edc.query.resolved | QueryResolvedEvent | EDC | CTMS |
| edc.ae.reported | AeReportedEvent | EDC | Safety, CTMS |
| edc.visit.completed | VisitCompletedEvent | EDC | CTMS, LIMS, IWRS |
| edc.data.changed | DataChangedEvent | EDC | CTMS |
| edc.study.locked | StudyLockedEvent | EDC | CTMS, Safety, RegSubmit |

## Event Schemas

### SubjectEnrolledEvent
```json
{
  "$id": "https://cdos.io/schemas/events/subject-enrolled.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "subject_id", "study_id", "site_id"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "edc.subject.enrolled" },
    "timestamp": { "type": "string", "format": "date-time" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "site_id": { "type": "string", "format": "uuid" },
    "enrollment_date": { "type": "string", "format": "date" }
  }
}
```

### AeReportedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/ae-reported.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "ae_id", "subject_id", "study_id", "severity", "serious"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "edc.ae.reported" },
    "timestamp": { "type": "string", "format": "date-time" },
    "ae_id": { "type": "string", "format": "uuid" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "severity": { "type": "string", "enum": ["MILD", "MODERATE", "SEVERE"] },
    "serious": { "type": "boolean" }
  }
}
```

## Error Handling

- **Retry**: 3 attempts with exponential backoff (1s, 5s, 25s)
- **Dead letter queue**: `dlq.edc` — messages exceeding retry limit routed here with full payload and error context
- **Circuit breaker**: 5 failures in 60s → circuit OPEN for 30s, half-open on next request, close after 3 consecutive successes
- **Timeout**: API requests timeout after 30s; event publish timeout after 10s
- **Idempotency**: All POST/PATCH endpoints accept `Idempotency-Key` header; duplicate requests within 24h return cached response

## SLA

- **Latency (API)**: p50 < 100ms, p95 < 300ms, p99 < 500ms
- **Latency (Events)**: p99 < 5s for event delivery to all consumers
- **Availability**: 99.9% uptime (≤8.76h downtime/year)
- **RPO**: 0 (zero data loss — all writes durable before acknowledgment)
- **RTO**: < 15 minutes for failover to standby region

## Data Model Cross-References

Adapter reads/writes these canonical entities:
- [Entity:Subject] — enrollment, demographics, status
- [Entity:CRFPage] — form data entry, edit checks
- [Entity:Query] — data clarification requests
- [Entity:AdverseEvent] — AE reporting
- [Entity:Visit] — visit schedule and completion
- [Entity:Study] — study metadata (read-only)
- [Entity:Site] — site context (read-only)
