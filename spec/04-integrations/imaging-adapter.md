# Adapter: Imaging

Medical imaging system for radiological assessments, image upload, central reader workflow, and RECIST/mRECIST measurements. Referenced products: BioClinica, Parexel Imaging, Medidata Imaging.

## API Contract

| Endpoint | Method | Request | Response | Auth |
|----------|--------|---------|----------|------|
| /studies/{study_id}/imaging-protocols | GET | path: study_id | ImagingProtocol[] | OAuth2 Bearer |
| /subjects/{subject_id}/images | GET | path: subject_id, query: visit_id, modality | Image[] | OAuth2 Bearer |
| /images | POST | ImageUploadRequest (multipart/form-data) | Image (with image_id) | OAuth2 Bearer |
| /images/{image_id} | GET | path: image_id | Image (metadata) | OAuth2 Bearer |
| /images/{image_id}/dicom | GET | path: image_id | DICOM file (binary) | OAuth2 Bearer |
| /images/{image_id}/quality-check | POST | { qc_status, findings } | ImageQCResult | OAuth2 Bearer |
| /readers/{reader_id}/assignments | GET | path: reader_id, query: status | ReadingAssignment[] | OAuth2 Bearer |
| /readings | POST | Reading (JSON) | Reading (with reading_id) | OAuth2 Bearer |
| /readings/{reading_id} | PUT | Reading (JSON) | Reading (updated) | OAuth2 Bearer |
| /subjects/{subject_id}/measurements | GET | path: subject_id, query: visit_id, method | Measurement[] | OAuth2 Bearer |
| /measurements | POST | Measurement (JSON) | Measurement (with measurement_id) | OAuth2 Bearer |
| /subjects/{subject_id}/response-assessment | GET | path: subject_id, query: method (RECIST/mRECIST) | ResponseAssessment | OAuth2 Bearer |

## Event Contract

| Topic | Schema | Producer | Consumer |
|-------|--------|----------|----------|
| imaging.image.uploaded | ImageUploadedEvent | Imaging | CTMS |
| imaging.image.qc-passed | ImageQCPassedEvent | Imaging | CTMS |
| imaging.image.qc-failed | ImageQCFailedEvent | Imaging | CTMS |
| imaging.reading.completed | ReadingCompletedEvent | Imaging | EDC, CTMS |
| imaging.reading.discrepancy | ReadingDiscrepancyEvent | Imaging | CTMS |
| imaging.response.assessed | ResponseAssessedEvent | Imaging | EDC, CTMS |
| imaging.reader.assigned | ReaderAssignedEvent | Imaging | CTMS |

## Event Schemas

### ReadingCompletedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/reading-completed.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "reading_id", "image_id", "subject_id", "study_id", "reader_id"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "imaging.reading.completed" },
    "timestamp": { "type": "string", "format": "date-time" },
    "reading_id": { "type": "string", "format": "uuid" },
    "image_id": { "type": "string", "format": "uuid" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "reader_id": { "type": "string", "format": "uuid" },
    "findings": { "type": "string" },
    "target_lesion_count": { "type": "integer" },
    "non_target_lesion_count": { "type": "integer" }
  }
}
```

### ResponseAssessedEvent
```json
{
  "$id": "https://cdos.io/schemas/events/response-assessed.json",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "subject_id", "study_id", "visit_id", "method", "overall_response"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "imaging.response.assessed" },
    "timestamp": { "type": "string", "format": "date-time" },
    "subject_id": { "type": "string", "format": "uuid" },
    "study_id": { "type": "string", "format": "uuid" },
    "visit_id": { "type": "string", "format": "uuid" },
    "method": { "type": "string", "enum": ["RECIST_1.1", "mRECIST", "iRECIST", "LYRIC", "RANO"] },
    "overall_response": { "type": "string", "enum": ["CR", "PR", "SD", "PD", "NE", "CRi", "PRi"] },
    "sum_target_lesions_mm": { "type": "number" },
    "new_lesions": { "type": "boolean" }
  }
}
```

## Error Handling

- **Retry**: 3 attempts with exponential backoff (1s, 5s, 25s)
- **Dead letter queue**: `dlq.imaging` — messages exceeding retry limit routed here with full payload and error context
- **Circuit breaker**: 5 failures in 60s → circuit OPEN for 30s, half-open on next request, close after 3 consecutive successes
- **Timeout**: API requests timeout after 30s; DICOM upload timeout after 120s (large file handling)
- **Idempotency**: All POST/PUT endpoints accept `Idempotency-Key` header; duplicate requests within 24h return cached response
- **Large file handling**: DICOM uploads > 100MB use chunked upload with resumable protocol; failed chunks retry independently
- **Reading discrepancy resolution**: If reader 1 and reader 2 assessments disagree, `ReadingDiscrepancyEvent` triggers adjudication workflow with reader 3

## SLA

- **Latency (API)**: p50 < 100ms, p95 < 300ms, p99 < 500ms (metadata); p99 < 30s (DICOM download)
- **Latency (Events)**: p99 < 5s for event delivery to all consumers
- **Availability**: 99.9% uptime (≤8.76h downtime/year)
- **RPO**: 0 (zero data loss — all images and readings durable before acknowledgment)
- **RTO**: < 15 minutes for failover to standby region
- **Storage**: Images retained for study duration + 15 years per ICH E6(R2) requirements

## Data Model Cross-References

Adapter reads/writes these canonical entities:
- [Entity:Subject] — subject context for image and reading association (read-only)
- [Entity:Visit] — visit context for image timing (read-only)
- [Entity:Study] — study imaging protocol configuration (read-only)
- [Entity:CRFPage] — imaging assessments mapped to CRF pages for EDC integration (write)
