# CDOS Controlled Terminology Reference

This document catalogs the controlled terminology (CT) sources used across the CDOS data model. All entities in `canonical/` reference these vocabularies for their coded fields.

---

## 1. CDISC Controlled Terminology (CDISC CT)

**Standard:** CDISC Controlled Terminology, latest release
**Applied To:** All SDTM domains (DM, AE, LB, CM, SV, TS, TI)
**Format:** Codelist Code / Term Code / Submission Value

### Key Codelists

| Codelist Code | Codelist Name | Used In | Example Terms |
|---------------|---------------|---------|---------------|
| C66731 | Sex | Subject.sex | M, F, U |
| C74457 | Race | Subject.race | WHITE, ASIAN, BLACK OR AFRICAN AMERICAN |
| C66769 | Severity | AdverseEvent.severity | MILD, MODERATE, SEVERE |
| C66770 | Serious Event | AdverseEvent.seriousness | Y, N |
| C66768 | Causality | AdverseEvent.causality | RELATED, NOT RELATED, POSSIBLY RELATED |
| C66767 | Outcome of Event | AdverseEvent.outcome | RECOVERED, NOT RECOVERED, FATAL |
| C66766 | Action Taken | AdverseEvent.action_taken | NONE, DOSE REDUCED, DRUG WITHDRAWN |
| C78734 | Normal Abnormal | LabResult.normal_flag | NORMAL, ABNORMAL, ABNORMAL LOW, ABNORMAL HIGH |
| C78736 | Lab Category | LabResult.category | HEMATOLOGY, CHEMISTRY, URINALYSIS |
| C66740 | Visit Name | Visit.visit_name | SCREENING, BASELINE, TREATMENT |
| C85493 | Study Design | Protocol.study_design | RANDOMIZED, OPEN LABEL, PLACEBO CONTROLLED |

### Referenced Version
- CDISC CT Version: Latest quarterly release
- Source: https://wiki.cdisc.org/display/ctdashterminology
- Implementation: CDISC-provided XML and CSV files, loaded into `cdisc_controlled_terminology` table

---

## 2. MedDRA (Medical Dictionary for Regulatory Activities)

**Standard:** MedDRA, latest version
**Applied To:** AdverseEvent entity (ae domain)
**Format:** Code / Term / Level

### MedDRA Hierarchy

| Level | Scope | Example |
|-------|-------|---------|
| SOC (System Organ Class) | Broadest classification | Gastrointestinal disorders |
| HLGT (High Level Group Term) | Sub-group | Gastrointestinal motility and defaecation conditions |
| HLT (High Level Term) | Therapeutic area grouping | Diarrhoea NEC |
| PT (Preferred Term) | Preferred terminology | Diarrhoea |
| LLT (Lowest Level Term) | Most specific term | Diarrhoea postoperative |

### Fields in AdverseEvent

| Entity Field | MedDRA Level | CDISC Variable | Example |
|-------------|-------------|----------------|---------|
| meddra_code | PT Code | AEDECOD | 10012735 |
| meddra_llt | LLT | — | Loose stools |
| meddra_pt | PT | AEDECOD | Diarrhoea |
| meddra_soc | SOC | AEBODSYS | Gastrointestinal disorders |

### Top SOC Categories (26 System Organ Classes)

1. Administration site conditions
2. Blood and lymphatic system disorders
3. Cardiac disorders
4. Congenital, familial and genetic disorders
5. Ear and labyrinth disorders
6. Endocrine disorders
7. Eye disorders
8. Gastrointestinal disorders
9. General disorders and administration site conditions
10. Hepatobiliary disorders
11. Immune system disorders
12. Infections and infestations
13. Injury, poisoning and procedural complications
14. Investigations
15. Metabolism and nutrition disorders
16. Musculoskeletal and connective tissue disorders
17. Neoplasms benign, malignant and unspecified (incl cysts and polyps)
18. Nervous system disorders
19. Pregnancy, puerperium and perinatal conditions
20. Psychiatric disorders
21. Renal and urinary disorders
22. Reproductive system and breast disorders
23. Respiratory, thoracic and mediastinal disorders
24. Skin and subcutaneous tissue disorders
25. Social circumstances
26. Surgical and medical procedures
27. Vascular disorders

### Referenced Version
- MedDRA Version: Latest (updated biannually)
- Source: MedDRA MSSO (Maintenance and Support Services Organization)
- Implementation: Loaded into `meddra_soc_reference` and `meddra_pt_lookup` tables

---

## 3. WHO Drug Dictionary

**Standard:** WHO Drug Dictionary Enhanced (WHO-DDE), latest quarterly update
**Applied To:** Medication entity (med domain)
**Format:** ATC Code / Drug Name / Chemical Substance

### ATC Classification Hierarchy

| Level | Description | Example |
|-------|-------------|---------|
| Level 1 | Anatomical Main Group | N — NERVOUS SYSTEM |
| Level 2 | Therapeutic Subgroup | N02 — ANALGESICS |
| Level 3 | Pharmacological Subgroup | N02A — OPIOIDS |
| Level 4 | Chemical Subgroup | N02AB — Phenylpiperidine derivatives |
| Level 5 | Chemical Substance | N02AB02 — Pethidine |

### Fields in Medication

| Entity Field | WHO-DDE Mapping | Description |
|-------------|-----------------|-------------|
| medication_name | Trade/Generic Name | Name of the medication |
| who_drug_code | Drug Code | WHO-assigned drug code |

### ATC Level 1 Groups (14 Main Groups)

| Code | Name |
|------|------|
| A | Alimentary tract and metabolism |
| B | Blood and blood forming organs |
| C | Cardiovascular system |
| D | Dermatologicals |
| G | Genito-urinary system and sex hormones |
| H | Systemic hormonal preparations (excl. sex hormones and insulins) |
| J | Antiinfectives for systemic use |
| L | Antineoplastic and immunomodulating agents |
| M | Musculo-skeletal system |
| N | Nervous system |
| P | Antiparasitic products, insecticides and repellents |
| R | Respiratory system |
| S | Sensory organs |
| V | Various |

### Referenced Version
- WHO-DDE Version: Latest quarterly release
- Source: Uppsala Monitoring Centre (UMC)
- Implementation: Loaded into `who_drug_atc_reference` table

---

## 4. ISO 3166-1 Country Codes

**Standard:** ISO 3166-1 alpha-2 / alpha-3
**Applied To:** Site.country (CDISC DM: COUNTRY)
**Format:** 2-letter or 3-letter country code

### Usage
- Primary: ISO 3166-1 alpha-2 (e.g., US, GB, DE)
- Alternate: ISO 3166-1 alpha-3 (e.g., USA, GBR, DEU)
- Required field on Site entity
- Used in SDTM DM domain as COUNTRY variable

### Common Countries in Clinical Trials

| Alpha-2 | Alpha-3 | Name |
|---------|---------|------|
| US | USA | United States of America |
| CA | CAN | Canada |
| GB | GBR | United Kingdom |
| DE | DEU | Germany |
| FR | FRA | France |
| JP | JPN | Japan |
| CN | CHN | China |
| IN | IND | India |
| AU | AUS | Australia |
| BR | BRA | Brazil |

### Referenced Version
- ISO 3166-1: Latest published edition
- Implementation: Loaded into `iso_country_code` table

---

## 5. UCUM (Unified Code for Units of Measure)

**Standard:** UCUM, latest version
**Applied To:** LabResult.unit (CDISC LB: LBORRESU)
**Format:** UCUM code

### Common UCUM Codes for Lab Results

| UCUM Code | Description | Category |
|-----------|-------------|----------|
| g/dL | grams per deciliter | Concentration |
| g/L | grams per liter | Concentration |
| mg/dL | milligrams per deciliter | Concentration |
| mmol/L | millimoles per liter | Concentration |
| umol/L | micromoles per liter | Concentration |
| U/L | units per liter | Enzyme activity |
| 10*3/uL | thousands per microliter | Hematology (WBC, platelets) |
| 10*6/uL | millions per microliter | Hematology (RBC) |
| % | percent | Percentage (hematocrit, etc.) |
| fL | femtoliters | Hematology (MCV) |
| pg | picograms | Hematology (MCH) |
| ng/mL | nanograms per milliliter | Drug levels, biomarkers |
| pg/mL | picograms per milliliter | Hormones, biomarkers |
| IU/L | international units per liter | Enzyme activity |
| mL/min | milliliters per minute | Renal function (GFR) |

### Referenced Version
- UCUM: Latest
- Source: Regenstrief Institute
- Implementation: Loaded into `ucum_unit` table

---

## 6. CDISC SDTM Domain Codes

**Standard:** SDTM v3.4
**Applied To:** All entity-level CDISC mappings

### Domain Categories

| Domain Code | Domain Name | Class | CDOS Entity |
|------------|-------------|-------|-------------|
| DM | Demographics | Special Purpose | Study, Subject, Site |
| AE | Adverse Events | Events | AdverseEvent |
| LB | Laboratory Test Results | Findings | LabResult |
| CM | Concomitant Medications | Interventions | Medication |
| EX | Exposure | Interventions | Medication (study drug) |
| SV | Subject Visits | Findings | Visit |
| TS | Trial Summary | Special Purpose | Study, Protocol |
| TI | Trial Inclusion/Exclusion Criteria | Trial Design | Protocol |

### SDTM Variable Naming Convention
- Dataset qualifier prefix: 2-letter domain code (e.g., AE, LB)
- Example: AETERM, LBORRES, CMTRT
- CDOS attributes map to SDTM variables as documented in `schemas.md`

---

## Implementation Notes

1. **Versioning:** All CT tables include source version tracking. Updates are applied via numbered migrations.
2. **Loading:** CT data is loaded from CDISC-provided CSV/XML files during system initialization.
3. **Validation:** API layer validates coded fields against CT tables before persistence.
4. **Updates:** CT updates follow quarterly CDISC release cycle, applied as delta migrations.
5. **21 CFR Part 11:** All CT changes are audited with timestamps and change reasons.
