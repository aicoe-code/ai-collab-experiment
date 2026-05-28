# Trial Design: Real-World Evidence (RWE)

## Overview

Real-World Evidence studies use data collected outside traditional clinical trials — from [System:EDC]-like EHR systems, claims databases, registries, wearables, and patient-reported outcomes — to generate evidence on treatment effectiveness, safety, and outcomes in routine clinical practice. RWE studies may be prospective observational studies, retrospective database studies, or pragmatic trials embedded in clinical care.

| Attribute | Value |
|-----------|-------|
| Design Type | Real-World Evidence / Observational / Pragmatic |
| Typical Phase | Post-marketing (Phase 4), Label Expansion, Safety Monitoring |
| Data Sources | EHR, Claims, Registries, Wearables, ePRO |
| Regulatory Basis | FDA RWE Framework (2018); EMA RWE Reflection Paper (2024); ICH E10 |
| Key Challenge | Data quality, missingness, confounding, provenance |

---

## RWE Data Source Model

RWE studies integrate data from heterogeneous sources. Each source has distinct data quality characteristics and requires different processing.

### RWE Data Source Entity

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| data_source_id | UUID | PK, NOT NULL | Unique data source identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Study context |
| source_type | Enum(EHR, CLAIMS, REGISTRY, WEARABLE, EPRO, PATIENT_REPORTED, PHARMACY, LAB_SYSTEM, VITAL_REGISTRY) | NOT NULL | Type of data source |
| source_name | String(200) | NOT NULL | Name of data source (e.g., "Truven MarketScan", "Cerner Health Facts") |
| source_vendor | String(200) | — | Data vendor or institution |
| data_extraction_method | Enum(DIRECT_EHR_QUERY, FLAT_FILE_EXTRACT, FHIR_API, HL7_V2, MANUAL_ENTRY) | NOT NULL | How data is obtained |
| data_format | Enum(CDISC, OMOP, PCORNET, SENTINEL, PROPRIETARY) | NOT NULL | Native data model |
| temporal_coverage_start | Date | — | Earliest available data |
| temporal_coverage_end | Date | — | Most recent available data |
| population_cohort | String(500) | — | Description of population in source |
| data_quality_tier | Enum(TIER_1, TIER_2, TIER_3) | NOT NULL | Quality classification |
| refresh_frequency | Enum(REAL_TIME, DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUAL) | NOT NULL | How often data is refreshed |
| linkage_method | Enum(DETERMINISTIC, PROBABILISTIC, TOKENIZED, NONE) | NOT NULL | How records are linked across sources |
| data_use_agreement | String(500) | — | Reference to DUA |
| status | Enum(ONBOARDING, ACTIVE, PAUSED, RETIRED) | NOT NULL | Source status |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

### Data Quality Tier Definition

| Tier | Criteria | Usage |
|------|----------|-------|
| TIER_1 | ≥95% completeness, validated against source, temporally consistent | Primary analysis, regulatory submission |
| TIER_2 | 80–95% completeness, partially validated | Sensitivity analysis |
| TIER_3 | <80% completeness, limited validation | Exploratory analysis only |

---

## Data Model Changes

### New Entities

#### RWE Data Source (defined above)

#### DataLineage

Tracks the provenance and transformation chain for every RWE data point:

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| lineage_id | UUID | PK, NOT NULL | Unique lineage identifier |
| entity_type | String(50) | NOT NULL | Target entity type (e.g., "Subject", "AdverseEvent") |
| entity_id | UUID | NOT NULL | Target entity ID |
| source_data_source_id | UUID | FK → RWEDataSource | Origin data source |
| source_record_id | String(200) | NOT NULL | Original record identifier in source system |
| source_table | String(100) | — | Source table/field |
| source_column | String(100) | — | Source column |
| source_value | String(1000) | — | Original value before transformation |
| transform_applied | String(200) | — | Transform that produced the target value |
| transform_timestamp | DateTime | NOT NULL | When the transform was applied |
| confidence_score | Float | 0.0–1.0 | Confidence in the mapping |
| data_quality_flag | Enum(VALID, SUSPECT, IMPUTED, DERIVED) | NOT NULL | Quality indicator |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

#### RWEEndpoint

Defines endpoints derived from RWE data, with data requirements and validation:

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| endpoint_id | UUID | PK, NOT NULL | Unique endpoint identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Study context |
| endpoint_name | String(200) | NOT NULL | Endpoint name (e.g., "Time to Treatment Discontinuation") |
| endpoint_type | Enum(EFFECTIVENESS, SAFETY, UTILIZATION, COST, QUALITY_OF_LIFE, PATIENT_REPORTED) | NOT NULL | Endpoint category |
| data_sources_required | Array[String] | NOT NULL | Minimum data sources needed |
| algorithm_description | String(2000) | NOT NULL | Algorithm to derive endpoint |
| algorithm_code_url | String(500) | — | Link to executable algorithm code |
| validation_method | String(500) | NOT NULL | How endpoint was validated |
| missing_data_method | Enum(COMPLETE_CASE, MULTIPLE_IMPUTATION, INVERSE_PROBABILITY_WEIGHTING, LAST_OBSERVATION_CARRIED_FORWARD) | NOT NULL | Handling of missing data |
| confounding_method | Enum(IPTW, PROPENSITY_SCORE_MATCHING, INSTRUMENTAL_VARIABLE, DIFFERENCE_IN_DIFFERENCES, REGRESSION_DISCONTINUITY, NONE) | NOT NULL | Confounding adjustment |
| min_data_quality_tier | Enum(TIER_1, TIER_2, TIER_3) | NOT NULL | Minimum data quality required |
| status | Enum(DRAFT, VALIDATED, ACTIVE, RETIRED) | NOT NULL | Endpoint status |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

#### ConfounderSet

Defines confounders that must be measured and adjusted for:

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| confounder_set_id | UUID | PK, NOT NULL | Unique set identifier |
| study_id | UUID | FK → [Entity:Study], NOT NULL | Study context |
| set_name | String(200) | NOT NULL | Set name (e.g., "Core confounders for mortality analysis") |
| confounders | Array[Confounder] | NOT NULL | List of confounders |
| adjustment_method | String(200) | NOT NULL | Statistical adjustment method |
| balance_diagnostics | String(500) | NOT NULL | How balance is assessed (e.g., SMD < 0.1) |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Record creation timestamp |

#### Confounder (Nested)

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| confounder_name | String(200) | NOT NULL | Variable name |
| confounder_type | Enum(DEMOGRAPHIC, CLINICAL, LAB, MEDICATION, PROCEDURE, COMORBIDITY) | NOT NULL | Category |
| source_entity | String(50) | NOT NULL | [Entity:___] it maps to |
| source_field | String(100) | NOT NULL | Field within the entity |
| measurement_window | String(200) | NOT NULL | When measured relative to index date |
| required | Boolean | NOT NULL | Whether mandatory for analysis |

---

### Modified Entities

#### Subject — Add RWE-Specific Fields

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| source_type | Enum(PROSPECTIVE_CLINICAL_TRIAL, EHR, CLAIMS, REGISTRY, EPRO) | — | Source of subject data |
| data_source_id | UUID | FK → RWEDataSource | Data source for this subject |
| index_date | Date | — | RWE index date (treatment start, diagnosis, etc.) |
| enrollment_type | Enum(TRADITIONAL_CONSENT, WAIVER_OF_CONSENT, BROAD_CONSENT, OPT_OUT) | NOT NULL | Consent model used |
| data_linkage_token | String(200) | — | Tokenized identifier for cross-source linkage |
| follow_up_end_date | Date | — | Date follow-up ends (death, disenrollment, study end) |
| follow_up_end_reason | Enum(DEATH, DISENROLLMENT, STUDY_END, DATA_CUTOFF, LOST_TO_FOLLOW_UP) | — | Reason follow-up ended |

#### Study — Add RWE Configuration

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| rwe | Boolean | DEFAULT false | Whether study uses RWE data |
| rwe_design | Enum(RETROSPECTIVE_COHORT, PROSPECTIVE_OBSERVATIONAL, PRAGMATIC_TRIAL, CASE_CONTROL, CROSS_SECTIONAL) | — | RWE design type |
| data_sources | Array[String] | — | List of data source IDs |
| primary_data_model | Enum(CDISC, OMOP, PCORNET, SENTINEL) | NOT NULL | Canonical data model for analysis |
| imputation_strategy | String(200) | — | How missing data is handled |
| minimum_follow_up_days | Integer | ≥ 0 | Required follow-up duration |

#### Visit — Add RWE Visit Types

| Attribute | Type | Constraint | Description |
|-----------|------|-----------|-------------|
| visit_source | Enum(CLINICAL_TRIAL, EHR_ROUTINE, EHR_UNSCHEDULED, CLAIMS, PATIENT_INITIATED) | — | Source of visit data |
| data_quality_flag | Enum(VALID, SUSPECT, ESTIMATED) | — | Data quality indicator |

---

## CDISC Mapping

### RWEDataSource → No direct SDTM mapping (metadata entity)

Mapped to Define-XML and submission metadata:

| CDOS Attribute | CDISC Mapping | Notes |
|---------------|--------------|-------|
| data_source_id | — | Referenced in Define-XML data origin descriptions |
| source_type | — | Documented in study metadata |
| data_quality_tier | — | Referenced in analysis metadata |

### Subject (RWE Additions)

| CDOS Attribute | CDISC Variable | Domain | Role |
|---------------|---------------|--------|------|
| index_date | RFICDTC | DM | Timing |
| enrollment_type | — | DM | Record Qualifier |
| follow_up_end_date | RFPENDTC | DM | Timing |
| source_type | DMDATA_SOURCE (custom) | SUPPDM | Qualifier |

### DataLineage → Not directly mapped to SDTM (audit/provenance entity)

Stored as supplemental metadata in Define-XML or as traceability appendices.

---

## Transform Changes

### Modified Transforms

#### [Transform:Protocol→EDC]

```
RULE-RWE-001: IF study.rwe = true
             THEN EDC may be replaced by EHR data extraction
             AND protocol must specify data quality acceptance criteria per source

RULE-RWE-002: IF study.rwe_design = "PRAGMATIC_TRIAL"
             THEN EDC CRF must align with routine clinical workflows
             AND minimize additional data collection beyond standard of care
```

#### [Transform:EDC→SDTM]

```
RULE-RWE-003: FOR each RWE data source
             TRANSFORM source data INTO CDISC SDTM/CDASH format
             AND tag each SDTM record with source metadata via SUPPQUAL

RULE-RWE-004: IF source.data_format = "OMOP"
             THEN apply OMOP-to-SDTM mapping (OMOP CDM → SDTM domains)
             AND log all mapping decisions in DataLineage

RULE-RWE-005: IF source.data_format = "PCORNET"
             THEN apply PCORnet-to-SDTM mapping
             AND validate against CDISC CT after mapping

RULE-RWE-006: FOR each transformed record
             CREATE DataLineage entry with:
               source_data_source_id, source_record_id, source_table,
               source_column, source_value, transform_applied
```

#### [Transform:SDTM→ADaM]

```
RULE-RWE-007: ADSL must include RWE-specific variables:
               DATASRC (primary data source)
               INDEXDT (index date for time-to-event analysis)
               FOLLOWUP_DAYS (follow-up duration)
               ENROLLTYPE (enrollment type)

RULE-RWE-008: FOR effectiveness endpoints
             APPLY confounding adjustment method per endpoint:
               IF confounding_method = "IPTW"
                 THEN derive propensity scores and IPTW weights
                 AND include in ADSL as PS and IPW variables

RULE-RWE-009: FOR missing data handling
             IF missing_data_method = "MULTIPLE_IMPUTATION"
               THEN generate m imputed datasets (default m=20)
               AND combine using Rubin's rules in analysis output

RULE-RWE-010: DATA QUALITY integration
             IF any record has data_quality_flag = "SUSPECT"
             THEN include in sensitivity analysis only
             AND exclude from primary analysis if quality_flag is TIER_3
```

### New Transforms

#### Transform: RWE Source to Canonical

| Source | Target | Rule |
|--------|--------|------|
| EHR patient demographics | [Entity:Subject] | Map EHR demographics to Subject fields |
| EHR encounters | [Entity:Visit] | Map EHR visits to Visit with visit_source = EHR_ROUTINE |
| EHR problem list, diagnoses | [Entity:AdverseEvent] | Map ICD-coded diagnoses to AdverseEvent with meddra mapping |
| EHR lab results | [Entity:LabResult] | Map LOINC-coded labs to LabResult |
| EHR medication orders | [Entity:Medication] | Map RxNorm medications to Medication |
| Claims CPT/ICD codes | [Entity:Visit], [Entity:AdverseEvent] | Map claims codes to entities |

#### Transform: Propensity Score Derivation

| Source | Target | Rule |
|--------|--------|------|
| ConfounderSet.confounders | Propensity score model | Logistic regression: treatment ~ confounders |
| Propensity score model | IPTW weights | w = 1/PS for treated, 1/(1-PS) for control |
| IPTW weights | ADSL.IPW | Store weights in ADSL for weighted analysis |
| IPTW-applied data | Balance diagnostics | Check SMD < 0.1 post-weighting |

```
RULE-RWE-011: FOR propensity score derivation
             FIT logistic regression: treatment ~ confounder_1 + confounder_2 + ... + confounder_k
             AND predict propensity score for each subject
             AND compute stabilized IPTW: sw = (P(T=t)/P(T=t|X)) for treatment t

RULE-RWE-012: AFTER IPTW application
             IF any standardized mean difference > 0.1
             THEN ALERT: residual confounding detected
             AND recommend additional confounder adjustment or alternative method
```

#### Transform: Endpoint Algorithm Execution

| Source | Target | Rule |
|--------|--------|------|
| Multiple entities (Subject, Visit, AE, Lab, Med) | RWEEndpoint | Execute algorithm to derive endpoint value |
| Endpoint value + metadata | DataLineage | Record derivation chain |

```
RULE-RWE-013: FOR each RWEEndpoint
             EXECUTE endpoint_algorithm ON canonical data
             WHERE all data_sources_required are available
             AND data_quality ≥ endpoint.min_data_quality_tier
             AND subject.follow_up_end_date ≥ required_follow_up

RULE-RWE-014: IF endpoint requires data from multiple sources
             LINK records using subject.data_linkage_token
             AND log linkage match rate in DataLineage
             IF linkage_match_rate < 0.80
               THEN ALERT: high linkage failure rate
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-RWE-001 | Each subject has data_source_id NOT NULL | REJECT |
| VAL-RWE-002 | DataLineage exists for all RWE-derived records | QUARANTINE |
| VAL-RWE-003 | Subject.index_date ≤ first study-related data point | REJECT |
| VAL-RWE-004 | Subject.follow_up_end_date ≥ index_date | REJECT |
| VAL-RWE-005 | data_quality_tier ≥ endpoint.min_data_quality_tier | ALERT |
| VAL-RWE-006 | Confounder completeness ≥ 80% for required confounders | ALERT |
| VAL-RWE-007 | Linkage match rate ≥ 0.70 for multi-source studies | ALERT |
| VAL-RWE-008 | Endpoint algorithm executed without errors | REJECT |

---

## Business Rules

```
RULE-RWE-015: IF study.rwe = true AND subject.source_type IN (EHR, CLAIMS)
             THEN waiver of consent may apply
             AND IRB/IEC approval for waiver documented in eTMF

RULE-RWE-016: IF data arrives from new source ONBOARDING → ACTIVE
             THEN execute data_quality_assessment(source)
             AND assign data_quality_tier
             AND integrate into platform if tier ≥ TIER_2

RULE-RWE-017: FOR each data refresh cycle
             REFRESH source data WHERE refresh_frequency matches current date
             AND re-execute all dependent transforms
             AND update DataLineage for affected records

RULE-RWE-018: IF subject.data_linkage_token fails to match across ≥2 sources
             THEN QUARANTINE subject data
             AND flag for manual review of linkage

RULE-RWE-019: IF missing_data_method = "MULTIPLE_IMPUTATION"
             THEN run m imputations (m=20 default) on each refresh
             AND flag any variable with >50% missing rate for review
```

---

## System Integration

| System | Integration Point | Description |
|--------|------------------|-------------|
| [System:EDC] | EHR data feeds | EHR data extracted via FHIR or flat file; mapped to CDISC |
| [System:LIMS] | External lab data | LOINC-coded lab results from clinical labs |
| [System:Wearables] | Sensor data | Continuous monitoring data (activity, vitals) as endpoint inputs |
| [System:eCOA] | Patient-reported | ePRO instruments for RWE-specific endpoints |
| [System:RegSubmit] | RWE submissions | RWE packages formatted for regulatory submission (eCTD Module 5) |
| [System:Safety] | Post-marketing safety | RWE data feeds into pharmacovigilance signal detection |

---

## SDTM Datasets Affected

| Dataset | Impact |
|---------|--------|
| DM | Additional variables for RWE: index date, follow-up, data source |
| AE | May include claims-coded events (ICD → MedDRA mapping) |
| LB | LOINC-coded results from external labs |
| CM | RxNorm-coded medications from EHR/pharmacy data |
| EX | Treatment exposure derived from pharmacy/prescribing data |
| SV | Visit records from EHR encounters |
| DA | Device/Activity domain for wearable-derived data |
| SU | Substance Use domain for RWE substance exposure data |
| RELREC | Cross-source record linkage references |
| SUPPQUAL | Supplemental qualifiers for source metadata, quality flags |
