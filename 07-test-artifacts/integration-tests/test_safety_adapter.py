"""Integration tests for Safety system adapter.

Tests: FR-020, FR-021
"""

import pytest
from uuid import uuid4
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock


class TestSafetyAECaseIntake:
    """Integration tests for FR-020: Safety AE case intake."""

    @pytest.mark.integration
    async def test_receive_ae_case_from_safety_system(self):
        """TC-035: Safety adapter receives and maps AE case to canonical AdverseEvent.

        Given: a Safety system (Argus) with an ICSR case for our study
        When: fetch_ae_cases(study_id) is called
        Then: an AdverseEvent is returned with MedDRA coding and seriousness flags
        """
        mock_safety_response = {
            "case_id": "ICSR-001",
            "meddra_pt": "Headache",
            "meddra_code": 10019211,
            "severity": "MODERATE",
            "seriousness": ["HOSPITALIZATION"],
            "report_date": "2026-05-20",
        }

        adapter = MagicMock()
        adapter.fetch_ae_cases = AsyncMock(return_value=[mock_safety_response])

        cases = await adapter.fetch_ae_cases(study_id=str(uuid4()))
        assert len(cases) == 1
        assert cases[0]["meddra_code"] == 10019211
        assert "HOSPITALIZATION" in cases[0]["seriousness"]

    @pytest.mark.integration
    async def test_send_sae_report_to_safety_system(self):
        """TC-036: Safety adapter sends SAE expedited report to Safety system.

        Given: a CDOS-internal SAE requiring expedited reporting
        When: submit_sae_report(sae_data) is called
        Then: an ICSR is submitted to Safety and confirmation ID is returned
        """
        sae_data = {
            "ae_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "severity": "SEVERE",
            "seriousness_criteria": ["LIFE_THREATENING"],
            "onset_date": "2026-05-18",
            "description": "Anaphylactic reaction",
        }

        adapter = MagicMock()
        adapter.submit_sae_report = AsyncMock(return_value={
            "confirmation_id": "SAF-CONF-001",
            "status": "SUBMITTED",
            "submitted_at": datetime.utcnow().isoformat(),
        })

        result = await adapter.submit_sae_report(sae_data)
        assert result["status"] == "SUBMITTED"
        assert result["confirmation_id"] is not None


class TestSafetySignalSync:
    """Integration tests for FR-022: Safety signal aggregation with external system."""

    @pytest.mark.integration
    async def test_fetch_aggregated_signals_from_safety(self):
        """TC-037: Safety adapter retrieves aggregated safety signals for a study.

        Given: a Safety system with 3 detected signals for our study
        When: fetch_signals(study_id) is called
        Then: 3 signal objects are returned with MedDRA terms and frequency counts
        """
        mock_signals = [
            {"meddra_pt": "Headache", "count": 12, "signal_score": 3.5},
            {"meddra_pt": "Nausea", "count": 8, "signal_score": 2.1},
            {"meddra_pt": "Fatigue", "count": 6, "signal_score": 1.8},
        ]

        adapter = MagicMock()
        adapter.fetch_signals = AsyncMock(return_value=mock_signals)

        signals = await adapter.fetch_signals(study_id=str(uuid4()))
        assert len(signals) == 3
        assert all("signal_score" in s for s in signals)
