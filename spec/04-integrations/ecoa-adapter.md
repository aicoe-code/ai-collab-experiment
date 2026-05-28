# Adapter: eCOA

Electronic Clinical Outcome Assessment system for patient-reported outcomes (PRO), clinician-reported outcomes (ClinRO), and observer-reported outcomes (ObsRO). Referenced products: ERT, Clario, Medidata Patient Cloud.

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /studies/{study_id}/instruments | GET | path: study_id, query: type, language | Instrument[] | OAuth2 Bearer |
| /instruments/{instrument_id} | GET | path: instrument_id | Instrument | OAuth2 Bearer |
| /subjects/{subject_id}/assessments | GET | path: subject_id, query: visit_id, status | Assessment[] | OAuth2 Bearer |
| /assessments | POST | Assessment (JSON) | Assessment (with assessment_id) | OAuth2 Bearer |
| /assessments/{assessment_id}/responses | GET | path: assessment_id | Response[] | OAuth2 Bearer |
| /assessments/{assessment_id}/responses | POST | { responses: Response[] } | Response[] (with timestamps) | OAuth2 Bearer |
| /assessments/{assessment_id}/complete | PATCH | { completion_status, reason } | Assessment (completed) | OAuth2 Bearer |
| /subjects/{subject_id}/compliance | GET | path: subject_id, query: study_id | ComplianceReport | OAuth2 Bearer |
| /studies/{study_id}/e-diary/config | GET | path: study_id | EDiaryConfig | OAuth2 Bearer |
| /studies/{study_id}/e-diary/reminders | POST | { subject_id, schedule } | Reminder | OAuth2 Bearer |
| /studies/{study_id}/translations | GET | path: study_id, query: language | Translation[] | OAuth2 Bearer |
| /devices/provision | POST | { subject_id, device_type, os } | DeviceProvisioning | OAuth2 Bearer |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| ecoa.assessment.completed | AssessmentCompletedEvent | eCOA | EDC, CTMS |
| ecoa.assessment.missed | AssessmentMissedEvent | eCOA | CTMS |
| ecoa.response.submitted | ResponseSubmittedEvent | eCOA | EDC |
| ecoa.compliance.alert | ComplianceAlertEvent | eCOA | CTMS |
| ecoa.device.provisioned | DeviceProvisionedEvent | eCOA | CTMS |
| ecoa.device.returned | DeviceReturnedEvent | eCOA | CTMS |
| ecoa.instrument.validated | InstrumentValidatedEvent | eCOA | CTMS |

## Event Schemas

### AssessmentCompletedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/assessment-completed.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "assessment_id", "subject_id", "study_id", "instrument_id", "visit_id"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "ecoa.assessment.completed" },
    "timestamp": { "type": "string", "format": "date-time" },
    "assessment_id": { "type": "string", "format": "uuid" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "instrument_id": { "type": "string", "format": "uuid" },
    "visit_id": { "type": "string", "format": "uuid" },
    "completion_time_seconds": { "type": "integer" },
    "raw_score": { "type": "number" },
    "total_score": { "type": "number" },
    "language": { "type": "string" }
  }
}
```

### ComplianceAlertEvent
```json
{
  "$id": "https://cdos.io/schemas/events/compliance-alert.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "subject_id", "study_id", "alert_type", "compliance_rate"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "ecoa.compliance.alert" },
    "timestamp": { "type": "string", "format": "date-time" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "alert_type": { "type": "string", "enum": ["LOW_COMPLIANCE", "MISSED_WINDOW", "DEVICE_NON_RETURN"] },
    "compliance_rate": { "type": "number", "minimum": 0, "maximum": 100 }
  }
}
```

## Error Handling

- **Retry**: 3 attempts with exponential backoff (1s, 5s, 25s)
- **Dead letter queue**: `dlq.ecoa` — messages exceeding retry limit routed here with full payload and error context
- **Circuit breaker**: 5 failures in 60s → circuit OPEN for 30s, half-open on next request, close after 3 consecutive successes
- **Timeout**: API requests timeout after 30s; event publish timeout after 10s
- **Idempotency**: All POST/PATCH endpoints accept `Idempotency-Key` header; duplicate requests within 24h return cached response
- **Offline-capable**: eCOA responses collected on device are queued locally and synced when connectivity is restored; conflict resolution uses last-write-wins by device timestamp
- **Missed assessment window**: If assessment not completed within visit window + 24h grace period, auto-generate `AssessmentMissedEvent`

## SLA

- **Latency (API)**: p50 < 100ms, p95 < 300ms, p99 < 500ms
- **Latency (Events)**: p99 < 5s for event delivery to all consumers
- **Availability**: 99.9% uptime (≤8.76h downtime/year)
- **RPO**: 0 (zero data loss — all responses durable before acknowledgment)
- **RTO**: < 15 minutes for failover to standby region

## Data Model Cross-References

Adapter reads/writes these canonical entities:
- [Entity:Subject] — subject context for assessment assignment (read-only)
- [Entity:Visit] — visit window for assessment scheduling (read-only)
- [Entity:Study] — study instrument configuration (read-only)
- [Entity:CRFPage] — eCOA responses mapped to CRF pages for EDC integration (write)
