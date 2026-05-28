# Trial Design: Parallel Group

## Overview

A parallel-group design assigns each [Entity:Subject] to exactly one arm for the duration of the study. Arms receive different treatments (or placebo), and outcomes are compared between independent groups. This is the most common confirmatory trial design used in Phase 2/3.

| Attribute | Value |
|-----------|-------|
| Design Type | Parallel Group |
| Typical Phase | Phase 2, Phase 3 |
| Randomization | 1:1 or 1:1:1 (balanced blocks or minimization) |
| Blinding | Single-blind, double-blind, or open-label |
| Primary Analysis | Between-group comparison at endpoint |

---

## Arms and Stratification

Each parallel-group study defines a set of treatment arms. Arms are assigned at randomization time via [System:IWRS] and recorded in the Subject entity.

### Arm Definition

| Field | Type | Description |
|-------|------|-------------|
| arm_id | UUID | Unique arm identifier |
| study_id | UUID | FK → [Entity:Study] |
| arm_code | String(20) | Short code (e.g., ARM-A, ARM-B, PLACEBO) |
| arm_label | String(200) | Descriptive label |
| arm_type | Enum(EXPERIMENTAL, ACTIVE_COMPARATOR, PLACEBO, SHAM, USUAL_CARE) | Type of arm |
| treatment_description | String(1000) | Full treatment description |
| target_allocation_ratio | Float | Planned allocation ratio (e.g., 1.0 for equal) |

### Stratification Factors

| Field | Type | Description |
|-------|------|-------------|
| stratification_factor_id | UUID | Unique factor identifier |
| study_id | UUID | FK → [Entity:Study] |
| factor_name | String(100) | Factor name (e.g., Disease Stage, Region) |
| factor_values | Array[String] | Possible strata values |
| dynamic | Boolean | Whether factor changes during trial |

---

## Data Model Changes

### Modified Entities

#### Subject — Add Arm Assignment Fields

The existing [Entity:Subject] entity requires the following additional attributes:

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| arm_id | UUID | FK → Arm | Assigned treatment arm |
| stratification_factors | Object | — | Map of factor_name → factor_value at randomization |
| randomization_date | Date | — | Date of randomization |
| randomization_number | String(50) | — | Randomization number assigned by IWRS |
| treatment_start_date | Date | — | Date first dose received |
| treatment_end_date | Date | — | Date last dose received or discontinuation |

#### Study — Add Design Configuration

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| design_type | Enum(PARALLEL, ADAPTIVE, PLATFORM, CROSSOVER, OBSERVATIONAL) | NOT NULL | Study design type |
| number_of_arms | Integer | > 1 | Number of treatment arms |
| blinding | Enum(OPEN, SINGLE_BLIND, DOUBLE_BLIND) | NOT NULL | Blinding status |
| randomization_method | Enum(SIMPLE, BLOCK, STRATIFIED, MINIMIZATION) | — | Randomization method |

### New Entities

#### Arm (defined above)

#### StratificationFactor (defined above)

---

## CDISC Mapping (Subject Additions)

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| arm_id | ARMCD | DM | Record Qualifier | CDISC CT: ARMCD |
| randomization_date | RFXSTDTC | DM | Timing | — |
| randomization_number | — | — | — | — |
| treatment_start_date | RFXSTDTC | DM | Timing | — |
| treatment_end_date | RFXENDTC | DM | Timing | — |

---

## Transform Changes

### Modified Transforms

#### [Transform:Protocol→EDC]

Add derivation rules for arm configuration from the protocol:

```
RULE-PG-001: IF protocol.primary_endpoints NOT EMPTY
             THEN derive arm definitions from protocol.study_design section

RULE-PG-002: IF study.blinding = "DOUBLE_BLIND"
             THEN EDC CRF must include treatment code field (hidden from unblinded users)
```

#### [Transform:EDC→SDTM]

Add DM domain derivations for arm assignment:

```
RULE-PG-003: MAPPING subject.arm_id → DM.ARMCD, DM.ARM
RULE-PG-004: MAPPING subject.stratification_factors → DM.STRATn (SDTM stratification variables)
RULE-PG-005: IF subject.arm_id IS NULL AND subject.status = "ENROLLED"
             THEN REJECT with error "arm_required_for_enrolled_subject"
```

#### [Transform:SDTM→ADaM]

Add ADSL population and analysis derivations:

```
RULE-PG-006: DERIVE ADSL.SAFFL (Safety Population) = "Y" IF subject.treatment_start_date IS NOT NULL
RULE-PG-007: DERIVE ADSL.EFFFL (Efficacy Population) = "Y" IF subject meets protocol-defined criteria
RULE-PG-008: DERIVE ADSL.TRT01P (Planned Treatment) FROM subject.arm_id
RULE-PG-009: DERIVE ADSL.TRT01A (Actual Treatment) FROM Dose records
```

### New Transforms

#### Transform: IWRS Randomization → Subject Arm Assignment

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| iwrs.subject_id | subject.subject_id | none | link by subject identifier |
| iwrs.arm_code | subject.arm_id | String → UUID | resolve arm_id by arm_code |
| iwrs.randomization_number | subject.randomization_number | none | direct copy |
| iwrs.stratum | subject.stratification_factors | JSON → Object | parse stratum assignment |
| iwrs.timestamp | subject.randomization_date | DateTime → Date | date only |

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-PG-001 | subject.arm_id NOT NULL for all ENROLLED subjects | QUARANTINE |
| VAL-PG-002 | subject.arm_id IN (SELECT arm_id FROM Arm WHERE study_id = subject.study_id) | REJECT |
| VAL-PG-003 | Randomization date ≤ first treatment date | QUARANTINE |
| VAL-PG-004 | Target allocation not exceeded by >5% across strata | ALERT |

---

## Business Rules

```
RULE-PG-001: IF study.design_type = "PARALLEL" AND study.number_of_arms < 2
             THEN REJECT with error "parallel_requires_at_least_2_arms"

RULE-PG-002: IF subject.status changes to "WITHDRAWN"
             THEN trigger_follow_up_scheduling(subject, reason = "premature_discontinuation")

RULE-PG-003: PER blocking method: IF completed_enrollment_per_block = block_size
             THEN trigger_randomization_balance_check(study)

RULE-PG-004: IF imbalance_ratio > 1.25 in any stratum
             THEN ALERT to IWRS, trigger review by unblinded statistician
```

---

## Endpoints and Analysis Population

| Population | Definition | CDISC Flag |
|-----------|------------|-----------|
| ITT (Intent-to-Treat) | All randomized subjects | ITTFL |
| mITT (Modified ITT) | All randomized subjects with ≥1 post-baseline efficacy assessment | MITTFL |
| Per-Protocol | mITT subjects with no major protocol deviations | PPROTFL |
| Safety | All subjects who received ≥1 dose of study treatment | SAFFL |

---

## System Integration

| System | Integration Point | Description |
|--------|------------------|-------------|
| [System:IWRS] | Randomization | Assigns treatment arm, stratification stratum |
| [System:EDC] | Data Capture | Records arm assignment, stratification factors |
| [System:eCOA] | Outcomes | Collects efficacy endpoints by visit schedule |

---

## SDTM Datasets Affected

| Dataset | Key Variables Added |
|---------|-------------------|
| DM | ARMCD, ARM, ACTARM, ACTARMCD, STRATn |
| TA | Planned arm-visit-epoch assignments |
| TE | Treatment epoch definitions |
| TV | Visit-level treatment assignments |
