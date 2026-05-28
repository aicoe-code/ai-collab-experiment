# Adapter: Wearables

IoT and wearable sensor system for continuous data collection including activity, heart rate, sleep, and digital biomarkers. Referenced products: ActiGraph, Verily, Apple HealthKit.

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /studies/{study_id}/device-types | GET | path: study_id | DeviceType[] | OAuth2 Bearer |
| /subjects/{subject_id}/devices | GET | path: subject_id, query: status | Device[] | OAuth2 Bearer |
| /devices | POST | DeviceProvisionRequest (JSON) | Device (with device_id) | OAuth2 Bearer |
| /devices/{device_id}/decommission | POST | { reason } | Device (decommissioned) | OAuth2 Bearer |
| /subjects/{subject_id}/sensor-data | GET | path: subject_id, query: sensor_type, date_range, granularity | SensorData[] | OAuth2 Bearer |
| /sensor-data | POST | SensorDataBatch (JSON) | { accepted, rejected, duplicates } | OAuth2 Bearer |
| /subjects/{subject_id}/digital-biomarkers | GET | path: subject_id, query: biomarker_type, date_range | DigitalBiomarker[] | OAuth2 Bearer |
| /digital-biomarkers | POST | DigitalBiomarker (JSON) | DigitalBiomarker (with id) | OAuth2 Bearer |
| /studies/{study_id}/wearable-config | GET | path: study_id | WearableConfig | OAuth2 Bearer |
| /studies/{study_id}/wearable-config | PUT | WearableConfig (JSON) | WearableConfig (updated) | OAuth2 Bearer |
| /subjects/{subject_id}/compliance | GET | path: subject_id, query: study_id, date_range | WearableCompliance | OAuth2 Bearer |
| /alerts | GET | query: subject_id, study_id, severity | WearableAlert[] | OAuth2 Bearer |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| wearables.data.received | SensorDataReceivedEvent | Wearables | EDC |
| wearables.biomarker.derived | BiomarkerDerivedEvent | Wearables | EDC, CTMS |
| wearables.device.provisioned | DeviceProvisionedEvent | Wearables | CTMS |
| wearables.device.returned | DeviceReturnedEvent | Wearables | CTMS |
| wearables.compliance.alert | WearableComplianceAlertEvent | Wearables | CTMS |
| wearables.alert.triggered | WearableAlertTriggeredEvent | Wearables | CTMS, Safety |
| wearables.data.quality-issue | DataQualityIssueEvent | Wearables | CTMS |

## Event Schemas

### SensorDataReceivedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/sensor-data-received.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "subject_id", "study_id", "device_id", "sensor_type", "data_points_count", "start_time", "end_time"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "wearables.data.received" },
    "timestamp": { "type": "string", "format": "date-time" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "device_id": { "type": "string", "format": "uuid" },
    "sensor_type": { "type": "string", "enum": ["ACCELEROMETER", "GYROSCOPE", "HEART_RATE", "ECG", "SPO2", "SKIN_TEMPERATURE", "GPS"] },
    "data_points_count": { "type": "integer" },
    "start_time": { "type": "string", "format": "date-time" },
    "end_time": { "type": "string", "format": "date-time" }
  }
}
```

### BiomarkerDerivedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/biomarker-derived.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "subject_id", "study_id", "biomarker_type", "value", "unit", "derivation_window"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "wearables.biomarker.derived" },
    "timestamp": { "type": "string", "format": "date-time" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "biomarker_type": { "type": "string", "enum": ["DAILY_STEP_COUNT", "ACTIVE_MINUTES", "SLEEP_DURATION", "SLEEP_EFFICIENCY", "RESTING_HR", "HRV_SDNN", "WALKING_SPEED", "GAIT_SYMMETRY", "TREMOR_SCORE"] },
    "value": { "type": "number" },
    "unit": { "type": "string" },
    "derivation_window": { "type": "string" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
  }
}
```

## Error Handling

- **Retry**: 3 attempts with exponential backoff (1s, 5s, 25s)
- **Dead letter queue**: `dlq.wearables` — messages exceeding retry limit routed here with full payload and error context
- **Circuit breaker**: 5 failures in 60s → circuit OPEN for 30s, half-open on next request, close after 3 consecutive successes
- **Timeout**: API requests timeout after 30s; sensor data batch upload timeout after 60s (high-volume)
- **Idempotency**: All POST endpoints accept `Idempotency-Key` header; duplicate requests within 24h return cached response
- **High-volume ingestion**: Sensor data arrives in batches of up to 10,000 data points; uses async processing with backpressure — returns 202 Accepted with processing job ID
- **Data quality**: Invalid or out-of-range sensor readings flagged with `DataQualityIssueEvent`; data quarantined for review, not rejected
- **Device connectivity**: Device offline > 24h triggers `WearableComplianceAlertEvent`; device offline > 72h escalates to CTMS for action

## SLA

- **Latency (API)**: p50 < 100ms, p95 < 300ms, p99 < 500ms (metadata); p99 < 5s (sensor data batch upload)
- **Latency (Events)**: p99 < 5s for event delivery to all consumers
- **Availability**: 99.9% uptime (≤8.76h downtime/year)
- **RPO**: 0 (zero data loss — all sensor data durable before acknowledgment)
- **RTO**: < 15 minutes for failover to standby region
- **Throughput**: Support ≥ 10,000 data points/second sustained ingestion across all studies

## Data Model Cross-References

Adapter reads/writes these canonical entities:
- [Entity:Subject] — subject context for device provisioning and data association (read-only)
- [Entity:Study] — study wearable configuration (read-only)
- [Entity:Visit] — visit context for biomarker windowing (read-only)
- [Entity:CRFPage] — wearable-derived data mapped to CRF pages for EDC integration (write)
- [Entity:LabResult] — digital biomarkers treated as lab-equivalent results (write)
