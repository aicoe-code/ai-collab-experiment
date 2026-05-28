# Trial Design: Adaptive Design

## Overview

An adaptive design allows pre-planned modifications to the trial based on accumulating data, without undermining the trial's integrity or validity. Changes are driven by pre-specified decision points with quantitative trigger conditions evaluated at interim analyses.

| Attribute | Value |
|-----------|-------|
| Design Type | Adaptive |
| Typical Phase | Phase 2 (dose-finding), Phase 2b/3 (seamless) |
| Key Feature | Pre-planned modifications based on interim data |
| Regulatory Basis | ICH E9(R1) estimands framework; FDA Adaptive Designs Guidance (2019) |
| Alpha Control | Combination test or conditional error rate methods |

---

## Decision Point Specification

Decision points are pre-specified moments in the trial where interim data are evaluated and design modifications may occur. Each decision point is formally specified with trigger conditions, allowable adaptations, and decision authority.

### Decision Point Entity

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| decision_point_id | UUID | PK, NOT NULL | Unique decision point identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Study context |
| dp_name | String(100) | NOT NULL | Decision point label (e.g., DP-1, DOSE-SELECTION) |
| dp_type | Enum(DROP_ARM, DOSE_SELECTION, SAMPLE_SIZE_REESTIMATION, ENDPOINT_SELECTION, FUTILITY, EARLY_EFFICACY, POPULATION_ENRICHMENT) | NOT NULL | Type of adaptation |
| trigger_condition | String(1000) | NOT NULL | Formal trigger condition (see notation below) |
| trigger_metric | String(200) | NOT NULL | What is measured (e.g., response rate, safety rate) |
| trigger_threshold | Float | — | Numeric threshold for triggering |
| trigger_direction | Enum(ABOVE, BELOW, BETWEEN, OUTSIDE) | NOT NULL | Direction of threshold comparison |
| interim_analysis_timing | String(100) | NOT NULL | When the interim occurs (e.g., "after 50% of subjects complete Week 12") |
| information_fraction | Float | 0 < x < 1 | Proportion of total planned information at interim |
| alpha_spent | Float | 0 ≤ x ≤ 1 | Cumulative alpha allocated at this decision point |
| decision_authority | String(200) | NOT NULL | Who makes the decision (IDMC, Sponsor, DMC Charter ref) |
| blinding_at_interim | Enum(BLINDED, PARTIALLY_UNBLINDED, FULLY_UNBLINDED) | NOT NULL | Blinding status at interim |
| adaptation_options | Array[AdaptationOption] | NOT NULL | List of possible actions |
| status | Enum(PLANNED, TRIGGERED, EXECUTED, SKIPPED, INAPPLICABLE) | NOT NULL | Current status |
| actual_decision_date | Date | — | Date the decision was made |
| decision_outcome | String(500) | — | What was actually decided |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DateTime | NOT NULL | Record last update timestamp |

### Adaptation Option Entity

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| adaptation_option_id | UUID | PK, NOT NULL | Unique option identifier |
| decision_point_id | UUID | FK → DecisionPoint, NOT NULL | Parent decision point |
| option_code | String(50) | NOT NULL | Short code (e.g., DROP-ARM-3, CONTINUE-AS-IS) |
| option_label | String(200) | NOT NULL | Descriptive label |
| action_description | String(1000) | NOT NULL | What changes if this option is selected |
| affects_entity | String(100) | NOT NULL | Which [Entity:___] is affected |
| affects_transform | String(100) | — | Which [Transform:___] is affected |
| requires_reconsent | Boolean | DEFAULT false | Whether subjects must re-consent |
| regulatory_notification | Boolean | DEFAULT false | Whether authority notification required |

---

## Trigger Condition Notation

Decision point trigger conditions use formal notation:

```
DP-TRIGGER-001: DROP_ARM
  WHEN: arm.response_rate < threshold.response_rate FOR arm IN study.arms
  THRESHOLD: response_rate < 0.15 (below historical control)
  METRIC: proportion of subjects with CR/PR by RECIST 1.1 at Week 8
  INFORMATION_FRACTION: 0.33 (after 1/3 of planned N completes Week 8)
  ACTION: Drop arm with lowest response rate if below futility boundary

DP-TRIGGER-002: SAMPLE_SIZE_REESTIMATION
  WHEN: observed_variance / planned_variance > reestimation_ratio
  THRESHOLD: ratio > 1.2 OR ratio < 0.8
  METRIC: pooled variance of primary endpoint from interim data
  INFORMATION_FRACTION: 0.50
  ACTION: Recalculate sample size using O'Brien-Fleming spending function

DP-TRIGGER-003: DOSE_SELECTION
  WHEN: all_arms_analyzed = true AT dose_finding_interim
  THRESHOLD: bayesian_posterior_probability(best_dose) > 0.80
  METRIC: Bayesian posterior probability of being the best dose
  INFORMATION_FRACTION: 0.25
  ACTION: Select dose for confirmatory phase; drop other doses

DP-TRIGGER-004: POPULATION_ENRICHMENT
  WHEN: subgroup.response_rate / overall.response_rate > enrichment_ratio
  THRESHOLD: ratio > 1.5 AND subgroup_size ≥ 50
  METRIC: response rate in biomarker-positive subgroup vs. overall
  INFORMATION_FRACTION: 0.40
  ACTION: Restrict enrollment to biomarker-positive subjects

DP-TRIGGER-005: FUTILITY
  WHEN: conditional_power < futility_threshold
  THRESHOLD: conditional_power < 0.20
  METRIC: conditional power calculated using observed treatment effect
  INFORMATION_FRACTION: 0.50, 0.75 (evaluated at two interim analyses)
  ACTION: Stop trial for futility; no further enrollment

DP-TRIGGER-006: EARLY_EFFICACY
  WHEN: test_statistic > efficacy_boundary(information_fraction)
  THRESHOLD: z > O'Brien-Fleming boundary at current information fraction
  METRIC: standardized test statistic for primary endpoint
  INFORMATION_FRACTION: 0.50, 0.75
  ACTION: Stop trial early for efficacy; prepare regulatory submission
```

---

## Data Model Changes

### New Entities

#### DecisionPoint (defined above)

#### AdaptationOption (defined above)

#### InterimAnalysis

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| interim_id | UUID | PK, NOT NULL | Unique interim identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Study context |
| decision_point_id | UUID | FK → DecisionPoint | Linked decision point |
| analysis_number | Integer | NOT NULL | Sequential analysis number |
| planned_date | Date | — | Planned interim analysis date |
| actual_date | Date | — | Actual analysis date |
| information_fraction | Float | NOT NULL | Actual information fraction achieved |
| n_randomized | Integer | NOT NULL | Number randomized at analysis |
| n_completed | Integer | — | Number completing primary endpoint |
| analysis_results | JSON | — | Structured results (endpoint estimates, CIs, p-values) |
| data_cutoff_date | Date | NOT NULL | Data included through this date |
| performed_by | String(200) | NOT NULL | Statistician who performed analysis |
| report_url | String(500) | — | Link to interim analysis report |
| status | Enum(PLANNED, LOCKED, ANALYZED, REPORTED) | NOT NULL | Analysis status |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

#### AdaptiveProtocolAmendment

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| amendment_id | UUID | PK, NOT NULL | Unique amendment identifier |
| protocol_id | UUID | FK → [Entity:Protocol], NOT NULL | Protocol being amended |
| decision_point_id | UUID | FK → DecisionPoint | Decision point that triggered amendment |
| amendment_type | Enum(SAMPLE_SIZE, ENDPOINT, POPULATION, DOSING, PROCEDURE) | NOT NULL | Type of change |
| changes_description | String(2000) | NOT NULL | Description of protocol changes |
| sections_affected | Array[String] | NOT NULL | Protocol sections modified |
| effective_date | Date | NOT NULL | Date amendment takes effect |
| reconsent_required | Boolean | NOT NULL | Whether re-consent is needed |
| irb_approval_date | Date | — | Date IRB approved amendment |
| regulatory_notification_date | Date | — | Date authority notified |
| status | Enum(DRAFT, SUBMITTED, APPROVED, REJECTED) | NOT NULL | Amendment status |

### Modified Entities

#### Study — Add Adaptive Design Configuration

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| adaptive | Boolean | DEFAULT false | Whether study uses adaptive design |
| adaptation_types | Set(DOSE_SELECTION, SAMPLE_SIZE, ENDPOINT, POPULATION, FUTILITY, EARLY_EFFICACY) | — | Types of adaptations planned |
| alpha_spending_function | Enum(OBRIEN_FLEMING, POCOCK, HAYBORTH_DEMETRIOU, WANG_TSIATIS) | — | Alpha spending method |
| total_alpha | Float | DEFAULT 0.05 | Total type I error rate |
| max_sample_size | Integer | — | Maximum sample size after re-estimation |
| dsmb_charter_url | String(500) | — | Link to DSMB charter document |

---

## CDISC Mapping (New Entities)

### DecisionPoint → No direct SDTM domain (metadata/process entity)

Mapped to Supplemental Qualifier datasets or Define-XML metadata:

| CDOS Attribute | CDISC Mapping | Notes |
|---------------|--------------|-------|
| decision_point_id | — | Protocol metadata, captured in Define-XML |
| dp_type | — | Recorded in protocol document |
| information_fraction | — | Referenced in SAP |
| trigger_threshold | — | Pre-specified in SAP |

### InterimAnalysis → ADaM BDS structure

| CDOS Attribute | CDISC Variable | Domain | Role |
|---------------|---------------|--------|------|
| interim_id | — | ADES | Identifier |
| information_fraction | INFOFRAC | ADES | Parameter |
| n_randomized | N | ADES | Parameter |
| analysis_results | — | ADES | Multiple records per interim |

---

## Transform Changes

### Modified Transforms

#### [Transform:Protocol→EDC]

```
RULE-AD-001: IF study.adaptive = true
             THEN protocol_to_edc must include decision point metadata
             AND EDC must support dynamic CRF changes per protocol amendment

RULE-AD-002: IF study.adaptation_types CONTAINS "POPULATION_ENRICHMENT"
             THEN EDC must enforce eligibility criteria versioning
             AND new screening criteria effective_date = amendment.effective_date
```

#### [Transform:EDC→SDTM]

```
RULE-AD-003: IF subject.enrolled_after_amendment AND amendment.amendment_type = "POPULATION"
             THEN DM domain must include APERSN (population reason flag)

RULE-AD-004: FOR each interim_analysis
             TRANSFORM EDC data WHERE visit.actual_date ≤ interim.data_cutoff_date
             INTO analysis-ready SDTM datasets with date-stamped cut
```

#### [Transform:SDTM→ADaM]

```
RULE-AD-005: IF study.adaptive AND interim.analysis_number > 0
             THEN ADSL must include INTFLAGn = "Y" for subjects included in interim n
             AND derive analysis population per interim-specific SAP

RULE-AD-006: IF sample_size_reestimated
             THEN update ADSL.NPERARM, ADAE.N, ADLB.N to reflect actual allocation

RULE-AD-007: IF arm dropped at decision point
             THEN ADSL for dropped-arm subjects: ARMCD = original, DROPREAS = reason
             AND exclude from ITT sensitivity analysis only with documented justification
```

### New Transforms

#### Transform: Interim Analysis Data Cut

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| subject.study_id | interim.study_id | none | link to study |
| visit.actual_date | — | — | filter: visit.actual_date ≤ data_cutoff_date |
| ae.onset_date | — | — | filter: ae.onset_date ≤ data_cutoff_date |
| lab.collection_date | — | — | filter: lab.collection_date ≤ data_cutoff_date |
| — | interim.n_randomized | aggregate | count WHERE subject.status IN (ENROLLED, COMPLETED, WITHDRAWN) |
| — | interim.information_fraction | derived | interim.n_randomized / study.target_enrollment |

#### Transform: Decision Point Evaluation

| Source | Target | Rule |
|--------|--------|------|
| InterimAnalysis.analysis_results | DecisionPoint.trigger_evaluation | Compare trigger_metric vs. trigger_threshold |
| DecisionPoint.trigger_evaluation | DecisionPoint.status | IF triggered: status = TRIGGERED |

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-AD-001 | decision_point.information_fraction strictly increasing across decision points | REJECT |
| VAL-AD-002 | SUM(alpha_spent) across all decision points ≤ total_alpha | REJECT |
| VAL-AD-003 | interim.data_cutoff_date ≤ interim.actual_date | REJECT |
| VAL-AD-004 | adaptation_option.affects_entity references valid entity name | REJECT |
| VAL-AD-005 | decision_point.trigger_condition parseable against schema | QUARANTINE |
| VAL-AD-006 | reconsent_required = true IF amendment affects eligibility or risk | ALERT |

---

## Business Rules

```
RULE-AD-001: IF decision_point.status = "TRIGGERED"
             AND decision_point.decision_authority = "IDMC"
             THEN lock_database_to_interim_cut(study, interim)
             AND generate_IDMC_report(interim)
             AND notify_IDMC_chair(decision_point)

RULE-AD-002: IF adaptation_option.selected = true
             AND adaptation_option.requires_reconsent = true
             THEN trigger_reconsent_workflow(study, amendment)
             AND pause_new_enrollment(study) UNTIL reconsent_complete

RULE-AD-003: IF arm.dropped = true
             THEN notify_IWRS(study, arm) to stop assignment
             AND update_CTMS_enrollment_plan(study, new_plan)
             AND set subject.status = "ACTIVE" for dropped-arm subjects (continue follow-up)

RULE-AD-004: IF sample_size_reestimated AND new_N > max_sample_size
             THEN REJECT reestimation AND escalate to steering committee

RULE-AD-005: IF early_efficacy_triggered AND information_fraction < 0.50
             THEN require_IDMC_charter_exception AND document in SAP amendment

RULE-AD-006: AFTER each decision_point executed
             THEN generate_adaptation_audit_trail(decision_point)
             AND update_protocol_amendment(protocol, amendment)
             AND update_sap(study, decision_point.decision_outcome)
```

---

## System Integration

| System | Integration Point | Description |
|--------|------------------|-------------|
| [System:EDC] | Dynamic CRF | CRF pages update per protocol amendments; eligibility criteria versioned |
| [System:IWRS] | Arm management | Dropped arms removed from randomization; allocation ratios updated |
| [System:CTMS] | Study conduct | Amendment tracking, enrollment plan updates, site notifications |
| [System:LIMS] | Data cut | Lab data frozen at interim cutoff dates |
| [System:Safety] | DSMB reports | SAE data included in unblinded IDMC safety reports |

---

## SDTM Datasets Affected

| Dataset | Impact |
|---------|--------|
| DM | Population flags (APERSN), amendment-effective date flags |
| TA | Treatment assignments updated if arms dropped or added |
| TE | Epoch definitions for adaptive phases |
| SUPPDM | Supplemental qualifiers for adaptive design metadata |
| ADES | Analysis dataset for design effect summaries |
