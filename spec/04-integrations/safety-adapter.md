# Adapter: Safety

Pharmacovigilance system for adverse event processing, seriousness assessment, causality, expedited reporting (ICSR), SUSAR detection, and regulatory submission. Referenced products: Argus Safety, ArisGlobal, Oracle AERS.

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /cases | POST | SafetyCase (JSON) | SafetyCase (with case_id) | OAuth2 Bearer |
| /cases/{case_id} | GET | path: case_id | SafetyCase | OAuth2 Bearer |
| /cases/{case_id} | PUT | SafetyCase (JSON) | SafetyCase (updated) | OAuth2 Bearer |
| /cases/{case_id}/assessments | POST | CausalityAssessment (JSON) | CausalityAssessment | OAuth2 Bearer |
| /cases/{case_id}/icsr | GET | path: case_id | [Entity:Submission] (ICSR format) | OAuth2 Bearer |
| /cases/{case_id}/icsr/submit | POST | { regulatory_body, format } | [Entity:Submission] | OAuth2 Bearer |
| /studies/{study_id}/cases | GET | path: study_id, query: seriousness, date_range | SafetyCase[] | OAuth2 Bearer |
| /studies/{study_id}/susar-detection | POST | { analysis_window, threshold } | SUSARReport | OAuth2 Bearer |
| /signal-detection/run | POST | SignalDetectionRequest (JSON) | SignalDetectionResult | OAuth2 Bearer |
| /meddra/search | GET | query: term, level | MedDRAResult[] | OAuth2 Bearer |
| /studies/{study_id}/safety-report | GET | path: study_id, query: period | SafetyReport | OAuth2 Bearer |
| /cases/{case_id}/follow-up | POST | FollowUp (JSON) | FollowUp (with id) | OAuth2 Bearer |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| safety.case.created | SafetyCaseCreatedEvent | Safety | CTMS |
| safety.case.updated | SafetyCaseUpdatedEvent | Safety | CTMS |
| safety.sae.detected | SAEDetectedEvent | Safety | CTMS, EDC |
| safety.susar.detected | SUSARDetectedEvent | Safety | CTMS, RegSubmit |
| safety.icsr.submitted | ICSRSubmittedEvent | Safety | CTMS |
| safety.icsr.acknowledged | ICSRAcknowledgedEvent | Safety | CTMS |
| safety.signal.detected | SignalDetectedEvent | Safety | CTMS |

## Event Schemas

### SAEDetectedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/sae-detected.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "case_id", "ae_id", "subject_id", "study_id", "seriousness_criteria"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "safety.sae.detected" },
    "timestamp": { "type": "string", "format": "date-time" },
    "case_id": { "type": "string", "format": "uuid" },
    "ae_id": { "type": "string", "format": "uuid" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "seriousness_criteria": {
      "type": "array",
      "items": { "type": "string", "enum": ["DEATH", "LIFE_THREATENING", "HOSPITALIZATION", "DISABILITY", "CONGENITAL_ANOMALY", "IMPORTANT_MEDICAL_EVENT"] }
    },
    "meddra_pt": { "type": "string" },
    "reporting_deadline": { "type": "string", "format": "date-time" }
  }
}
```

### SUSARDetectedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/susar-detected.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "case_id", "ae_id", "study_id", "meddra_pt", "expectedness", "reporting_deadline"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "safety.susar.detected" },
    "timestamp": { "type": "string", "format": "date-time" },
    "case_id": { "type": "string", "format": "uuid" },
    "ae_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "meddra_pt": { "type": "string" },
    "expectedness": { "type": "string", "enum": ["EXPECTED", "UNEXPECTED"] },
    "reporting_deadline": { "type": "string", "format": "date-time" }
  }
}
```

## Error Handling

- **Retry**: 3 attempts with exponential backoff (1s, 5s, 25s)
- **Dead letter queue**: `dlq.safety` — messages exceeding retry limit routed here with full payload and error context
- **Circuit breaker**: 5 failures in 60s → circuit OPEN for 30s, half-open on next request, close after 3 consecutive successes
- **Timeout**: API requests timeout after 30s; event publish timeout after 10s
- **Idempotency**: All POST/PUT endpoints accept `Idempotency-Key` header; duplicate requests within 24h return cached response
- **Regulatory deadline enforcement**: SAE/SUSAR cases approaching reporting deadlines (72h for SUSAR, 15 calendar days for SAE) trigger escalation alerts at T-24h, T-12h, T-2h
- **ICSRAcknowledgedEvent retry**: If regulatory body does not acknowledge within 48h, escalate to safety operations

## SLA

- **Latency (API)**: p50 < 100ms, p95 < 300ms, p99 < 500ms
- **Latency (Events)**: p99 < 5s for standard events; < 1s for SAE/SUSAR events
- **Availability**: 99.95% uptime (≤4.38h downtime/year) — elevated due to regulatory reporting obligations
- **RPO**: 0 (zero data loss — all writes durable before acknowledgment)
- **RTO**: < 10 minutes for failover to standby region

## Data Model Cross-References

Adapter reads/writes these canonical entities:
- [Entity:AdverseEvent] — source AE data from EDC, enriched with causality and seriousness
- [Entity:Subject] — subject demographics for ICSR generation (read-only)
- [Entity:Study] — study context, IB reference for expectedness (read-only)
- [Entity:Submission] — ICSR regulatory submissions to health authorities
