# CDOS Cost Model

## Overview

This document provides a comprehensive cost analysis for the Clinical Development Operating System (CDOS), including build vs. buy analysis, 3-year total cost of ownership (TCO), return on investment (ROI) calculation, and staffing model. All figures are in USD.

---

## 1. Build vs. Buy Analysis

### 1.1 Option A: Build CDOS (Custom Platform)

**Assumptions:**
- 24-month development timeline (per roadmap.md)
- Average fully-loaded engineer cost: $185,000/year (salary + benefits + overhead)
- Cloud infrastructure costs based on AWS/GCP pricing (2024 rates)
- Open-source tools used where possible (PostgreSQL, Kafka, Kubernetes, etc.)
- Commercial licenses for clinical-specific tools (Pinnacle 21, SAS)

| Category | Year 1 | Year 2 | Year 3 | 3-Year Total |
|----------|--------|--------|--------|--------------|
| **Engineering Staff** (see Section 4) | $1,850,000 | $2,220,000 | $1,480,000 | $5,550,000 |
| **Cloud Infrastructure** | $180,000 | $240,000 | $300,000 | $720,000 |
| **Software Licenses** | $350,000 | $350,000 | $350,000 | $1,050,000 |
| **Professional Services** | $200,000 | $100,000 | $50,000 | $350,000 |
| **Training & Change Management** | $75,000 | $50,000 | $25,000 | $150,000 |
| **Compliance & Validation** | $150,000 | $100,000 | $75,000 | $325,000 |
| **Contingency (15%)** | $420,750 | $462,000 | $342,000 | $1,224,750 |
| **TOTAL** | **$3,225,750** | **$3,522,000** | **$2,622,000** | **$9,369,750** |

### 1.2 Option Buy: Commercial Clinical Platform Suite

**Assumptions:**
- Enterprise license for a leading clinical platform (e.g., Medidata Rave, Veeva Vault)
- Typical contract: per-study pricing + platform fee
- 10 concurrent studies at steady state
- Implementation services from vendor
- Ongoing support and maintenance

| Category | Year 1 | Year 2 | Year 3 | 3-Year Total |
|----------|--------|--------|--------|--------------|
| **Platform License** | $1,200,000 | $1,200,000 | $1,200,000 | $3,600,000 |
| **Per-Study Fees** (10 studies) | $500,000 | $750,000 | $1,000,000 | $2,250,000 |
| **Implementation Services** | $800,000 | $200,000 | $100,000 | $1,100,000 |
| **Integration Costs** (custom adapters) | $300,000 | $200,000 | $150,000 | $650,000 |
| **Support & Maintenance** (20% of license) | $240,000 | $240,000 | $240,000 | $720,000 |
| **Internal IT Staff** (3 FTE) | $555,000 | $555,000 | $555,000 | $1,665,000 |
| **Training** | $100,000 | $50,000 | $30,000 | $180,000 |
| **Contingency (10%)** | $369,500 | $419,500 | $327,500 | $1,116,500 |
| **TOTAL** | **$4,064,500** | **$3,614,500** | **$3,602,500** | **$11,281,500** |

### 1.3 Build vs. Buy Comparison

| Metric | Build (CDOS) | Buy (Commercial) | Delta |
|--------|--------------|-------------------|-------|
| 3-Year TCO | $9,369,750 | $11,281,500 | -$1,911,750 (17% savings) |
| Time to First Value | 6 months | 3 months | +3 months |
| Customization Control | Full | Limited by vendor | Build advantage |
| Vendor Lock-in | None | High | Build advantage |
| Maintenance Burden | Internal team | Vendor-supported | Buy advantage |
| Scalability (per-study marginal cost) | $5,000/study | $100,000/study | Build advantage at scale |
| Regulatory Validation | Internal responsibility | Vendor-provided | Buy advantage |

**Recommendation:** Build CDOS for organizations with 5+ concurrent studies, strong engineering capability, and need for customization. Buy for organizations with <5 studies and preference for vendor-managed compliance.

---

## 2. Three-Year TCO Breakdown (Build Option)

### Year 1: Foundation & Development ($3,225,750)

| Item | Amount | % of Year 1 |
|------|--------|-------------|
| Engineering team (10 FTE) | $1,850,000 | 57.4% |
| Cloud infrastructure (dev/staging/prod) | $180,000 | 5.6% |
| Software licenses (Pinnacle 21, SAS, Kafka managed) | $350,000 | 10.8% |
| Professional services (architecture, compliance) | $200,000 | 6.2% |
| Training & change management | $75,000 | 2.3% |
| Compliance & validation (21 CFR Part 11, GAMP 5) | $150,000 | 4.7% |
| Contingency (15%) | $420,750 | 13.0% |

### Year 2: Expansion & Integration ($3,522,000)

| Item | Amount | % of Year 2 |
|------|--------|-------------|
| Engineering team (12 FTE, peak) | $2,220,000 | 63.0% |
| Cloud infrastructure (scaling) | $240,000 | 6.8% |
| Software licenses | $350,000 | 9.9% |
| Professional services | $100,000 | 2.8% |
| Training & change management | $50,000 | 1.4% |
| Compliance & validation | $100,000 | 2.8% |
| Contingency (15%) | $462,000 | 13.1% |

### Year 3: Scale & Optimization ($2,622,000)

| Item | Amount | % of Year 3 |
|------|--------|-------------|
| Engineering team (8 FTE, steady state) | $1,480,000 | 56.4% |
| Cloud infrastructure (production scale) | $300,000 | 11.4% |
| Software licenses | $350,000 | 13.3% |
| Professional services | $50,000 | 1.9% |
| Training & change management | $25,000 | 1.0% |
| Compliance & validation | $75,000 | 2.9% |
| Contingency (15%) | $342,000 | 13.0% |

### 3-Year TCO Summary

| Category | Year 1 | Year 2 | Year 3 | Total | % of TCO |
|----------|--------|--------|--------|-------|----------|
| Engineering Staff | $1,850,000 | $2,220,000 | $1,480,000 | $5,550,000 | 59.2% |
| Cloud Infrastructure | $180,000 | $240,000 | $300,000 | $720,000 | 7.7% |
| Software Licenses | $350,000 | $350,000 | $350,000 | $1,050,000 | 11.2% |
| Professional Services | $200,000 | $100,000 | $50,000 | $350,000 | 3.7% |
| Training | $75,000 | $50,000 | $25,000 | $150,000 | 1.6% |
| Compliance & Validation | $150,000 | $100,000 | $75,000 | $325,000 | 3.5% |
| Contingency | $420,750 | $462,000 | $342,000 | $1,224,750 | 13.1% |
| **TOTAL** | **$3,225,750** | **$3,522,000** | **$2,622,000** | **$9,369,750** | **100%** |

---

## 3. ROI Calculation

### 3.1 Methodology

ROI is calculated using the standard formula:

```
ROI = (Net Benefits - Total Investment) / Total Investment × 100%
```

Benefits are derived from quantifiable operational improvements documented in success-metrics.md. Each benefit category uses conservative estimates based on industry benchmarks.

### 3.2 Benefit Categories

#### Benefit 1: Data Reconciliation Time Reduction

**Current State:** Manual data reconciliation between EDC, CTMS, and Safety systems takes 2-4 weeks per study lock.

**Future State (CDOS):** Automated reconciliation via canonical data model reduces this to 2-4 hours.

**Calculation:**
```
Studies per year:                    10
Current reconciliation cost/study:   3 weeks × 2 FTE × $75/hr × 40 hrs = $18,000
CDOS reconciliation cost/study:      4 hours × 1 FTE × $75/hr = $300
Savings per study:                   $17,700
Annual savings:                      $17,700 × 10 = $177,000
3-year savings:                      $177,000 × 3 = $531,000
```

#### Benefit 2: Query Resolution Time Reduction

**Current State:** Average query resolution time is 14 days due to manual routing between systems.

**Future State (CDOS):** Automated query generation and routing reduces to 3 days (79% reduction).

**Calculation:**
```
Queries per study:                   500 (average)
Current cost/query:                  14 days × 0.5 hrs/day × $75/hr = $525
CDOS cost/query:                     3 days × 0.25 hrs/day × $75/hr = $56.25
Savings per query:                   $468.75
Savings per study:                   $468.75 × 500 = $234,375
Annual savings:                      $234,375 × 10 = $2,343,750
3-year savings:                      $2,343,750 × 3 = $7,031,250
```

#### Benefit 3: SDTM/ADaM Generation Time Reduction

**Current State:** SDTM and ADaM dataset generation takes 6-8 weeks of programming per study.

**Future State (CDOS):** Automated transformation pipeline reduces to 1 week (87% reduction).

**Calculation:**
```
Studies per year:                    10
Current cost/study:                  7 weeks × 1 FTE × $85/hr × 40 hrs = $23,800
CDOS cost/study:                     1 week × 0.5 FTE × $85/hr × 40 hrs = $1,700
Savings per study:                   $22,100
Annual savings:                      $22,100 × 10 = $221,000
3-year savings:                      $221,000 × 3 = $663,000
```

#### Benefit 4: SAE Reporting Time Reduction

**Current State:** SAE processing from report to safety database takes 5-7 days.

**Future State (CDOS):** Automated SAE routing reduces to < 24 hours (80% reduction).

**Calculation:**
```
SAEs per study:                      20 (average)
Current cost/SAE:                    6 days × 2 hrs/day × $90/hr = $1,080
CDOS cost/SAE:                       1 day × 0.5 hrs/day × $90/hr = $45
Savings per SAE:                     $1,035
Savings per study:                   $1,035 × 20 = $20,700
Annual savings:                      $20,700 × 10 = $207,000
3-year savings:                      $207,000 × 3 = $621,000
```

#### Benefit 5: Regulatory Submission Preparation

**Current State:** eCTD assembly and submission preparation takes 4-6 weeks per submission.

**Future State (CDOS):** Automated eCTD assembly reduces to 1 week (80% reduction).

**Calculation:**
```
Submissions per year:                3 (NDA/BLA level)
Current cost/submission:             5 weeks × 2 FTE × $95/hr × 40 hrs = $38,000
CDOS cost/submission:                1 week × 1 FTE × $95/hr × 40 hrs = $3,800
Savings per submission:              $34,200
Annual savings:                      $34,200 × 3 = $102,600
3-year savings:                      $102,600 × 3 = $307,800
```

#### Benefit 6: Reduced Data Management Overhead

**Current State:** Manual data management tasks (reconciliation, coding, listing review) require 5 FTE per study.

**Future State (CDOS):** Automation reduces to 2 FTE per study (60% reduction).

**Calculation:**
```
Studies per year:                    10
Current FTE/study:                   5 FTE × $150,000/year = $750,000
CDOS FTE/study:                      2 FTE × $150,000/year = $300,000
Savings per study:                   $450,000
Annual savings:                      $450,000 × 10 = $4,500,000
3-year savings:                      $4,500,000 × 3 = $13,500,000
```

**Note:** This benefit assumes staff redeployment to higher-value activities, not headcount reduction.

### 3.3 ROI Summary

| Benefit Category | Annual Savings | 3-Year Savings |
|------------------|----------------|----------------|
| Data Reconciliation | $177,000 | $531,000 |
| Query Resolution | $2,343,750 | $7,031,250 |
| SDTM/ADaM Generation | $221,000 | $663,000 |
| SAE Reporting | $207,000 | $621,000 |
| Regulatory Submission | $102,600 | $307,800 |
| Data Management Overhead | $4,500,000 | $13,500,000 |
| **TOTAL BENEFITS** | **$7,551,350** | **$22,654,050** |

```
3-Year Investment (TCO):           $9,369,750
3-Year Total Benefits:             $22,654,050
Net Benefit:                       $22,654,050 - $9,369,750 = $13,284,300

ROI = ($13,284,300 / $9,369,750) × 100% = 141.8%

Payback Period = $9,369,750 / $7,551,350 per year = 1.24 years (≈ 15 months)
```

### 3.4 Sensitivity Analysis

| Scenario | 3-Year TCO | 3-Year Benefits | ROI | Payback |
|----------|------------|-----------------|-----|---------|
| **Base Case** | $9,369,750 | $22,654,050 | 141.8% | 15 months |
| **Conservative** (50% of projected benefits) | $9,369,750 | $11,327,025 | 20.9% | 30 months |
| **Optimistic** (150% of projected benefits) | $9,369,750 | $33,981,075 | 262.7% | 10 months |
| **High Cost** (130% of TCO) | $12,180,675 | $22,654,050 | 86.0% | 19 months |
| **Low Study Volume** (5 studies) | $9,369,750 | $11,327,025 | 20.9% | 30 months |

**Break-even point:** CDOS investment is recovered with as few as 3 concurrent studies.

---

## 4. Staffing Model

### 4.1 Team Structure by Phase

#### Phase 1: Foundation (Months 1-6) — 10 FTE

| Role | FTE | Responsibilities |
|------|-----|------------------|
| Engineering Manager | 1 | Team leadership, sprint planning, stakeholder communication |
| Senior Backend Engineer | 2 | Canonical data store, transformation pipeline, API layer |
| Senior Integration Engineer | 2 | EDC adapter, event bus, Kafka configuration |
| Platform Engineer | 2 | Kubernetes, Terraform, CI/CD, infrastructure |
| Data Engineer | 1 | CDISC mapping service, controlled terminology, schemas |
| Compliance Engineer | 1 | 21 CFR Part 11 audit trail, IAM, encryption |
| QA Engineer | 1 | Test automation, CDISC validation, integration testing |

#### Phase 2: Core Integrations (Months 7-12) — 12 FTE

| Role | FTE | Change |
|------|-----|--------|
| Engineering Manager | 1 | — |
| Senior Backend Engineer | 2 | — |
| Senior Integration Engineer | 3 | +1 (Safety, LIMS, IWRS adapters) |
| Platform Engineer | 2 | — |
| Data Engineer | 2 | +1 (ADaM pipeline, risk models) |
| Compliance Engineer | 1 | — |
| QA Engineer | 1 | — |

#### Phase 3: Advanced (Months 13-18) — 10 FTE

| Role | FTE | Change |
|------|-----|--------|
| Engineering Manager | 1 | — |
| Senior Backend Engineer | 2 | — |
| Senior Integration Engineer | 2 | -1 (stabilization) |
| Platform Engineer | 1 | -1 (infrastructure stable) |
| Data Engineer | 2 | — |
| Compliance Engineer | 1 | — |
| QA Engineer | 1 | — |

#### Phase 4: Scale (Months 19-24) — 8 FTE

| Role | FTE | Change |
|------|-----|--------|
| Engineering Manager | 1 | — |
| Senior Backend Engineer | 2 | — |
| Senior Integration Engineer | 1 | -1 (maintenance mode) |
| Platform Engineer | 1 | — |
| Data Engineer | 1 | -1 (pipeline stable) |
| QA Engineer | 1 | — |
| Technical Writer | 1 | +1 (documentation) |

### 4.2 Staffing Cost Summary

| Period | FTE | Monthly Cost | Period Cost |
|--------|-----|--------------|-------------|
| Phase 1 (6 months) | 10 | $154,167 | $925,000 |
| Phase 2 (6 months) | 12 | $185,000 | $1,110,000 |
| Phase 3 (6 months) | 10 | $154,167 | $925,000 |
| Phase 4 (6 months) | 8 | $123,333 | $740,000 |
| **Year 1 Total** | — | — | **$1,850,000** |
| **Year 2 Total** | — | — | **$2,220,000** |
| **Year 3 Total** | — | — | **$1,480,000** |
| **3-Year Total** | — | — | **$5,550,000** |

**Assumptions:**
- Average fully-loaded cost: $185,000/year per FTE (salary + benefits + overhead)
- Senior roles at $200,000-$220,000, junior roles at $140,000-$160,000
- No contractor premium included (assumes FTE hires)
- 15% annual salary inflation applied in Year 2-3 projections

---

## 5. Software License Breakdown

| Tool | Annual Cost | Category |
|------|-------------|----------|
| Pinnacle 21 Enterprise | $150,000 | CDISC Validation |
| SAS Foundation | $100,000 | Statistical Computing |
| Confluent Cloud (managed Kafka) | $60,000 | Event Bus |
| HashiCorp Vault Enterprise | $25,000 | Secrets Management |
| Grafana Cloud | $15,000 | Monitoring |
| **Total Annual Licenses** | **$350,000** | — |

**Note:** All other tools are open-source (PostgreSQL, Kubernetes, Redis, Keycloak, Airflow, Camunda, NiFi, Terraform, OpenTelemetry).

---

## 6. Cloud Infrastructure Breakdown

| Component | Year 1 | Year 2 | Year 3 |
|-----------|--------|--------|--------|
| Kubernetes (EKS/GKE) | $48,000 | $72,000 | $96,000 |
| PostgreSQL (RDS/Cloud SQL) | $36,000 | $48,000 | $60,000 |
| Object Storage (S3/GCS) | $12,000 | $18,000 | $24,000 |
| Networking & CDN | $18,000 | $24,000 | $30,000 |
| Monitoring & Logging | $12,000 | $18,000 | $24,000 |
| Backup & DR | $24,000 | $30,000 | $36,000 |
| Development & Staging Environments | $30,000 | $30,000 | $30,000 |
| **Total** | **$180,000** | **$240,000** | **$300,000** |

---

## Cross-References

- Success metrics driving ROI: [Success Metrics](success-metrics.md)
- Roadmap phases: [Implementation Roadmap](roadmap.md)
- Architecture (infrastructure components): [Module 01](../01-architecture/overview.md)
- Technology stack (tools referenced): [Module 01](../01-architecture/technology-stack.md)
- Compliance requirements: [Module 07](../07-compliance/21-cfr-part-11.md)
