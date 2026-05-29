"""EDC Adapter — integration with Electronic Data Capture systems.

Implements: FR-005 (EDC Integration), TR-021
Supports: Medidata Rave, Oracle InForm, Veeva Vault CDMS, Castor
Protocol: REST API with OAuth2 authentication
"""

from __future__ import annotations

from typing import Any

import httpx

from services.adapters.base_adapter import BaseAdapter
from shared.models.subject import Subject
from shared.utils.config import get_settings
from shared.utils.logging import get_logger
from shared.utils.errors import ExternalSystemError

logger = get_logger(__name__)


class EDCAdapter(BaseAdapter):
    """Adapter for Electronic Data Capture (EDC) system integration.

    Fetches CRF data, subject demographics, and visit schedules
    from the configured EDC platform.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self._base_url = base_url or settings.edc_base_url
        self._api_key = api_key or settings.edc_api_key
        self._client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        """Establish HTTP connection to EDC system."""
        logger.info("Connecting to EDC: %s", self._base_url)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        # Verify connectivity
        healthy = await self.health_check()
        if not healthy:
            raise ExternalSystemError("EDC", "Connection health check failed")
        logger.info("Connected to EDC")

    async def disconnect(self) -> None:
        """Close HTTP connection to EDC."""
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("Disconnected from EDC")

    async def health_check(self) -> bool:
        """Check EDC system health endpoint."""
        if not self._client:
            return False
        try:
            response = await self._client.get("/health")
            return response.status_code == 200
        except httpx.HTTPError as e:
            logger.warning("EDC health check failed: %s", e)
            return False

    async def fetch_subjects(self, study_id: str) -> list[Subject]:
        """Fetch subjects from EDC for a given study.

        Args:
            study_id: Study identifier in EDC.

        Returns:
            List of Subject models mapped from EDC data.

        Raises:
            ExternalSystemError: If API call fails.
        """
        if not self._client:
            raise ExternalSystemError("EDC", "Not connected")

        logger.info("Fetching subjects from EDC for study %s", study_id)
        try:
            response = await self._client.get(
                f"/studies/{study_id}/subjects",
                params={"status": "all"},
            )
            response.raise_for_status()
            data = response.json()
            # TODO: Map EDC-specific fields to canonical Subject model
            return []
        except httpx.HTTPError as e:
            raise ExternalSystemError("EDC", f"Failed to fetch subjects: {e}")

    async def push_data(self, entity_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Push data to EDC (e.g., queries, lab data).

        Args:
            entity_type: Entity type (query, lab_result, etc.).
            payload: Data to push.

        Returns:
            EDC acknowledgment response.
        """
        if not self._client:
            raise ExternalSystemError("EDC", "Not connected")

        logger.info("Pushing %s to EDC", entity_type)
        try:
            response = await self._client.post(f"/{entity_type}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ExternalSystemError("EDC", f"Failed to push {entity_type}: {e}")

    async def fetch_crf_data(
        self, study_id: str, subject_id: str, form_oid: str
    ) -> dict[str, Any]:
        """Fetch CRF page data for a subject.

        Args:
            study_id: Study identifier.
            subject_id: Subject identifier.
            form_oid: CRF form OID.

        Returns:
            CRF data dictionary.
        """
        if not self._client:
            raise ExternalSystemError("EDC", "Not connected")

        response = await self._client.get(
            f"/studies/{study_id}/subjects/{subject_id}/forms/{form_oid}"
        )
        response.raise_for_status()
        return response.json()
