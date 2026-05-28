# Adapter: IWRS

Interactive Web Response System for randomization, drug assignment, kit management, and supply chain logistics. Referenced products: Signant Health, 4G Clinical, Medidata RTSM.

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /studies/{study_id}/randomize | POST | { subject_id, site_id, stratum } | RandomizationResult | OAuth2 Bearer |
| /subjects/{subject_id}/randomization | GET | path: subject_id | RandomizationResult | OAuth2 Bearer |
| /studies/{study_id}/treatment-codes | GET | path: study_id, query: unblinded | TreatmentCode[] | OAuth2 Bearer (restricted) |
| /studies/{study_id}/kit-assignments | POST | { subject_id, visit_id, kit_type } | KitAssignment | OAuth2 Bearer |
| /subjects/{subject_id}/kit-assignments | GET | path: subject_id | KitAssignment[] | OAuth2 Bearer |
| /studies/{study_id}/supply/inventory | GET | path: study_id, query: site_id, depot | InventoryLevel[] | OAuth2 Bearer |
| /studies/{study_id}/supply/resupply | POST | { site_id, kit_type, quantity } | ResupplyOrder | OAuth2 Bearer |
| /studies/{study_id}/stratification | POST | { subject_id, factors } | StratumResult | OAuth2 Bearer |
| /studies/{study_id}/dose-escalation | GET | path: study_id | DoseLevel[] | OAuth2 Bearer |
| /studies/{study_id}/dose-escalation/next-cohort | POST | { cohort_size, toxicity_data } | CohortDecision | OAuth2 Bearer |
| /studies/{study_id}/unblind | POST | { subject_id, reason, authorized_by } | UnblindingResult | OAuth2 Bearer (restricted) |
| /studies/{study_id}/settings | GET | path: study_id | IWRSSettings | OAuth2 Bearer |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| iwrs.subject.randomized | SubjectRandomizedEvent | IWRS | CTMS, EDC |
| iwrs.kit.assigned | KitAssignedEvent | IWRS | EDC, LIMS |
| iwrs.kit.returned | KitReturnedEvent | IWRS | LIMS |
| iwrs.supply.low-stock | SupplyLowStockEvent | IWRS | CTMS |
| iwrs.supply.resupply-triggered | ResupplyTriggeredEvent | IWRS | CTMS |
| iwrs.dose-escalation.decision | DoseEscalationDecisionEvent | IWRS | CTMS, EDC |
| iwrs.unblinding.requested | UnblindingRequestedEvent | IWRS | CTMS |
| iwrs.unblinding.executed | UnblindingExecutedEvent | IWRS | CTMS, EDC |

## Event Schemas

### SubjectRandomizedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/subject-randomized.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "subject_id", "study_id", "site_id", "treatment_arm", "randomization_number", "stratum"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "iwrs.subject.randomized" },
    "timestamp": { "type": "string", "format": "date-time" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "site_id": { "type": "string", "format": "uuid" },
    "treatment_arm": { "type": "string" },
    "randomization_number": { "type": "integer" },
    "stratum": { "type": "string" },
    "block_id": { "type": "string" }
  }
}
```

### KitAssignedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/kit-assigned.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "kit_id", "subject_id", "study_id", "visit_id"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "iwrs.kit.assigned" },
    "timestamp": { "type": "string", "format": "date-time" },
    "kit_id": { "type": "string" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "visit_id": { "type": "string", "format": "uuid" },
    "kit_type": { "type": "string" },
    "lot_number": { "type": "string" },
    "expiration_date": { "type": "string", "format": "date" }
  }
}
```

## Error Handling

- **Retry**: 3 attempts with exponential backoff (1s, 5s, 25s)
- **Dead letter queue**: `dlq.iwrs` — messages exceeding retry limit routed here with full payload and error context
- **Circuit breaker**: 5 failures in 60s → circuit OPEN for 30s, half-open on next request, close after 3 consecutive successes
- **Timeout**: API requests timeout after 30s; event publish timeout after 10s
- **Idempotency**: All POST endpoints accept `Idempotency-Key` header; duplicate requests within 24h return cached response
- **Randomization failure**: If randomization API fails, subject is NOT enrolled — rollback EDC enrollment, alert site coordinator
- **Unblinding safeguards**: Unblind endpoint requires dual authorization (2 different users with role `unblind_authorizer`); all unblind events published immediately to CTMS and EDC

## SLA

- **Latency (API)**: p50 < 200ms, p95 < 500ms, p99 < 1s (randomization is latency-sensitive but not sub-100ms)
- **Latency (Events)**: p99 < 5s for standard events; < 1s for randomization and unblinding events
- **Availability**: 99.95% uptime (≤4.38h downtime/year) — elevated due to randomization dependency for enrollment
- **RPO**: 0 (zero data loss — randomization assignments are irreversible and must be durable)
- **RTO**: < 10 minutes for failover to standby region

## Data Model Cross-References

Adapter reads/writes these canonical entities:
- [Entity:Subject] — subject randomization assignment (write: treatment_arm, randomization_number)
- [Entity:Dose] — kit/dose assignment per visit
- [Entity:Study] — study randomization settings, stratification factors (read-only)
- [Entity:Site] — site inventory and supply levels (read-only)
- [Entity:Visit] — visit context for kit assignment (read-only)
