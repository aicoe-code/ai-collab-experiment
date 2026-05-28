# Transformation Pipeline Overview

## End-to-End Chain

The CDOS transformation pipeline converts raw clinical data through canonical
representations into submission-ready artifacts.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Protocol   │────▶│  EDC Raw    │────▶│  CDOS       │────▶│  CDISC      │
│   Document   │     │  CRF Data   │     │  Canonical  │     │  SDTM       │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
       │                   │                   │                    │
       │ T01               │ T02               │ T03,T04,T05       │ T06
       ▼                   ▼                   ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Protocol   │     │  CDASH-     │     │  Lab (LB)   │     │  CDISC      │
│  Metadata   │     │  Aligned    │     │  Safety (AE)│     │  ADaM       │
│  (EDC-Ready)│     │  Fields     │     │  Coded Data │     │  Datasets   │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │ T07
                                                                   ▼
                                                            ┌─────────────┐
                                                            │  eCTD       │
                                                            │  Submission │
                                                            │  Package    │
                                                            └─────────────┘
```

## Transform Chain Table

| Step | Transform ID | Source | Target | File | Trigger |
|------|-------------|--------|--------|------|---------|
| 1 | T01 | Protocol | EDC Metadata | 01-protocol-to-edc.md | Protocol finalization |
| 2 | T02 | EDC CRF Data | CDOS Canonical | 02-edc-to-sdtm.md | CRF page lock |
| 3 | T03 | LIMS Lab Data | SDTM LB domain | 03-labs-to-sdtm.md | Lab data import |
| 4 | T04 | Safety System | ICSR XML | 04-safety-to-icsr.md | SAE/SUSAR report |
| 5 | T05 | Verbatim Terms | Coded Terms | 05-coding-transforms.md | Coding request |
| 6 | T06 | SDTM Datasets | ADaM Datasets | 06-sdtm-to-adam.md | Analysis request |
| 7 | T07 | ADaM Datasets | eCTD Package | 07-adam-to-submission.md | Submission build |

## Domain Coverage

| CDISC Domain | Canonical Entity | Transform(s) |
|-------------|------------------|--------------|
| DM | Subject | T02 |
| AE | AdverseEvent | T02, T04, T05 |
| LB | LabResult | T02, T03 |
| EX | Dose | T02 |
| CM | Medication | T02 |

## Downstream Consumers

| Transform Output | Consumer |
|-----------------|----------|
| EDC Metadata | EDC system configuration |
| CDOS Canonical entities | All downstream transforms |
| SDTM domains | ADaM derivation, regulatory review |
| ADaM datasets | Statistical analysis, submission |
| ICSR XML | Safety system, regulatory agency |
| eCTD package | [System:RegSubmit] |

## Shared Logic

All transforms reference common derivation rules defined in `transform-rules.md`.
