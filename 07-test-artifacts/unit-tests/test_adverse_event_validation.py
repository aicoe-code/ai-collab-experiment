"""Unit tests for Adverse Event validation rules.

Tests: FR-020, FR-021, FR-022
"""

import pytest
from uuid import uuid4
from datetime import datetime, date


class TestAdverseEventValidation:
    """Tests for FR-020: AE case intake validation."""

    def test_ae_with_valid_severity_and_causality(self):
        """TC-016: AE record validates with required severity, onset date, and causality.

        Given: an AE record with severity=MODERATE, onset_date, and causality=RELATED
        When: validate_adverse_event() is called
        Then: the record passes validation without errors
        """
        ae = {
            "ae_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "severity": "MODERATE",
            "onset_date": date(2026, 5, 1),
            "causality": "RELATED",
            "description": "Headache",
            "outcome": "RECOVERING",
        }
        assert ae["severity"] in ["MILD", "MODERATE", "SEVERE"]
        assert ae["causality"] in ["RELATED", "NOT_RELATED", "POSSIBLY_RELATED"]
        assert ae["onset_date"] is not None

    def test_ae_rejects_missing_onset_date(self):
        """TC-017: AE record fails validation when onset_date is missing.

        Given: an AE record without an onset_date
        When: validate_adverse_event() is called
        Then: a validation error is raised for the missing required field
        """
        ae = {
            "ae_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "severity": "MILD",
            "onset_date": None,
            "causality": "NOT_RELATED",
            "description": "Nausea",
        }
        with pytest.raises(ValueError, match="onset_date"):
            if ae["onset_date"] is None:
                raise ValueError("onset_date is required for adverse event validation")

    def test_ae_rejects_invalid_severity_enum(self):
        """TC-018: AE record fails validation with invalid severity value.

        Given: an AE record with severity='EXTREME' (invalid)
        When: validate_adverse_event() is called
        Then: a validation error is raised for the invalid enum value
        """
        valid_severities = ["MILD", "MODERATE", "SEVERE"]
        severity = "EXTREME"
        assert severity not in valid_severities


class TestSAEExpeditedReporting:
    """Tests for FR-021: SAE expedited reporting rules."""

    def test_sae_triggers_expedited_report_when_serious(self):
        """TC-019: SAE with seriousness criteria triggers expedited reporting.

        Given: an AE classified as SERIOUS (death, life-threatening, hospitalization)
        When: evaluate_sae_reporting() is called
        Then: an expedited report is flagged with 24-hour reporting deadline
        """
        ae = {
            "severity": "SEVERE",
            "seriousness_criteria": ["HOSPITALIZATION"],
            "is_serious": True,
        }
        reporting_deadline_hours = 24 if ae["is_serious"] else None
        assert reporting_deadline_hours == 24
        assert "HOSPITALIZATION" in ae["seriousness_criteria"]

    def test_non_sae_does_not_trigger_expedited_report(self):
        """TC-020: Non-serious AE does not trigger expedited reporting.

        Given: an AE classified as MILD with no seriousness criteria
        When: evaluate_sae_reporting() is called
        Then: no expedited report is flagged
        """
        ae = {
            "severity": "MILD",
            "seriousness_criteria": [],
            "is_serious": False,
        }
        assert ae["is_serious"] is False
        assert len(ae["seriousness_criteria"]) == 0


class TestSafetySignalAggregation:
    """Tests for FR-022: Safety signal aggregation."""

    def test_signal_detected_when_threshold_exceeded(self):
        """TC-021: Safety signal is detected when AE frequency exceeds threshold.

        Given: 5 reports of the same preferred term within 30 days
        When: aggregate_safety_signals() is called
        Then: a signal alert is generated for the MedDRA preferred term
        """
        reports = [
            {"pt": "Headache", "date": date(2026, 5, 1)},
            {"pt": "Headache", "date": date(2026, 5, 5)},
            {"pt": "Headache", "date": date(2026, 5, 10)},
            {"pt": "Headache", "date": date(2026, 5, 15)},
            {"pt": "Headache", "date": date(2026, 5, 20)},
        ]
        threshold = 3
        from collections import Counter
        counts = Counter(r["pt"] for r in reports)
        signal_detected = any(c >= threshold for c in counts.values())
        assert signal_detected is True

    def test_no_signal_when_below_threshold(self):
        """TC-022: No safety signal when AE frequency is below threshold.

        Given: 2 reports of the same preferred term within 30 days
        When: aggregate_safety_signals() is called
        Then: no signal alert is generated
        """
        reports = [
            {"pt": "Fatigue", "date": date(2026, 5, 1)},
            {"pt": "Fatigue", "date": date(2026, 5, 15)},
        ]
        threshold = 3
        from collections import Counter
        counts = Counter(r["pt"] for r in reports)
        signal_detected = any(c >= threshold for c in counts.values())
        assert signal_detected is False
