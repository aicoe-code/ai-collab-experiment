# Trial Design: Platform Trial

## Overview

A platform trial evaluates multiple interventions against a common control within a single master protocol. Arms can be added or dropped over time without stopping the trial. Subjects are randomized to the current set of available arms using Bayesian response-adaptive randomization or equal allocation. Platform trials are increasingly common in oncology (e.g., I-SPY2, GBM AGILE) and infectious disease (e.g., RECOVERY, SOLIDARITY).

| Attribute | Value |
|-----------|-------|
| Design Type | Platform (Master Protocol) |
| Typical Phase | Phase 2/3 seamless |
| Key Feature | Multiple arms, shared control, arm addition/removal over time |
| Regulatory Basis | FDA Guidance on Master Protocols (2022); ICH E20 |
| Statistical Framework | Bayesian hierarchical model or frequentist with family-wise error rate control |

---

## Arm Lifecycle Management

Unlike parallel-group trials, platform trials manage arms dynamically. Arms move through a lifecycle:

```
                    ┌────────────┐
     ┌──────────────│  PENDING   │
     │              └─────┬──────┘
     │                    │ activation trigger
     │              ┌─────▼──────┐
     │              │  ACTIVE    │◄────── re-activation
     │              └─────┬──────┘
     │                    │ graduation/futility/safety
     │         ┌──────────┼──────────┐
     │   ┌─────▼──────┐  │  ┌───────▼──────┐
     │   │ GRADUATED  │  │  │  SUSPENDED   │
     │   └────────────┘  │  └──────────────┘
     │                   │
     │              ┌────▼───────┐
     └──────────────│  CLOSED    │
                    └────────────┘
```

### Arm Entity (Platform Extension)

The Arm entity defined in [parallel-group.md](./parallel-group.md) is extended with lifecycle attributes:

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| arm_id | UUID | PK, NOT NULL | Unique arm identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Platform study |
| arm_code | String(20) | NOT NULL | Short code |
| arm_label | String(200) | NOT NULL | Descriptive label |
| arm_type | Enum(EXPERIMENTAL, ACTIVE_COMPARATOR, CONTROL, SHAM) | NOT NULL | Arm type |
| control_type | Enum(SHARED_CONCURRENT, SHARED_HISTORICAL, EXTERNAL, NONE) | — | Whether arm serves as control |
| lifecycle_status | Enum(PENDING, ACTIVE, SUSPENDED, GRADUATED, CLOSED) | NOT NULL | Current lifecycle state |
| activation_date | Date | — | Date arm became active |
| closure_date | Date | — | Date arm was closed |
| closure_reason | Enum(FUTILITY, GRADUATION, SAFETY, SPONSOR_DECISION, REGULATORY, OTHER) | — | Reason for closure |
| eligibility_amendment | String(50) | — | Protocol amendment version controlling enrollment to this arm |
| treatment_description | String(1000) | NOT NULL | Full treatment description |
| moa | String(200) | — | Mechanism of action |
| bayesian_prior | JSON | — | Prior distribution parameters for Bayesian analysis |
| current_allocation_ratio | Float | NOT NULL, DEFAULT 1.0 | Current randomization allocation ratio |
| cumulative_n_randomized | Integer | DEFAULT 0 | Total subjects randomized to this arm |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

---

## Data Model Changes

### New Entities

#### SubStudy (Platform-Specific)

Each arm or arm-comparison within the platform may operate as a sub-study with its own analysis plan:

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| sub_study_id | UUID | PK, NOT NULL | Unique sub-study identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Parent platform study |
| arm_id | UUID | FK → Arm | Experimental arm in this comparison |
| control_arm_id | UUID | FK → Arm | Control arm for comparison |
| sub_study_name | String(200) | NOT NULL | Descriptive name |
| primary_endpoint | String(500) | NOT NULL | Primary endpoint for this comparison |
| sample_size | Integer | — | Planned sample size for this comparison |
| analysis_method | String(200) | NOT NULL | Statistical method (e.g., Bayesian logistic regression) |
| futility_boundary | JSON | — | Pre-specified futility boundary |
| graduation_boundary | JSON | — | Pre-specified graduation threshold |
| status | Enum(PLANNING, ENROLLING, ANALYZING, COMPLETED) | NOT NULL | Sub-study status |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

#### PlatformEvent

Logs all arm lifecycle events for audit and regulatory submission:

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| event_id | UUID | PK, NOT NULL | Unique event identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Platform study |
| arm_id | UUID | FK → Arm | Arm involved |
| event_type | Enum(ARM_ACTIVATED, ARM_SUSPENDED, ARM_CLOSED, ARM_GRADUATED, ARM_ADDED, ALLOCATION_UPDATED, ELIGIBILITY_AMENDED) | NOT NULL | Event type |
| event_timestamp | DateTime | NOT NULL | When the event occurred |
| triggered_by | String(200) | NOT NULL | Who/what triggered the event |
| reason | String(1000) | — | Reason for the event |
| previous_state | String(100) | — | State before event |
| new_state | String(100) | — | State after event |
| regulatory_notification | Boolean | DEFAULT false | Whether authority was notified |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

#### RandomizationTable (Platform-Specific)

Tracks real-time randomization with dynamic allocation:

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| randomization_id | UUID | PK, NOT NULL | Unique randomization record |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Platform study |
| subject_id | UUID | FK → [Entity:Subject], NOT NULL | Subject randomized |
| arm_id | UUID | FK → Arm, NOT NULL | Assigned arm |
| randomization_number | String(50) | NOT NULL | Unique randomization number |
| stratum | String(100) | — | Stratification stratum |
| allocation_method | Enum(EQUAL, BAYESIAN_RAR, THOMPSON_SAMPLING, MINIMIZATION) | NOT NULL | Method used for allocation |
| allocation_probabilities | JSON | — | Arm allocation probabilities at time of randomization |
| active_arms_at_assignment | Array[String] | NOT NULL | Arms available at time of assignment |
| randomization_timestamp | DateTime | NOT NULL | When randomization occurred |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

### Modified Entities

#### Study — Add Platform Configuration

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| platform | Boolean | DEFAULT false | Whether this is a platform trial |
| master_protocol_version | String(20) | — | Current master protocol version |
| arm_management_method | Enum(STEERING_COMMITTEE, IDMC, BAYESIAN_AUTOMATIC) | NOT NULL | Who decides arm additions/removals |
| shared_control | Boolean | DEFAULT true | Whether a shared control arm is used |
| concurrent_control | Boolean | DEFAULT true | Whether control is concurrent vs. historical |
| bayesian_rar | Boolean | DEFAULT false | Whether Bayesian response-adaptive randomization is used |
| minimum_arms | Integer | DEFAULT 2 | Minimum active arms (including control) |
| maximum_arms | Integer | DEFAULT 10 | Maximum concurrent experimental arms |

#### Subject — Add Platform-Specific Fields

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| sub_study_id | UUID | FK → SubStudy | Sub-study this subject belongs to |
| available_arms_at_screening | Array[String] | — | Arms available when subject was screened |
| eligibility_version | String(50) | — | Eligibility criteria version applied |

---

## Transform Changes

### Modified Transforms

#### [Transform:Protocol→EDC]

```
RULE-PT-001: IF study.platform = true
             THEN EDC CRF must support dynamic eligibility criteria versioning
             AND subject screening CRF tagged with eligibility_version

RULE-PT-002: FOR each arm lifecycle event
             GENERATE EDC notification to affected sites
             AND update IWRS arm list
```

#### [Transform:EDC→SDTM]

```
RULE-PT-003: IF subject.available_arms_at_screening ≠ current active arms
             THEN DM.SUBSETID = sub_study.sub_study_name
             AND SUPPDM.QNAM = "ELIGVER", QVAL = subject.eligibility_version

RULE-PT-004: FOR each arm closure
             GENERATE AE, EX, CM data cut at arm closure date
             AND include in arm-specific safety summary
```

#### [Transform:SDTM→ADaM]

```
RULE-PT-005: ADSL must include PLATFORM-specific variables:
             SUBSTUDY (sub-study identifier)
             AVAILARM (arms available at subject's randomization)
             ELIGVER (eligibility criteria version)

RULE-PT-006: FOR Bayesian RAR analysis
             DERIVE ADPC (pharmacokinetic) datasets per arm
             AND update Bayesian posterior distributions

RULE-PT-007: IF arm_graduated
             THEN lock arm-specific ADaM datasets
             AND generate arm-closeout analysis package
```

### New Transforms

#### Transform: Bayesian Allocation Update

| Source | Target | Rule |
|--------|--------|------|
| AdverseEvent (per arm) | Bayesian posterior | Update posterior with observed AE rates |
| Response endpoint (per arm) | Bayesian posterior | Update posterior with observed response rates |
| Bayesian posterior | RandomizationTable.allocation_probabilities | Thompson sampling allocation |
| Allocation probabilities | IWRS randomization weights | Inverse probability weighted assignment |

```
RULE-PT-008: AFTER every n_new_subjects (e.g., n=20)
             TRIGGER Bayesian posterior update
             AND recalculate allocation_probabilities for all active arms
             AND update IWRS randomization weights

RULE-PT-009: IF bayesian_posterior_probability(arm is worst) > 0.95
             THEN TRIGGER arm_futility_recommendation(arm)
             AND notify_steering_committee(arm, "futility")

RULE-PT-010: IF bayesian_posterior_probability(arm is superior to control) > 0.975
             THEN TRIGGER arm_graduation_recommendation(arm)
             AND notify_steering_committee(arm, "graduation")
```

#### Transform: Dynamic Eligibility Criteria

| Source | Target | Rule |
|--------|--------|------|
| Protocol amendment (eligibility section) | EDC screening CRF | Version eligibility criteria |
| New biomarker data | Eligibility criteria | Add/remove biomarker-based criteria |
| Eligibility criteria version | Subject screening log | Record which version was applied |

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-PT-001 | At least 1 control arm always active (if shared_control = true) | REJECT |
| VAL-PT-002 | SUM(allocation_probabilities) = 1.0 at each randomization | REJECT |
| VAL-PT-003 | subject.arm_id IN active_arms_at_assignment | REJECT |
| VAL-PT-004 | lifecycle_status transitions follow valid state machine | REJECT |
| VAL-PT-005 | platform_event timestamps in chronological order per arm | ALERT |
| VAL-PT-006 | Bayesian posterior update frequency ≥ protocol minimum | ALERT |

---

## Business Rules

```
RULE-PT-011: IF arm.lifecycle_status changes from ACTIVE → SUSPENDED
             THEN stop IWRS randomization to arm
             AND notify all active sites(arm = SUSPENDED)
             AND continue follow-up for existing subjects on arm

RULE-PT-012: IF arm.lifecycle_status changes to CLOSED
             THEN lock arm data after resolution period
             AND generate arm-closeout report to steering committee
             AND notify regulator IF arm.close_reason = SAFETY

RULE-PT-013: IF new_arm.submitted AND study.active_arm_count < study.maximum_arms
             THEN create platform_event(ARM_ADDED)
             AND update EDC CRF with new arm information
             AND activate IWRS allocation to new arm

RULE-PT-014: IF concurrent_control = false
             THEN historical control data must be from matching population
             AND documented in SAP with propensity score methodology
```

---

## System Integration

| System | Integration Point | Description |
|--------|------------------|-------------|
| [System:IWRS] | Dynamic randomization | Real-time allocation updates; arm list changes |
| [System:EDC] | Versioned CRFs | Eligibility criteria and arm-specific CRFs update dynamically |
| [System:CTMS] | Arm lifecycle | Track arm activation, suspension, graduation across sites |
| [System:LIMS] | Biomarker-based eligibility | Biomarker results drive eligibility for specific arms |
| [System:Imaging] | Response assessment | Imaging endpoints feed Bayesian response-adaptive model |
| [System:Safety] | Arm-level safety | Safety signals trigger arm suspension review |

---

## SDTM Datasets Affected

| Dataset | Impact |
|---------|--------|
| DM | SUBSETID for arm/sub-study; eligibility version tracking |
| TA | Dynamic: epochs and arms added/removed over time |
| TAETORD | Treatment epoch order varies by enrollment window |
| SUPPDM | Eligibility version, platform-specific qualifiers |
| TS | Trial summary updated with each arm addition/removal |
| TE | Epoch definitions for each arm's lifecycle phase |
