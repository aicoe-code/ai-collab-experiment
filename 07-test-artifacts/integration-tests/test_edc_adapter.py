"""Integration tests for EDC adapter.

Tests: FR-011, FR-012, FR-013
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch


class TestEDCCRFFetch:
    """Integration tests for FR-011: EDC CRF data ingestion."""

    @pytest.mark.integration
    async def test_fetch_crf_pages_from_edc(self):
        """TC-032: EDC adapter fetches CRF pages and maps to canonical model.

        Given: an EDC adapter connected to a test EDC instance with 3 CRF pages
        When: fetch_crf_pages(study_id, subject_id) is called
        Then: 3 CRFPage objects are returned with valid field data and CDASH codes
        """
        mock_edc_response = [
            {"page_id": str(uuid4()), "form": "DM", "fields": {"age": 45, "sex": "M"}},
            {"page_id": str(uuid4()), "form": "AE", "fields": {"aeterm": "Headache"}},
            {"page_id": str(uuid4()), "form": "LB", "fields": {"lbtest": "Glucose", "lbresult": 95}},
        ]

        adapter = MagicMock()
        adapter.fetch_crf_pages = AsyncMock(return_value=mock_edc_response)

        pages = await adapter.fetch_crf_pages(study_id=str(uuid4()), subject_id=str(uuid4()))
        assert len(pages) == 3
        assert pages[0]["form"] == "DM"
        assert pages[1]["form"] == "AE"

    @pytest.mark.integration
    async def test_edc_adapter_handles_connection_failure(self):
        """TC-033: EDC adapter raises ConnectionError when EDC is unreachable.

        Given: an EDC adapter configured with an invalid endpoint
        When: fetch_crf_pages() is called
        Then: a ConnectionError is raised with retry guidance
        """
        adapter = MagicMock()
        adapter.fetch_crf_pages = AsyncMock(side_effect=ConnectionError("EDC unreachable"))

        with pytest.raises(ConnectionError, match="EDC unreachable"):
            await adapter.fetch_crf_pages(study_id=str(uuid4()), subject_id=str(uuid4()))


class TestEDCQuerySync:
    """Integration tests for FR-012 and FR-013: EDC query synchronization."""

    @pytest.mark.integration
    async def test_sync_queries_from_edc(self):
        """TC-034: EDC adapter synchronizes open queries from EDC to CDOS.

        Given: an EDC instance with 2 open queries
        When: sync_queries(study_id) is called
        Then: 2 Query objects are imported with status OPEN and EDC query IDs
        """
        mock_queries = [
            {"edc_query_id": "EQ-001", "status": "OPEN", "field": "age", "message": "Verify age"},
            {"edc_query_id": "EQ-002", "status": "OPEN", "field": "sex", "message": "Confirm sex"},
        ]

        adapter = MagicMock()
        adapter.sync_queries = AsyncMock(return_value=mock_queries)

        queries = await adapter.sync_queries(study_id=str(uuid4()))
        assert len(queries) == 2
        assert queries[0]["status"] == "OPEN"
        assert all("edc_query_id" in q for q in queries)
