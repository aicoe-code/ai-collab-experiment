# Adapter: LIMS

Laboratory Information Management System for specimen tracking, lab test ordering, result management, and reference range validation. Referenced products: Medidata Rave Lab, Covance LIMS, ICON LIMS.

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /studies/{study_id}/samples | GET | path: study_id, query: subject_id, status | [Entity:Sample][] | OAuth2 Bearer |
| /samples | POST | [Entity:Sample] (JSON) | [Entity:Sample] (with sample_id) | OAuth2 Bearer |
| /samples/{sample_id} | GET | path: sample_id | [Entity:Sample] | OAuth2 Bearer |
| /samples/{sample_id}/status | PATCH | { status, reason } | [Entity:Sample] (updated) | OAuth2 Bearer |
| /studies/{study_id}/lab-results | GET | path: study_id, query: subject_id, panel, date_range | [Entity:LabResult][] | OAuth2 Bearer |
| /lab-results | POST | [Entity:LabResult] (JSON) | [Entity:LabResult] (with lab_id) | OAuth2 Bearer |
| /lab-results/{lab_id} | PUT | [Entity:LabResult] (JSON) | [Entity:LabResult] (updated) | OAuth2 Bearer |
| /studies/{study_id}/lab-manuals | GET | path: study_id | LabManual[] | OAuth2 Bearer |
| /studies/{study_id}/reference-ranges | GET | path: study_id, query: panel, sex, age_group | ReferenceRange[] | OAuth2 Bearer |
| /lab-orders | POST | LabOrder (JSON) | LabOrder (with order_id) | OAuth2 Bearer |
| /lab-orders/{order_id}/results | GET | path: order_id | [Entity:LabResult][] | OAuth2 Bearer |
| /studies/{study_id}/kits | GET | path: study_id, query: site_id | KitInventory[] | OAuth2 Bearer |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| lims.sample.received | SampleReceivedEvent | LIMS | EDC |
| lims.sample.rejected | SampleRejectedEvent | LIMS | EDC |
| lims.lab-result.released | LabResultReleasedEvent | LIMS | EDC, CTMS |
| lims.lab-result.critical | LabResultCriticalEvent | LIMS | Safety, EDC, CTMS |
| lims.kit.shipped | KitShippedEvent | LIMS | CTMS, IWRS |
| lims.kit.depleted | KitDepletedEvent | LIMS | CTMS |
| lims.reference-range.updated | ReferenceRangeUpdatedEvent | LIMS | EDC |

## Event Schemas

### LabResultReleasedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/lab-result-released.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "lab_id", "subject_id", "study_id", "sample_id", "test_code", "result_value", "unit", "normal_flag"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "lims.lab-result.released" },
    "timestamp": { "type": "string", "format": "date-time" },
    "lab_id": { "type": "string", "format": "uuid" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "sample_id": { "type": "string", "format": "uuid" },
    "test_code": { "type": "string" },
    "result_value": { "type": ["number", "string"] },
    "unit": { "type": "string" },
    "normal_flag": { "type": "string", "enum": ["NORMAL", "LOW", "HIGH", "ABNORMAL", "CRITICAL"] }
  }
}
```

### SampleReceivedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/sample-received.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "sample_id", "subject_id", "study_id"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "lims.sample.received" },
    "timestamp": { "type": "string", "format": "date-time" },
    "sample_id": { "type": "string", "format": "uuid" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "sample_type": { "type": "string" },
    "collection_date": { "type": "string", "format": "date" },
    "condition": { "type": "string", "enum": ["ACCEPTABLE", "HEMOLYZED", "CLOTTED", "INSUFFICIENT", "OTHER"] }
  }
}
```

## Error Handling

- **Retry**: 3 attempts with exponential backoff (1s, 5s, 25s)
- **Dead letter queue**: `dlq.lims` — messages exceeding retry limit routed here with full payload and error context
- **Circuit breaker**: 5 failures in 60s → circuit OPEN for 30s, half-open on next request, close after 3 consecutive successes
- **Timeout**: API requests timeout after 30s; event publish timeout after 10s
- **Idempotency**: All POST/PATCH endpoints accept `Idempotency-Key` header; duplicate requests within 24h return cached response
- **Critical result escalation**: Lab results with `normal_flag = CRITICAL` bypass normal queue and trigger immediate Safety + EDC notification via priority channel `lims.critical`

## SLA

- **Latency (API)**: p50 < 100ms, p95 < 300ms, p99 < 500ms
- **Latency (Events)**: p99 < 5s for standard events; < 1s for critical lab results
- **Availability**: 99.9% uptime (≤8.76h downtime/year)
- **RPO**: 0 (zero data loss — all writes durable before acknowledgment)
- **RTO**: < 15 minutes for failover to standby region

## Data Model Cross-References

Adapter reads/writes these canonical entities:
- [Entity:Sample] — specimen tracking, chain of custody, status
- [Entity:LabResult] — test results, reference ranges, normal flags
- [Entity:Subject] — subject context for result association (read-only)
- [Entity:Study] — study context, lab manual reference (read-only)
