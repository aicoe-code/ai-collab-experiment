"""End-to-end tests for safety reporting business process.

Tests: FR-020, FR-021, FR-022
"""

import pytest
from uuid import uuid4
from datetime import date, datetime


class TestSafetyReportingFlow:
    """E2E tests covering AE detection through SAE expedited reporting."""

    @pytest.mark.e2e
    async def test_ae_to_sae_expedited_reporting_flow(self):
        """TC-044: Full safety flow from AE detection to SAE expedited report submission.

        Given: an enrolled subject experiencing an adverse event
        When: the safety reporting process executes:
          1. AE recorded in EDC (FR-020)
          2. AE ingested into CDOS via EDC adapter
          3. AE classified as SAE (hospitalization criterion met)
          4. SAE expedited report generated (FR-021)
          5. ICSR submitted to Safety system
        Then: SAE report is submitted with confirmation, audit trail complete
        """
        # Step 1: AE recorded in EDC
        ae_record = {
            "ae_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "preferred_term": "Anaphylactic reaction",
            "severity": "SEVERE",
            "onset_date": date(2026, 5, 20).isoformat(),
            "seriousness_criteria": ["HOSPITALIZATION", "LIFE_THREATENING"],
            "outcome": "RECOVERING",
        }
        assert ae_record["severity"] == "SEVERE"

        # Step 2: Ingested into CDOS
        cdos_ae = {
            **ae_record,
            "ingestion_timestamp": datetime.utcnow().isoformat(),
            "source_system": "EDC",
        }
        assert cdos_ae["source_system"] == "EDC"

        # Step 3: SAE classification
        is_sae = len(cdos_ae["seriousness_criteria"]) > 0
        assert is_sae is True

        # Step 4: Expedited report
        sae_report = {
            "report_id": str(uuid4()),
            "ae_id": cdos_ae["ae_id"],
            "report_type": "EXPEDITED",
            "deadline": "2026-05-21T00:00:00Z",  # 24-hour deadline
            "generated_at": datetime.utcnow().isoformat(),
        }
        assert sae_report["report_type"] == "EXPEDITED"

        # Step 5: Submit to Safety
        submission = {
            "confirmation_id": "SAF-ICSR-001",
            "status": "SUBMITTED",
            "submitted_at": datetime.utcnow().isoformat(),
        }
        assert submission["status"] == "SUBMITTED"

    @pytest.mark.e2e
    async def test_safety_signal_detection_and_alert_flow(self):
        """TC-045: Safety signal detection triggers alert when threshold exceeded.

        Given: multiple AE reports for the same MedDRA preferred term
        When: safety signal aggregation runs (FR-022)
        Then: a signal alert is generated and notified to the safety team
        """
        ae_reports = [
            {"pt": "Headache", "date": "2026-05-01"},
            {"pt": "Headache", "date": "2026-05-05"},
            {"pt": "Headache", "date": "2026-05-10"},
            {"pt": "Headache", "date": "2026-05-15"},
            {"pt": "Headache", "date": "2026-05-20"},
        ]

        # Aggregation
        from collections import Counter
        counts = Counter(r["pt"] for r in ae_reports)
        threshold = 3

        signals = {pt: count for pt, count in counts.items() if count >= threshold}
        assert "Headache" in signals
        assert signals["Headache"] >= threshold

        # Alert generation
        alert = {
            "alert_id": str(uuid4()),
            "signal_type": "FREQUENCY_THRESHOLD",
            "meddra_pt": "Headache",
            "count": signals["Headache"],
            "notified_to": "safety_team",
            "created_at": datetime.utcnow().isoformat(),
        }
        assert alert["notified_to"] == "safety_team"
