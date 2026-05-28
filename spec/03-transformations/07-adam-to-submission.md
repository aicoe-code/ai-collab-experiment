# Transform: ADaM → eCTD Submission Package

## Overview

- Source: CDISC ADaM datasets (ADSL, ADAE, ADLB, ADPC) + Define-XML
- Target: eCTD submission package (Module 5 clinical study datasets)
- Trigger: Submission build request
- Frequency: On-demand (per submission milestone)

---

## Field Mapping

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| ADSL.* | adsl.xpt | DataFrame → SAS transport | SAS XPORT v5 |
| ADAE.* | adae.xpt | DataFrame → SAS transport | SAS XPORT v5 |
| ADLB.* | adlb.xpt | DataFrame → SAS transport | SAS XPORT v5 |
| Define-XML | define.xml | XML → eCTD-validated XML | ICH M8 compliance |
| ADaM metadata | define2-1.xsl | transform | stylesheet |
| SAP | studyreport.docx | template → final | report generation |
| Tables/Figures | tlf-listing.pdf | compiled | TLF package |

---

## Business Rules

```
RULE-001: FOR EACH adam_dataset IN (ADSL, ADAE, ADLB):
          xpt_file = export_sas_xport(adam_dataset, version=5)
          VALIDATE xpt_file against FDA technical conformance guide
          IF validation FAILS THEN REJECT

RULE-002: Generate Define-XML v2.1:
          define = build_define_xml(
            datasets: [ADSL, ADAE, ADLB],
            metadata: data_dictionary,
            controlled_terminology: cdisc_ct_version,
            computational_methods: derivation_documentation
          )
          VALIDATE define against Define-XML v2.1 schema

RULE-003: Build eCTD Module 5 structure:
          ectd = {
            "m5": {
              "clinical": {
                "datasets": [adsl.xpt, adae.xpt, adlb.xpt],
                "define": define.xml,
                "reviewers_guide": reviewers_guide.pdf,
                "datasets_guide": datasets_guide.pdf
              }
            }
          }

RULE-004: Generate Study Data Reviewer's Guide:
          srdg = build_reviewers_guide(
            study_id: ADSL.STUDYID[0],
            datasets: [ADSL, ADAE, ADLB],
            known_issues: qc_findings,
            imputation_methods: derivation_doc
          )

RULE-005: FOR EACH dataset:
          qc = compare_source_to_xpt(adam_dataset, xpt_file)
          IF qc.row_count_diff > 0 THEN REJECT
          IF qc.value_diffs > 0 THEN QUARANTINE

RULE-006: STAMP_AUDIT(package, "T07", submission_user)  // SHARED-009

RULE-007: Generate submission XML backbone:
          backbone = build_ectd_xml(
            sequence_number: submission.sequence_number,
            application_number: submission.ind_number,
            documents: ectd_package
          )
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-001 | All XPT files parseable by SAS 9.4 | REJECT |
| VAL-002 | Define-XML validates against CDISC v2.1 XSD | REJECT |
| VAL-003 | USUBJID consistent across all XPT files | REJECT |
| VAL-004 | No truncated variable names (>8 chars for SAS v5 XPORT) | REJECT |
| VAL-005 | Character variables <= 200 bytes | QUARANTINE |
| VAL-006 | Numeric date variables in SAS date format | REJECT |
| VAL-007 | eCTD backbone validates against ICH M8 schema | REJECT |
| VAL-008 | Row counts match between ADaM source and XPT | REJECT |

---

## Error Handling

- SAS XPORT export failure → REJECT, log to `dlq.adam-to-submission`
- Define-XML schema validation failure → REJECT with error details
- Row count mismatch → REJECT, flag for QC review
- eCTD backbone invalid → REJECT, alert regulatory operations
- Character truncation detected → QUARANTINE, truncate with warning
- Submission sequence conflict → REJECT with error "sequence_conflict"
