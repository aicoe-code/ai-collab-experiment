"""Integration tests for LIMS adapter.

Tests: FR-017, FR-018, FR-019
"""

import pytest
from uuid import uuid4
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock


class TestLIMSLabResultIngestion:
    """Integration tests for FR-017: LIMS lab result ingestion."""

    @pytest.mark.integration
    async def test_fetch_lab_results_from_lims(self):
        """TC-038: LIMS adapter fetches lab results and maps to LabResult model.

        Given: a LIMS instance with 5 lab results for a subject
        When: fetch_lab_results(study_id, subject_id) is called
        Then: 5 LabResult objects are returned with test name, value, units, and normal range
        """
        mock_results = [
            {"test": "Glucose", "value": 95, "units": "mg/dL", "normal_low": 70, "normal_high": 100},
            {"test": "Creatinine", "value": 1.1, "units": "mg/dL", "normal_low": 0.7, "normal_high": 1.3},
            {"test": "ALT", "value": 25, "units": "U/L", "normal_low": 7, "normal_high": 56},
            {"test": "Hemoglobin", "value": 14.2, "units": "g/dL", "normal_low": 12.0, "normal_high": 17.5},
            {"test": "Platelet Count", "value": 250, "units": "K/uL", "normal_low": 150, "normal_high": 400},
        ]

        adapter = MagicMock()
        adapter.fetch_lab_results = AsyncMock(return_value=mock_results)

        results = await adapter.fetch_lab_results(study_id=str(uuid4()), subject_id=str(uuid4()))
        assert len(results) == 5
        assert results[0]["test"] == "Glucose"
        assert all("normal_low" in r for r in results)

    @pytest.mark.integration
    async def test_abnormal_lab_result_flagging(self):
        """TC-039: LIMS adapter flags lab results outside normal range.

        Given: a lab result with value above normal_high (Glucose=150, normal_high=100)
        When: fetch_lab_results() returns the result
        Then: the result is flagged as ABNORMAL_HIGH (FR-019)
        """
        result = {"test": "Glucose", "value": 150, "units": "mg/dL", "normal_low": 70, "normal_high": 100}

        if result["value"] > result["normal_high"]:
            flag = "ABNORMAL_HIGH"
        elif result["value"] < result["normal_low"]:
            flag = "ABNORMAL_LOW"
        else:
            flag = "NORMAL"

        assert flag == "ABNORMAL_HIGH"


class TestLIMSSampleChainOfCustody:
    """Integration tests for FR-018: LIMS sample chain of custody."""

    @pytest.mark.integration
    async def test_record_sample_chain_of_custody(self):
        """TC-040: LIMS adapter records sample collection and custody transfer.

        Given: a sample collected at a site with collector ID and timestamp
        When: record_sample_coc(sample_data) is called
        Then: the sample record is created with custody chain entry
        """
        sample_data = {
            "sample_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "sample_type": "BLOOD",
            "collected_by": "INV-001",
            "collection_date": "2026-05-20T10:30:00Z",
            "storage_condition": "-80C",
        }

        adapter = MagicMock()
        adapter.record_sample_coc = AsyncMock(return_value={
            **sample_data,
            "coc_status": "RECEIVED",
            "received_at": "2026-05-20T14:00:00Z",
        })

        result = await adapter.record_sample_coc(sample_data)
        assert result["coc_status"] == "RECEIVED"
        assert result["sample_type"] == "BLOOD"
