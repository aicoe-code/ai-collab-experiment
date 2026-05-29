# CDOS Non-Functional Requirements (NFRs)

**Document Version:** 1.0
**Author:** Agent-TR
**Last Updated:** 2026-05-29

Each NFR is tagged with category and measurable acceptance target. References to
functional requirements (FR-xxx) are defined in `02-functional-requirements/`.

---

## Category: Performance

### TR-001: API Response Time (p50)
| Attribute | Value |
|-----------|-------|
| Category | Performance |
| Description | The CDOS Core API SHALL return responses at the 50th percentile in under 200ms for single-entity CRUD operations across all canonical entities (Study, Subject, Site, Visit, AdverseEvent, LabResult, CRFPage, Query). |
| Measurable Target | p50 latency < 200ms for /studies/{id}, /subjects/{id}, /sites/{id} GET/PUT endpoints |
| Traceability | Supports FR-001 (Study CRUD), FR-010 (Subject management) |

### TR-002: API Response Time (p99)
| Attribute | Value |
|-----------|-------|
| Category | Performance |
| Description | The CDOS Core API SHALL return responses at the 99th percentile in under 500ms for all single-entity CRUD operations and under 2000ms for aggregation/list endpoints under nominal load. |
| Measurable Target | p99 latency < 500ms (CRUD), p99 latency < 2000ms (list/aggregation) |
| Traceability | Supports FR-001, FR-010, FR-020 (Query management) |

### TR-003: Transform Pipeline Throughput
| Attribute | Value |
|-----------|-------|
| Category | Performance |
| Description | The CDOS transformation engine SHALL process SDTM mapping transforms at a sustained rate of at least 500 records per second per active study pipeline running on a single compute node. |
| Measurable Target | >= 500 records/sec/node for SDTM (DM, AE, LB, EX, CM) domain transforms |
| Traceability | Supports FR-030 (Data transformation), FR-031 (SDTM mapping) |

### TR-004: Event Bus Publish Latency
| Attribute | Value |
|-----------|-------|
| Category | Performance |
| Description | The CDOS event bus (Kafka) SHALL acknowledge published events within 100ms at the 95th percentile, including serialization and topic routing. |
| Measurable Target | p95 publish-to-ack latency < 100ms |
| Traceability | Supports FR-040 (Event-driven workflows), integration requirements |

### TR-005: End-to-End Data Ingestion Latency
| Attribute | Value |
|-----------|-------|
| Category | Performance |
| Description | Data ingested from an external system (e.g., EDC) SHALL be available in the CDOS canonical data store within 5 minutes of source system availability for batch jobs, and within 30 seconds for real-time event-driven integrations. |
| Measurable Target | Batch: < 5 min end-to-end; Real-time: < 30 sec end-to-end |
| Traceability | Supports FR-032 (EDC integration), FR-035 (Real-time sync) |

### TR-006: Database Query Performance
| Attribute | Value |
|-----------|-------|
| Category | Performance |
| Description | SQL queries for single-study dashboards SHALL execute within 3 seconds for studies with up to 10,000 subjects and 500,000 CRF pages. Vector similarity searches SHALL return results within 500ms for the top-10 matches. |
| Measurable Target | SQL queries: < 3s (10K subjects); Vector search: p95 < 500ms |
| Traceability | Supports FR-015 (Dashboard), FR-050 (AI-assisted data review) |

---

## Category: Scalability

### TR-007: Concurrent User Capacity
| Attribute | Value |
|-----------|-------|
| Category | Scalability |
| Description | The CDOS platform SHALL support at least 2,000 concurrent authenticated users across all studies without degradation below the performance targets defined in TR-001 through TR-002. |
| Measurable Target | >= 2,000 concurrent users with no SLA violation |
| Traceability | Supports FR-001, FR-010, FR-015 |

### TR-008: Study Data Volume Scalability
| Attribute | Value |
|-----------|-------|
| Category | Scalability |
| Description | The CDOS platform SHALL support up to 500 concurrent active studies, each with up to 10,000 subjects, 500,000 CRF pages, and 2,000,000 lab results, for a total of up to 2.5 billion data points across the platform. |
| Measurable Target | 500 studies x 10K subjects x 500K CRF pages; no query degradation beyond TR-006 targets |
| Traceability | Supports FR-001, FR-002 (Multi-study management) |

### TR-009: Horizontal Compute Scaling
| Attribute | Value |
|-----------|-------|
| Category | Scalability |
| Description | The CDOS compute tier SHALL scale horizontally from 3 to 50 worker nodes within 5 minutes of trigger (auto-scaling or manual). Scale-down SHALL occur within 10 minutes of load reduction. |
| Measurable Target | Scale-up: 3->50 nodes in < 5 min; Scale-down: 50->3 nodes in < 10 min |
| Traceability | Supports infrastructure requirements |

### TR-010: Storage Growth Capacity
| Attribute | Value |
|-----------|-------|
| Category | Scalability |
| Description | The storage tier SHALL support automatic expansion up to 100 TB total (SQL + vector + object) without downtime or manual intervention. Growth rate projection: ~5 TB/year at nominal usage. |
| Measurable Target | Auto-expand to 100 TB; zero downtime during expansion |
| Traceability | Supports infrastructure requirements |

### TR-011: Kafka Topic Partition Scalability
| Attribute | Value |
|-----------|-------|
| Category | Scalability |
| Description | The Kafka event bus SHALL support up to 1,000 topics and 10,000 partitions with consumer lag under 10 seconds at peak throughput of 50,000 messages per second. |
| Measurable Target | 1,000 topics, 10,000 partitions, 50K msg/sec, consumer lag < 10s |
| Traceability | Supports FR-040 (Event-driven workflows) |

---

## Category: Availability

### TR-012: Platform Uptime SLA
| Attribute | Value |
|-----------|-------|
| Category | Availability |
| Description | The CDOS platform SHALL maintain 99.9% uptime measured monthly, excluding scheduled maintenance windows. This equates to a maximum of 43.8 minutes of unplanned downtime per month. |
| Measurable Target | >= 99.9% monthly uptime (max 43.8 min unplanned downtime/month) |
| Traceability | All functional requirements |

### TR-013: Disaster Recovery RTO/RPO
| Attribute | Value |
|-----------|-------|
| Category | Availability |
| Description | The CDOS platform SHALL achieve a Recovery Time Objective (RTO) of 4 hours and a Recovery Point Objective (RPO) of 1 hour. Backups SHALL be stored in a geographically separate region (>= 100 miles). |
| Measurable Target | RTO <= 4 hours; RPO <= 1 hour; geo-redundant backups >= 100 miles |
| Traceability | Supports GxP compliance requirements |

### TR-014: Zero-Downtime Deployments
| Attribute | Value |
|-----------|-------|
| Category | Availability |
| Description | Application deployments SHALL use rolling updates with zero downtime. Canary deployments SHALL route at least 5% of traffic to new versions for a minimum of 15 minutes before full rollout. |
| Measurable Target | 0 seconds downtime during deployments; canary: >= 5% traffic for >= 15 min |
| Traceability | Supports CI/CD pipeline requirements |

---

## Category: Security

### TR-015: Authentication and Authorization
| Attribute | Value |
|-----------|-------|
| Category | Security |
| Description | The CDOS platform SHALL authenticate all users via OAuth 2.0 / OpenID Connect with multi-factor authentication (MFA) required. Token expiry SHALL be set to 15 minutes for access tokens and 8 hours for refresh tokens. Role-Based Access Control (RBAC) SHALL enforce study-level and site-level data isolation. |
| Measurable Target | MFA required for 100% of users; access token TTL = 15 min; refresh token TTL = 8 hrs; RBAC enforced on 100% of API endpoints |
| Traceability | Supports FR-005 (Access control), 21 CFR Part 11 compliance |

### TR-016: Data Encryption
| Attribute | Value |
|-----------|-------|
| Category | Security |
| Description | All data at rest SHALL be encrypted with AES-256. All data in transit SHALL be encrypted with TLS 1.3. Field-level encryption SHALL be applied to Personally Identifiable Information (PII) fields (subject name, date of birth, medical record number) using envelope encryption with per-study keys. |
| Measurable Target | AES-256 at rest; TLS 1.3 in transit; field-level encryption on all PII fields; key rotation every 90 days |
| Traceability | Supports GDPR compliance, 21 CFR Part 11 |

### TR-017: Audit Trail Completeness
| Attribute | Value |
|-----------|-------|
| Category | Security |
| Description | The CDOS platform SHALL maintain an immutable, append-only audit trail for every data modification on every entity. Audit records SHALL capture: user identity, timestamp (UTC), entity, field, old value, new value, and reason for change. Audit records SHALL be retained for a minimum of 15 years. |
| Measurable Target | 100% of write operations audited; immutable storage; 15-year retention |
| Traceability | Supports 21 CFR Part 11, GxP compliance |

### TR-018: Vulnerability Management
| Attribute | Value |
|-----------|-------|
| Category | Security |
| Description | The CDOS platform SHALL undergo automated vulnerability scanning (SAST, DAST, SCA) on every build. Critical and high vulnerabilities SHALL be remediated within 72 hours and 14 days respectively. Penetration testing SHALL be conducted annually. |
| Measurable Target | SAST/DAST/SCA on every CI build; Critical: remediate < 72 hrs; High: remediate < 14 days; Annual pen test |
| Traceability | Supports GxP, security compliance |

### TR-019: Network Security
| Attribute | Value |
|-----------|-------|
| Category | Security |
| Description | The CDOS platform SHALL enforce network segmentation with private subnets for application and data tiers. All external access SHALL be routed through a Web Application Firewall (WAF) and API gateway with rate limiting of 1,000 requests per minute per user. |
| Measurable Target | Private subnets for app/data tiers; WAF on all external endpoints; rate limit: 1,000 req/min/user |
| Traceability | Supports infrastructure and security requirements |

---

## Summary Table

| ID | Category | Measurable Target Summary |
|----|----------|--------------------------|
| TR-001 | Performance | p50 latency < 200ms |
| TR-002 | Performance | p99 latency < 500ms (CRUD), < 2000ms (aggregation) |
| TR-003 | Performance | >= 500 records/sec/node transform throughput |
| TR-004 | Performance | p95 publish-to-ack < 100ms |
| TR-005 | Performance | Batch < 5 min, real-time < 30 sec ingestion |
| TR-006 | Performance | SQL < 3s (10K subjects), vector search p95 < 500ms |
| TR-007 | Scalability | >= 2,000 concurrent users |
| TR-008 | Scalability | 500 studies, 2.5 billion data points |
| TR-009 | Scalability | 3->50 nodes in < 5 min |
| TR-010 | Scalability | Auto-expand to 100 TB, zero downtime |
| TR-011 | Scalability | 1,000 topics, 50K msg/sec, lag < 10s |
| TR-012 | Availability | 99.9% monthly uptime |
| TR-013 | Availability | RTO <= 4 hrs, RPO <= 1 hr |
| TR-014 | Availability | Zero-downtime deployments |
| TR-015 | Security | OAuth2/OIDC + MFA, 15-min access tokens, RBAC |
| TR-016 | Security | AES-256 at rest, TLS 1.3 in transit, field-level PII encryption |
| TR-017 | Security | 100% audit coverage, immutable, 15-year retention |
| TR-018 | Security | SAST/DAST/SCA per build, critical < 72 hrs |
| TR-019 | Security | Private subnets, WAF, rate limit 1,000 req/min/user |
