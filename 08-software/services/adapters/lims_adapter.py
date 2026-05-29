"""LIMS Adapter — integration with Laboratory Information Management Systems.

Implements: FR-018 (Lab Data Management), TR-022
Supports: Medidata Rave Lab, Covance LIMS, ICON LIMS
Protocol: REST API with API key authentication
"""

from __future__ import annotations

from typing import Any

import httpx

from services.adapters.base_adapter import BaseAdapter
from shared.models.lab_result import LabResult, LabResultStatus
from shared.models.subject import Subject
from shared.utils.config import get_settings
from shared.utils.logging import get_logger
from shared.utils.errors import ExternalSystemError

logger = get_logger(__name__)


class LIMSAdapter(BaseAdapter):
    """Adapter for Laboratory Information Management System (LIMS) integration.

    Fetches lab results, specimen tracking data, and reference ranges
    from the configured LIMS platform.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self._base_url = base_url or settings.lims_base_url
        self._api_key = api_key or settings.lims_api_key
        self._client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        """Establish HTTP connection to LIMS."""
        logger.info("Connecting to LIMS: %s", self._base_url)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "X-API-Key": self._api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        healthy = await self.health_check()
        if not healthy:
            raise ExternalSystemError("LIMS", "Connection health check failed")
        logger.info("Connected to LIMS")

    async def disconnect(self) -> None:
        """Close HTTP connection to LIMS."""
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("Disconnected from LIMS")

    async def health_check(self) -> bool:
        """Check LIMS system health endpoint."""
        if not self._client:
            return False
        try:
            response = await self._client.get("/health")
            return response.status_code == 200
        except httpx.HTTPError as e:
            logger.warning("LIMS health check failed: %s", e)
            return False

    async def fetch_subjects(self, study_id: str) -> list[Subject]:
        """Fetch subjects from LIMS (limited to subjects with lab data).

        Args:
            study_id: Study identifier.

        Returns:
            List of Subject models.
        """
        # LIMS typically doesn't own subject data; this is a pass-through
        logger.debug("LIMS does not own subject data; use EDC adapter instead")
        return []

    async def push_data(self, entity_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Push data to LIMS (e.g., kit assignments, specimen metadata).

        Args:
            entity_type: Entity type.
            payload: Data to push.

        Returns:
            LIMS acknowledgment response.
        """
        if not self._client:
            raise ExternalSystemError("LIMS", "Not connected")

        logger.info("Pushing %s to LIMS", entity_type)
        try:
            response = await self._client.post(f"/{entity_type}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ExternalSystemError("LIMS", f"Failed to push {entity_type}: {e}")

    async def fetch_lab_results(
        self, study_id: str, subject_id: str, visit: str | None = None
    ) -> list[LabResult]:
        """Fetch lab results for a subject from LIMS.

        Args:
            study_id: Study identifier.
            subject_id: Subject identifier.
            visit: Optional visit filter.

        Returns:
            List of LabResult models mapped from LIMS data.
        """
        if not self._client:
            raise ExternalSystemError("LIMS", "Not connected")

        logger.info(
            "Fetching lab results from LIMS for study=%s, subject=%s, visit=%s",
            study_id, subject_id, visit,
        )
        try:
            params: dict[str, str] = {}
            if visit:
                params["visit"] = visit
            response = await self._client.get(
                f"/studies/{study_id}/subjects/{subject_id}/results",
                params=params,
            )
            response.raise_for_status()
            # TODO: Map LIMS response to LabResult models
            return []
        except httpx.HTTPError as e:
            raise ExternalSystemError("LIMS", f"Failed to fetch lab results: {e}")
