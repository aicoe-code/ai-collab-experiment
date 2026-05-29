# CDOS Error Model

All CDOS APIs (REST and Events) use a consistent error model based on [RFC 9457 (Problem Details for HTTP APIs)](https://www.rfc-editor.org/rfc/rfc9457).

## REST Error Response Format

All REST error responses use `Content-Type: application/problem+json`:

```json
{
  "type": "https://api.cdos.io/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Field 'severity' must be one of: MILD, MODERATE, SEVERE",
  "instance": "https://api.cdos.io/v1/studies/123/adverse-events",
  "errors": [
    {
      "field": "severity",
      "message": "Invalid enum value",
      "value": "MINOR"
    }
  ]
}
```

## Error Codes

| HTTP Status | Error Type | When Used |
|------------|-----------|-----------|
| 400 | `bad-request` | Malformed request body or query parameters |
| 401 | `unauthenticated` | Missing or invalid authentication token |
| 403 | `forbidden` | Authenticated but insufficient permissions |
| 404 | `not-found` | Resource does not exist |
| 409 | `conflict` | Resource already exists or state conflict |
| 422 | `validation-error` | Request valid JSON but fails business rules |
| 429 | `rate-limited` | Too many requests |
| 500 | `internal-error` | Unexpected server error |
| 503 | `service-unavailable` | Downstream system unavailable |

## Error Type URIs

| Error Type | URI |
|-----------|-----|
| Bad Request | `https://api.cdos.io/errors/bad-request` |
| Unauthenticated | `https://api.cdos.io/errors/unauthenticated` |
| Forbidden | `https://api.cdos.io/errors/forbidden` |
| Not Found | `https://api.cdos.io/errors/not-found` |
| Conflict | `https://api.cdos.io/errors/conflict` |
| Validation Error | `https://api.cdos.io/errors/validation-error` |
| Rate Limited | `https://api.cdos.io/errors/rate-limited` |
| Internal Error | `https://api.cdos.io/errors/internal-error` |
| Service Unavailable | `https://api.cdos.io/errors/service-unavailable` |
| Adapter Error | `https://api.cdos.io/errors/adapter-error` |
| Transform Error | `https://api.cdos.io/errors/transform-error` |
| Compliance Error | `https://api.cdos.io/errors/compliance-error` |

## Event Error Model

For asynchronous event processing failures, errors are published to a dead-letter queue (DLQ) topic:

```json
{
  "error_id": "uuid",
  "original_event_id": "uuid",
  "original_topic": "ae.reported",
  "error_type": "transform-error",
  "error_code": "INVALID_MEDDRA_CODE",
  "message": "MedDRA code 'XYZ' not found in version 27.0",
  "retryable": true,
  "retry_count": 3,
  "max_retries": 5,
  "failed_at": "2026-05-28T10:30:00Z",
  "context": {
    "ae_id": "uuid",
    "study_id": "uuid"
  }
}
```

## Event Error Codes

| Code | Topic | Retryable | Description |
|------|-------|-----------|-------------|
| `INVALID_MEDDRA_CODE` | ae.reported | Yes | MedDRA code not in controlled terminology |
| `DUPLICATE_ENROLLMENT` | subject.enrolled | No | Subject already enrolled in study |
| `SITE_NOT_ACTIVE` | subject.enrolled | No | Site is not in ACTIVE status |
| `LAB_VALUE_OUT_OF_RANGE` | lab.result_received | Yes | Lab value exceeds plausible range |
| `SAFETY_REPORT_FAILED` | ae.susar | Yes | Safety report submission to authority failed |
| `IWRS_UNAVAILABLE` | subject.randomized | Yes | IWRS system not responding |
| `CDISC_MAPPING_FAILED` | lab.result_received | Yes | SDTM mapping transformation error |
| `AUDIT_TRAIL_WRITE_FAILED` | * | Yes | Audit trail persistence failed |

## Error Handling Strategy

| Layer | Behavior |
|-------|----------|
| API Gateway | Returns problem+json to caller, logs error |
| Event Producer | Publishes to DLQ after max retries exhausted |
| Event Consumer | Retries with exponential backoff, then DLQ |
| Transform Engine | Quarantines records with transform errors |
| Adapter | Circuit breaker: 5 failures in 60s → open for 30s |
