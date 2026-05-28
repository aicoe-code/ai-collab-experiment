# Trial Design: Crossover Design

## Overview

A crossover design allows each [Entity:Subject] to receive multiple treatments in a pre-specified sequence, serving as their own control. This reduces inter-subject variability and typically requires fewer subjects than a parallel-group design. The most common form is the 2×2 crossover (two treatments, two periods), but higher-order designs exist.

| Attribute | Value |
|-----------|-------|
| Design Type | Crossover |
| Typical Phase | Phase 1 (PK studies), Phase 2 (chronic stable conditions) |
| Key Feature | Each subject receives all treatments |
| Suitable Conditions | Stable/chronic diseases, no carryover effect |
| Statistical Model | Mixed-effects model with subject as random effect |

---

## Sequence and Period Structure

A crossover trial defines treatment sequences (the order in which treatments are administered) and periods (the time blocks during which each treatment is given).

### Sequence Entity

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| sequence_id | UUID | PK, NOT NULL | Unique sequence identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Study context |
| sequence_code | String(20) | NOT NULL | Sequence code (e.g., AB, BA, ABC, BCA) |
| sequence_label | String(200) | NOT NULL | Descriptive label (e.g., "Treatment A then Treatment B") |
| treatment_order | Array[String] | NOT NULL | Ordered list of arm_codes (e.g., ["A", "B"]) |
| number_of_periods | Integer | NOT, NULL | Number of periods in this sequence |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

### Period Entity

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| period_id | UUID | PK, NOT NULL | Unique period identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Study context |
| sequence_id | UUID | FK → Sequence, NOT NULL | Sequence this period belongs to |
| period_number | Integer | NOT NULL | Period ordinal (1, 2, 3, ...) |
| arm_code | String(20) | NOT NULL | Treatment administered in this period |
| arm_id | UUID | FK → Arm | Resolved arm for this period |
| washout_days | Integer | ≥ 0 | Minimum washout days before next period |
| period_duration_days | Integer | > 0 | Duration of this treatment period |
| period_start_type | Enum(FIXED_DAY, RESPONSE_BASED, EVENT_BASED) | NOT NULL | How period start is determined |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

---

## Subject Period Tracking

Each [Entity:Subject] progresses through periods based on their assigned sequence. The Visit entity and a new SubjectPeriod entity track this.

### SubjectPeriod Entity

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| subject_period_id | UUID | PK, NOT NULL | Unique subject-period identifier |
| subject_id | UUID | FK → [Entity:Subject], NOT NULL | Subject |
| period_id | UUID | FK → Period, NOT NULL | Period in sequence |
| sequence_id | UUID | FK → Sequence, NOT NULL | Assigned sequence |
| period_number | Integer | NOT NULL | Period ordinal |
| treatment_code | String(20) | NOT NULL | Treatment received in this period |
| period_start_date | Date | — | Actual start date of this period |
| period_end_date | Date | — | Actual end date of this period |
| washout_start_date | Date | — | Start of washout before this period |
| washout_end_date | Date | — | End of washout (start of treatment) |
| carryover_assessment | Enum(NONE, SUSPECTED, CONFIRMED) | DEFAULT NONE | Whether carryover was detected |
| period_status | Enum(NOT_STARTED, IN_TREATMENT, WASHOUT, COMPLETED, DISCONTINUED) | NOT NULL | Status |
| discontinuation_reason | String(500) | — | Reason for discontinuing this period |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

---

## Data Model Changes

### New Entities

#### Sequence (defined above)

#### Period (defined above)

#### SubjectPeriod (defined above)

#### CarryoverAssessment

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| carryover_id | UUID | PK, NOT NULL | Unique assessment identifier |
| subject_id | UUID | FK → [Entity:Subject], NOT NULL | Subject assessed |
| period_id | UUID | FK → Period, NOT NULL | Period assessed for carryover |
| test_name | String(200) | NOT NULL | Endpoint/parameter assessed |
| carryover_detected | Boolean | NOT NULL | Whether carryover was detected |
| evidence | String(1000) | — | Evidence of carryover (statistical test, clinical finding) |
| p_value | Float | — | p-value from carryover test (if applicable) |
| assessment_method | String(200) | NOT NULL | Method used to assess carryover |
| assessed_by | String(200) | NOT NULL | Who performed assessment |
| assessed_date | Date | NOT NULL | Date of assessment |
| impact_on_analysis | Enum(NONE, FIRST_PERIOD_ONLY, EXCLUDED) | NOT NULL | How carryover affects analysis |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

### Modified Entities

#### Subject — Add Sequence Assignment

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| sequence_id | UUID | FK → Sequence | Assigned treatment sequence |
| crossover_randomization_number | String(50) | — | Randomization number specific to sequence assignment |

#### Study — Add Crossover Configuration

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| crossover | Boolean | DEFAULT false | Whether study uses crossover design |
| crossover_type | Enum(TWO_BY_TWO, TWO_BY_THREE, THREE_BY_THREE, WILLIAMS, LATIN_SQUARE) | — | Type of crossover design |
| washout_required | Boolean | NOT NULL | Whether washout period is required |
| minimum_washout_days | Integer | ≥ 0 | Minimum washout duration |
| carryover_testing | Boolean | DEFAULT true | Whether formal carryover testing is planned |
| period_baseline_required | Boolean | DEFAULT true | Whether baseline is required at each period |

#### Visit — Add Period Context

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| subject_period_id | UUID | FK → SubjectPeriod | Period this visit belongs to |
| period_number | Integer | — | Period ordinal for this visit |
| washout_visit | Boolean | DEFAULT false | Whether this visit is during washout |

---

## CDISC Mapping

### SubjectPeriod

| CDOS Attribute | CDISC Variable | Domain | Role | Controlled Term |
|---------------|---------------|--------|------|----------------|
| subject_period_id | — | SE | Identifier | — |
| period_number | EPOCH | SE | Record Qualifier | — |
| treatment_code | TRT | SE | Record Qualifier | — |
| period_start_date | SESTDTC | SE | Timing | — |
| period_end_date | SEENDTC | SE | Timing | — |
| period_status | SESTATUS | SE | Record Qualifier | — |

### Sequence

| CDOS Attribute | CDISC Variable | Domain | Role |
|---------------|---------------|--------|------|
| sequence_code | ARMCD | DM | Record Qualifier |
| treatment_order | TA (per epoch) | TA | Sequence |

---

## Transform Changes

### Modified Transforms

#### [Transform:Protocol→EDC]

```
RULE-CO-001: IF study.crossover = true
             THEN EDC CRF must include period-level assessments
             AND each CRF page tagged with period_number AND subject_period_id

RULE-CO-002: IF study.washout_required = true
             THEN EDC must include washout tracking CRF
             AND washout compliance documented per period
```

#### [Transform:EDC→SDTM]

```
RULE-CO-003: FOR each subject_period
             TRANSFORM EDC data INTO SDTM with EPOCH = period.treatment_code
             AND SE domain records epoch transitions

RULE-CO-004: IF carryover_assessment = "CONFIRMED" AND impact_on_analysis = "EXCLUDED"
             THEN exclude subject data from period(s) AFTER carryover period
             AND include in SUPPQUAL with QNAM = "CARRYEXC"

RULE-CO-005: FOR AE, LB, CM, EX domains
             ASSIGN each record to correct period based on onset_date/collection_date
             relative to period_start_date and period_end_date
```

#### [Transform:SDTM→ADaM]

```
RULE-CO-006: ADSL must include:
             SEQCDE (assigned sequence code)
             NPER (number of periods completed)
             COMPLFL (completers flag: all periods completed without discontinuation)
             CARRYFL (carryover flag: any confirmed carryover detected)

RULE-CO-007: FOR efficacy endpoints (ADaM BDS structure)
             STRUCTURE as:
               USUBJID, PARAMCD, AVAL, AVALC, AVISIT, AVISITN,
               PERIOD (period number), TRTSEQ (treatment per sequence),
               BASE (period-specific baseline)

RULE-CO-008: IF period_baseline_required = true
             THEN derive BASE as assessment at period start (not overall study baseline)
             AND ADSL must include BASETYPE = "PERIOD" flag

RULE-CO-009: FOR treatment effect estimation
             USE mixed-effects model: AVAL = TRTSEQ + PERIOD + SEQUENCE + (1|USUBJID)
             AND output treatment effect estimate with 95% CI
```

### New Transforms

#### Transform: Period Data Assignment

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| subject.subject_id | subject_period.subject_id | none | link to subject |
| sequence.treatment_order[period_number] | subject_period.treatment_code | Array index | resolve treatment for period |
| visit.actual_date | — | — | assign to period WHERE period_start ≤ date ≤ period_end |
| ae.onset_date | — | — | assign AE to period WHERE period contains onset_date |
| lab.collection_date | — | — | assign lab to period WHERE period contains collection_date |
| dose.administration_date | — | — | assign dose to period WHERE period contains administration_date |

```
RULE-CO-010: FOR each data point (AE, Lab, Dose, CM)
             ASSIGN to subject_period WHERE period_start_date ≤ data_date ≤ period_end_date
             IF data_date during washout: assign to washout flag, not a treatment period
```

#### Transform: Carryover Detection

| Source | Target | Rule |
|--------|--------|------|
| LabResult (period n baseline) | CarryoverAssessment | Compare to period n-1 washout values |
| AdverseEvent (period n) | CarryoverAssessment | Assess if AE expected from prior-period treatment |
| Pharmacokinetic data | CarryoverAssessment | Compare to expected washout PK profile |

```
RULE-CO-011: AT period n start (after washout)
             IF LabResult.value at period n baseline deviates > 2SD from population baseline
             THEN set carryover_assessment = "SUSPECTED"

RULE-CO-012: IF carryover_detected AND carryover_impact = "EXCLUDED"
             THEN remove period n data from primary analysis
             AND include in sensitivity analysis
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-CO-001 | Subject assigned to exactly one sequence | REJECT |
| VAL-CO-002 | Sequence treatment_order length = period count | REJECT |
| VAL-CO-003 | Washout duration ≥ study.minimum_washout_days | QUARANTINE |
| VAL-CO-004 | Period start date > previous period end date | REJECT |
| VAL-CO-005 | All periods in sequence completed for completer analysis | ALERT (if incomplete) |
| VAL-CO-006 | Carryover test performed at each period transition (if carryover_testing = true) | ALERT |

---

## Business Rules

```
RULE-CO-013: IF subject discontinues in period n
             THEN mark periods > n as "NOT_STARTED"
             AND include subject in period 1 through n analysis only
             AND set COMPLFL = "N"

RULE-CO-014: IF washout compliance < 80% (washout days < minimum)
             THEN QUARANTINE subject data for this period
             AND flag for sensitivity analysis exclusion

RULE-CO-015: IF period_baseline_required = true
             AND period n baseline missing
             THEN ALERT: baseline missing for period n
             AND allow enrollment continuation but flag for analysis

RULE-CO-016: FOR 2×2 crossover design
             RANDOMIZE subjects to sequence AB or BA with 1:1 allocation
             AND balance sequences within each site
```

---

## System Integration

| System | Integration Point | Description |
|--------|------------------|-------------|
| [System:IWRS] | Sequence randomization | Assigns treatment sequence (not individual arm) |
| [System:EDC] | Period-aware CRFs | CRFs tagged with period; period transitions tracked |
| [System:LIMS] | Period-tagged results | Lab results assigned to period for carryover analysis |
| [System:eCOA] | Period endpoints | Subject-reported outcomes collected per period |
| [System:Safety] | Period-specific AEs | AEs assigned to treatment period for causality assessment |

---

## SDTM Datasets Affected

| Dataset | Impact |
|---------|--------|
| DM | SEQCDE (sequence code) in ARMCD/ARM |
| SE | Subject-level epoch records (period transitions) |
| TA | Treatment epoch assignments per sequence |
| TE | Period/epoch definitions |
| AE | AE records tagged with EPOCH = treatment period |
| LB | Lab records tagged with period; period-specific baselines |
| EX | Exposure records per treatment period |
| TS | Trial summary: crossover design parameters |
