# Transform: Verbatim Terms → Coded Terms

## Overview

- Source: Raw verbatim text from EDC fields (AE terms, medication names, medical history)
- Target: CDISC CT-coded values (MedDRA for AEs, WHO Drug for medications)
- Trigger: Coding request (auto or manual queue)
- Frequency: Real-time (on verbatim entry) + batch review

---

## Field Mapping

| Source Field | Target Field | Type Conversion | Rule |
|-------------|-------------|----------------|------|
| AdverseEvent.term (verbatim) | AdverseEvent.meddra_code | string → MedDRA PT | auto-code via MedDRA |
| AdverseEvent.term (verbatim) | AdverseEvent.meddra_llt | string → MedDRA LLT | low-level term |
| AdverseEvent.meddra_code | AdverseEvent.soc_code | MedDRA PT → SOC | MedDRA hierarchy |
| AdverseEvent.meddra_code | AdverseEvent.hlgt_code | MedDRA PT → HLGT | MedDRA hierarchy |
| Medication.term (verbatim) | Medication.atc_code | string → WHO ATC | auto-code via WHO Drug |
| Medication.term (verbatim) | Medication.drug_name | string → WHO preferred | dictionary lookup |
| MedicalHistory.term (verbatim) | MedicalHistory.meddra_code | string → MedDRA PT | auto-code |

---

## Business Rules

```
RULE-001: FOR EACH verbatim_term:
          candidates = MedDRA.search(verbatim_term)
          IF candidates.count = 1 AND candidates.confidence >= 0.95
          THEN auto_code = candidates[0].pt_code
          AND auto_status = "AUTO_CODED"
          ELSE IF candidates.count >= 1 AND candidates.confidence >= 0.80
          THEN auto_status = "PENDING_REVIEW"
          AND queue_for_review(verbatim_term, candidates)
          ELSE auto_status = "NO_MATCH"
          AND queue_for_manual_coding(verbatim_term)

RULE-002: FOR EACH medication_term:
          candidates = WHO_Drug.search(medication_term)
          IF candidates.count = 1 AND candidates.confidence >= 0.95
          THEN auto_code = candidates[0].atc_code
          ELSE queue_for_manual_coding(medication_term)

RULE-003: IF auto_code IS SET
          THEN Derive MedDRA hierarchy:
            AdverseEvent.soc_code = MedDRA.get_soc(pt_code)
            AdverseEvent.hlgt_code = MedDRA.get_hlgt(pt_code)
            AdverseEvent.hlt_code = MedDRA.get_hlt(pt_code)

RULE-004: IF coding_reviewer APPROVES manual_code
          THEN AdverseEvent.meddra_code = manual_code
          AND auto_status = "MANUALLY_CODED"
          ELSE IF coding_reviewer REJECTS
          THEN auto_status = "CODING_REJECTED"
          AND queue_for_resolution(verbatim_term)

RULE-005: STAMP_AUDIT(record, "T05", system_user)  // SHARED-009

RULE-006: EXPECTEDNESS CHECK:
          is_expected = check_expectedness(meddra_code, Investigational_Product_Brochure)
          AdverseEvent.expected = is_expected
          IF NOT is_expected AND AdverseEvent.serious = true
          THEN AdverseEvent.susar_flag = true
```

---

## Validation Rules

| Rule ID | Check | On Failure |
|---------|-------|-----------|
| VAL-001 | verbatim_term NOT NULL | REJECT |
| VAL-002 | meddra_code IS valid in current MedDRA version | QUARANTINE |
| VAL-003 | atc_code IS valid in current WHO Drug version | QUARANTINE |
| VAL-004 | SOC code IS ancestor of PT in MedDRA hierarchy | REJECT |
| VAL-005 | Coding status IN (AUTO_CODED, MANUALLY_CODED) before downstream use | BLOCK |
| VAL-006 | MedDRA version consistent across all coded terms | REJECT |

---

## Error Handling

- No match found → queue for manual coding (no auto-reject)
- Ambiguous match → queue for medical coder review
- MedDRA version mismatch → REJECT with error "meddra_version_inconsistent"
- WHO Drug lookup failure → QUARANTINE, retry with alternate search
- Review timeout (>48h) → escalate to coding lead
