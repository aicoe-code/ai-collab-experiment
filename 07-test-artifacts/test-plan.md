# CDOS Master Test Plan

| Document ID | CDOS-TP-001 |
|-------------|-------------|
| Version | 1.0 |
| Date | 2026-05-29 |
| Status | Draft |
| Author | Agent-Tests |

---

## 1. Purpose

This document defines the test strategy, scope, approach, and entry/exit criteria for the Clinical Data Orchestration System (CDOS). It covers all test types required to validate functional requirements (FR-001 through FR-035), technical requirements (TR-001 through TR-019), and regulatory compliance (21 CFR Part 11, GDPR, GxP).

---

## 2. Scope

### 2.1 In Scope

- **Unit Tests**: Core business services, data models, validation rules, transform rules, query services
- **Integration Tests**: External system adapters (EDC, CTMS, LIMS, Safety, IWRS, eTMF, RegSubmit)
- **End-to-End Tests**: Full business processes (enrollment, safety reporting, submission assembly)
- **Performance/Load Tests**: API latency, throughput, concurrent users, data volume scalability
- **Validation Tests**: 21 CFR Part 11, GDPR, GxP compliance verification

### 2.2 Out of Scope

- Third-party vendor system testing (handled by vendor)
- Infrastructure provider SLAs (AWS/Azure responsibility)
- User acceptance testing (UAT) by clinical operations staff

---

## 3. Test Strategy

### 3.1 Test Pyramid

```
            ┌───────────┐
            │    E2E     │  ~5%  (3 files, critical flows)
           ┌┴───────────┴┐
           │ Integration  │  ~15% (3 files, adapter tests)
          ┌┴─────────────┴┐
          │   Unit Tests   │  ~80% (5 files, comprehensive)
          └───────────────┘
```

### 3.2 Approach

| Test Type | Framework | Runner | Environment |
|-----------|-----------|--------|-------------|
| Unit | pytest + unittest.mock | pytest -v | Local / CI |
| Integration | pytest + testcontainers | pytest -v --integration | Staging |
| E2E | pytest + httpx | pytest -v --e2e | Staging |
| Performance | Locust / k6 | locustfile.py | Performance env |
| Validation | pytest + compliance fixtures | pytest -v --validation | Staging |

---

## 4. Entry Criteria

- [ ] All functional requirements (FR-001 through FR-035) are baselined
- [ ] Technical design artifacts (04-technical-design/) are approved
- [ ] Data models (05-data-models/) are finalized
- [ ] API specifications (06-api-specifications/) are published
- [ ] Test environment (staging) is provisioned and accessible
- [ ] All Python code in 08-software/ passes syntax validation

---

## 5. Exit Criteria

- [ ] 100% of unit tests pass (≥3 tests per file, ≥5 files)
- [ ] 100% of integration tests pass (≥2 tests per file, ≥3 files)
- [ ] 100% of E2E tests pass (≥2 tests per file, ≥3 files)
- [ ] Performance targets met: p50 < 200ms, p99 < 500ms (TR-001, TR-002)
- [ ] All 21 CFR Part 11 validation tests pass
- [ ] All GDPR compliance validation tests pass
- [ ] Every test traces to ≥1 FR or NFR (07-G criterion)
- [ ] Code coverage ≥ 80% for services/core/ and shared/models/

---

## 6. Test Types Detail

### 6.1 Unit Tests (unit-tests/)

| File | Scope | FR/NFR Coverage |
|------|-------|-----------------|
| test_study_service.py | Study CRUD, versioning, milestone tracking | FR-001, FR-002, FR-004 |
| test_subject_model.py | Subject model validation, status transitions | FR-006, FR-007, FR-008 |
| test_adverse_event_validation.py | AE severity, seriousness, causality rules | FR-020, FR-021, FR-022 |
| test_transform_rules.py | SDTM mapping, CDISC transform rules | FR-030, TR-003 |
| test_query_service.py | Query lifecycle, auto-generation, resolution | FR-012, FR-013 |

### 6.2 Integration Tests (integration-tests/)

| File | Scope | FR/NFR Coverage |
|------|-------|-----------------|
| test_edc_adapter.py | EDC CRF ingestion, query sync | FR-011, FR-012, FR-013 |
| test_safety_adapter.py | AE case intake, SAE expedited reporting | FR-020, FR-021 |
| test_lims_adapter.py | Lab result ingestion, sample CoC | FR-017, FR-018, FR-019 |

### 6.3 End-to-End Tests (e2e-tests/)

| File | Scope | FR/NFR Coverage |
|------|-------|-----------------|
| test_enrollment_flow.py | Full screening → eligibility → enrollment → randomization | FR-006 through FR-010, FR-023 |
| test_safety_reporting_flow.py | AE detection → SAE reporting → signal aggregation | FR-020, FR-021, FR-022 |
| test_submission_assembly_flow.py | SDTM mapping → eCTD assembly → submission | FR-030, FR-033 |

### 6.4 Performance Tests (performance-tests/)

| File | Scope | NFR Coverage |
|------|-------|--------------|
| load-test-spec.md | TPS, latency, concurrent users, data volume | TR-001 through TR-011 |

### 6.5 Validation Tests (validation-tests/)

| File | Scope | FR/NFR Coverage |
|------|-------|-----------------|
| test_21cfr_part11.py | Audit trail, e-signature, access control | FR-026, FR-027, FR-028, TR-015, TR-017 |
| test_gdpr_compliance.py | Data minimization, pseudonymization, erasure | TR-016, GDPR Art. 5, 17, 25 |

---

## 7. Test Environment

| Environment | Purpose | Provisioned By |
|-------------|---------|----------------|
| Local (dev) | Unit tests | Developer workstation |
| CI/CD | Unit + integration | GitHub Actions |
| Staging | Integration + E2E + validation | Terraform (08-software/infrastructure/terraform/) |
| Performance | Load testing | Dedicated perf cluster (K8s) |

### 7.1 Test Data

- Synthetic subject data (fictitious PII, HIPAA-safe)
- Controlled terminology seeds from 05-data-models/seed-data/
- Mock EDC/LIMS/Safety responses for integration tests

---

## 8. Traceability

Every test method references at least one FR or NFR ID using the format:

```
"""Tests: FR-015 — CTMS monitoring visit report ingestion."""
```

The full traceability matrix is maintained in 09-sdlc-traceability/requirements-traceability.md.

---

## 9. Risk-Based Prioritization

| Priority | Test Areas | Rationale |
|----------|-----------|-----------|
| Critical | Subject enrollment, AE/SAE reporting, audit trail | Patient safety, regulatory compliance |
| High | EDC integration, SDTM mapping, e-signature | Data integrity, submission readiness |
| Medium | Query management, CTMS sync, dashboards | Operational efficiency |
| Low | UI formatting, report aesthetics | User experience |
