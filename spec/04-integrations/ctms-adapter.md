# Adapter: CTMS

Clinical Trial Management System for study planning, site management, monitoring, and operational oversight. Referenced products: Oracle Siebel CTMS, Medidata CTMS, Veeva Vault CTMS.

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /studies | GET | query: status, phase, sponsor | [Entity:Study][] | OAuth2 Bearer |
| /studies/{study_id} | GET | path: study_id | [Entity:Study] | OAuth2 Bearer |
| /studies/{study_id}/sites | GET | path: study_id, query: status, country | [Entity:Site][] | OAuth2 Bearer |
| /sites/{site_id}/investigators | GET | path: site_id | [Entity:Investigator][] | OAuth2 Bearer |
| /studies/{study_id}/enrollment | GET | path: study_id | { target, actual, forecast } | OAuth2 Bearer |
| /studies/{study_id}/milestones | GET | path: study_id | Milestone[] | OAuth2 Bearer |
| /studies/{study_id}/milestones/{id} | PUT | Milestone (JSON) | Milestone (updated) | OAuth2 Bearer |
| /monitoring/visits | POST | MonitoringVisit (JSON) | MonitoringVisit (with id) | OAuth2 Bearer |
| /monitoring/visits/{id}/findings | GET | path: visit_id | Finding[] | OAuth2 Bearer |
| /studies/{study_id}/protocol-amendments | GET | path: study_id | [Entity:Protocol][] | OAuth2 Bearer |
| /studies/{study_id}/reports/enrollment | GET | path: study_id, query: granularity | EnrollmentReport | OAuth2 Bearer |
| /studies/{study_id}/reports/site-performance | GET | path: study_id | SitePerformanceReport | OAuth2 Bearer |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| ctms.study.created | StudyCreatedEvent | CTMS | EDC, IWRS, LIMS |
| ctms.study.updated | StudyUpdatedEvent | CTMS | EDC, IWRS, LIMS, eTMF |
| ctms.site.activated | SiteActivatedEvent | CTMS | EDC, IWRS, LIMS |
| ctms.site.deactivated | SiteDeactivatedEvent | CTMS | EDC, IWRS |
| ctms.investigator.added | InvestigatorAddedEvent | CTMS | EDC, eTMF |
| ctms.protocol.amended | ProtocolAmendedEvent | CTMS | EDC, IWRS, LIMS, RegSubmit |
| ctms.enrollment.milestone | EnrollmentMilestoneEvent | CTMS | (internal dashboards) |
| ctms.monitoring.visit-scheduled | MonitoringVisitScheduledEvent | CTMS | EDC |

## Event Schemas

### StudyCreatedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/study-created.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "study_id", "study_name", "protocol_number"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "ctms.study.created" },
    "timestamp": { "type": "string", "format": "date-time" },
    "study_id": { "type": "string", "format": "uuid" },
    "study_name": { "type": "string" },
    "protocol_number": { "type": "string" },
    "phase": { "type": "string", "enum": ["I", "II", "III", "IV"] },
    "sponsor": { "type": "string" }
  }
}
```

### SiteActivatedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/site-activated.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "site_id", "study_id"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "ctms.site.activated" },
    "timestamp": { "type": "string", "format": "date-time" },
    "site_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "site_name": { "type": "string" },
    "country": { "type": "string" },
    "principal_investigator_id": { "type": "string", "format": "uuid" }
  }
}
```

## Error Handling

- **Retry**: 3 attempts with exponential backoff (1s, 5s, 25s)
- **Dead letter queue**: `dlq.ctms` — messages exceeding retry limit routed here with full payload and error context
- **Circuit breaker**: 5 failures in 60s → circuit OPEN for 30s, half-open on next request, close after 3 consecutive successes
- **Timeout**: API requests timeout after 30s; event publish timeout after 10s
- **Idempotency**: All POST/PUT endpoints accept `Idempotency-Key` header; duplicate requests within 24h return cached response

## SLA

- **Latency (API)**: p50 < 100ms, p95 < 300ms, p99 < 500ms
- **Latency (Events)**: p99 < 5s for event delivery to all consumers
- **Availability**: 99.9% uptime (≤8.76h downtime/year)
- **RPO**: 0 (zero data loss — all writes durable before acknowledgment)
- **RTO**: < 15 minutes for failover to standby region

## Data Model Cross-References

Adapter reads/writes these canonical entities:
- [Entity:Study] — study lifecycle, metadata, status
- [Entity:Site] — site activation, enrollment targets, performance
- [Entity:Investigator] — PI/sub-I assignments, qualifications
- [Entity:Protocol] — protocol versions, amendments
