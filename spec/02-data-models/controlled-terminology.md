# CDOS Controlled Terminology

This document defines the controlled terminology systems used across CDOS canonical data models. All controlled terms are versioned and sourced from recognized standards bodies.

---

## 1. MedDRA (Medical Dictionary for Regulatory Activities)

**Version:** MedDRA 27.0 (current release)
**Maintainer:** MSSO (MedDRA Maintenance and Support Services Organization)
**Website:** https://www.meddra.org

MedDRA is used for coding adverse events, medical history, and indications in CDOS.

### Hierarchy Levels

| Level | Code | Description | Example |
|-------|------|-------------|---------|
| SOC | System Organ Class | Highest level grouping | Hepatobiliary disorders |
| HLGT | High Level Group Term | Second level grouping | Hepatic and hepatobiliary disorders |
| HLT | High Level Term | Third level grouping | Hepatic failures NEC |
| PT | Preferred Term | Primary coding level | Hepatic failure |
| LLT | Lowest Level Term | Most specific level | Acute hepatic failure |

### CDOS Usage

| Entity | Attribute | MedDRA Level | Purpose |
|--------|-----------|-------------|---------|
| AdverseEvent | meddra_code | PT | Primary AE coding |
| AdverseEvent | meddra_llt | LLT | Most specific reported term |

### Coding Rules

1. Adverse events MUST be coded to MedDRA PT level for reporting
2. LLT MAY be captured for traceability to verbatim term
3. If a term cannot be coded, flag for medical review
4. SOC codes derive automatically from PT via MedDRA hierarchy
5. SMQ (Standardized MedDRA Queries) may be used for grouped analyses

---

## 2. WHO Drug (WHO Anatomical Therapeutic Chemical Classification)

**Version:** WHO Drug Enhanced Dictionary 2024 Q1
**Maintainer:** Uppsala Monitoring Centre (UMC)
**Website:** https://www.whocc.no

The WHO Drug dictionary is used for coding concomitant and prior medications.

### ATC Hierarchy

| Level | Code Format | Description | Example |
|-------|------------|-------------|---------|
| Level 1 | 1 letter | Anatomical main group | N — Nervous system |
| Level 2 | 1 letter + 2 digits | Therapeutic subgroup | N02 — Analgesics |
| Level 3 | 1 letter + 1 digit + 1 letter | Pharmacological subgroup | N02B — Other analgesics and antipyretics |
| Level 4 | 1 letter + 1 digit + 2 letters | Chemical subgroup | N02BE — Anilides |
| Level 5 | 1 letter + 1 digit + 2 letters + 2 digits | Chemical substance | N02BE01 — Paracetamol |

### CDOS Usage

| Entity | Attribute | WHO Code Level | Purpose |
|--------|-----------|---------------|---------|
| Medication | who_drug_code | ATC Level 5 | Primary drug coding |
| Medication | generic_name | — | INN (International Nonproprietary Name) |
| Medication | drug_name | — | Brand/trade name reported |

### Coding Rules

1. Medications MUST be coded to ATC Level 5 (substance level) when possible
2. Generic name (INN) is preferred over brand name for coding
3. If multiple ingredients, code each ingredient separately
4. Herbal/traditional medicines use ATC group V (Various)
5. Combination products: code under primary ingredient or use combination ATC code if available

---

## 3. CDISC Controlled Terminology (CT)

**Version:** CDISC CT 2024-03-29 (quarterly release)
**Maintainer:** CDISC
**Website:** https://www.cdisc.org/standards/controlled-terminology

CDISC CT provides standardized code lists for CDISC data standards (SDTM, ADaM, CDASH, ODM).

### Codelists Used in CDOS

#### Demographics

| Codelist | CDISC Code | CDOS Entity | CDOS Attribute | Terms |
|----------|-----------|-------------|---------------|-------|
| Sex | C66731 | Subject | sex | MALE, FEMALE, UNKNOWN |
| Race | C74457 | Subject | race | AMERICAN INDIAN OR ALASKA NATIVE, ASIAN, BLACK OR AFRICAN AMERICAN, NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER, WHITE, OTHER, MULTIPLE, NOT REPORTED, UNKNOWN |
| Ethnicity | C66790 | Subject | ethnicity | NOT HISPANIC OR LATINO, HISPANIC OR LATINO, NOT REPORTED, UNKNOWN |

#### Adverse Events

| Codelist | CDISC Code | CDOS Entity | CDOS Attribute | Terms |
|----------|-----------|-------------|---------------|-------|
| Severity | C66769 | AdverseEvent | severity | MILD, MODERATE, SEVERE |
| AE Seriousness | C66768 | AdverseEvent | serious_criteria | DEATH, LIFE-THREATENING, HOSPITALIZATION, PERSISTENT OR SIGNIFICANT DISABILITY/INCAPACITY, CONGENITAL ANOMALY/BIRTH DEFECT, IMPORTANT MEDICAL EVENT |
| AE Outcome | C66767 | AdverseEvent | outcome | RECOVERED/RESOLVED, RECOVERING/RESOLVING, NOT RECOVERED/NOT RESOLVED, RECOVERED/RESOLVED WITH SEQUELAE, FATAL, UNKNOWN |
| Causality | C66766 | AdverseEvent | causality | NOT RELATED, UNLIKELY, POSSIBLE, PROBABLE, DEFINITE |

#### Laboratory

| Codelist | CDISC Code | CDOS Entity | CDOS Attribute | Terms |
|----------|-----------|-------------|---------------|-------|
| Lab Normal Range Indicator | C78722 | LabResult | abnormal_flag | NORMAL, LOW, HIGH, ABNORMAL |
| Specimen Type | C78733 | LabResult | specimen_type | BLOOD, PLASMA, SERUM, URINE, CEREBROSPINAL FLUID, FECES, SALIVA, OTHER |
| Unit | C71620 | LabResult | unit | g/dL, mg/dL, mmol/L, U/L, 10^9/L, etc. |

#### Medications

| Codelist | CDISC Code | CDOS Entity | CDOS Attribute | Terms |
|----------|-----------|-------------|---------------|-------|
| Medication Category | C66781 | Medication | category | CONCOMITANT, CONCOMITANT PRIOR, CONCOMITANT AFTER, PRIOR |
| Route of Administration | C66729 | Medication | route | ORAL, INTRAVENOUS, INTRAMUSCULAR, SUBCUTANEOUS, TOPICAL, INHALATION, RECTAL, NASAL, OPHTHALMIC, TRANSDERMAL, OTHER |
| Dosing Frequency | C66730 | Medication | frequency | ONCE DAILY, TWICE DAILY, THREE TIMES DAILY, EVERY OTHER DAY, WEEKLY, AS NEEDED, CONTINUOUS, OTHER |

#### Visits

| Codelist | CDISC Code | CDOS Entity | CDOS Attribute | Terms |
|----------|-----------|-------------|---------------|-------|
| Visit | C66778 | Visit | visit_type | SCREENING, BASELINE, TREATMENT, FOLLOW-UP, END OF STUDY |

### CDISC Domain Codes

| Domain | Code | CDOS Entity | Description |
|--------|------|-------------|-------------|
| Demographics | DM | Subject | Subject demographics and enrollment |
| Adverse Events | AE | AdverseEvent | Adverse event reports |
| Laboratory Test Results | LB | LabResult | Lab test results |
| Concomitant/Prior Medications | CM | Medication | Medications taken by subjects |
| Subject Visits | SV | Visit | Subject visit schedule |
| Exposure | EX | — | Study drug exposure (future entity) |

---

## 4. Additional Standards Referenced

| Standard | Version | CDOS Usage | Source |
|----------|---------|-----------|--------|
| ISO 3166-1 | 2020 | Country codes in Site entity | ISO |
| ISO 8601 | 2019 | Date/time formatting throughout | ISO |
| ICD-10 | 2024 | Optional additional medical coding | WHO |
| SNOMED CT | 2024 | Optional clinical term coding | SNOMED International |
| UCUM | 2.1 | Units of measure validation | Regenstrief Institute |

---

## 5. Terminology Version Management

| Rule | Description |
|------|-------------|
| Version Lock | CDOS pins terminology to specific versions per release |
| Update Cycle | CDISC CT: quarterly; MedDRA: biannual; WHO Drug: quarterly |
| Grace Period | 90 days after new CT release before mandatory adoption |
| Mapping Required | When CT changes a term, old→new mapping must be documented |
| Audit Trail | All terminology version changes are logged with effective dates |
