"""Safety Adapter — integration with Pharmacovigilance / Safety systems.

Implements: FR-020 (Safety Reporting), TR-023
Supports: Argus Safety, ArisGlobal, Oracle AERS
Protocol: REST API with OAuth2 authentication
"""

from __future__ import annotations

from typing import Any

import httpx

from services.adapters.base_adapter import BaseAdapter
from shared.models.adverse_event import AdverseEvent
from shared.models.subject import Subject
from shared.utils.config import get_settings
from shared.utils.logging import get_logger
from shared.utils.errors import ExternalSystemError

logger = get_logger(__name__)


class SafetyAdapter(BaseAdapter):
    """Adapter for Safety / Pharmacovigilance system integration.

    Pushes adverse event reports (ICSR), handles SUSAR reporting,
    and retrieves expectedness assessments from the safety database.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self._base_url = base_url or settings.safety_base_url
        self._api_key = api_key or settings.safety_api_key
        self._client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        """Establish HTTP connection to Safety system."""
        logger.info("Connecting to Safety: %s", self._base_url)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        healthy = await self.health_check()
        if not healthy:
            raise ExternalSystemError("Safety", "Connection health check failed")
        logger.info("Connected to Safety system")

    async def disconnect(self) -> None:
        """Close HTTP connection to Safety system."""
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("Disconnected from Safety system")

    async def health_check(self) -> bool:
        """Check Safety system health endpoint."""
        if not self._client:
            return False
        try:
            response = await self._client.get("/health")
            return response.status_code == 200
        except httpx.HTTPError as e:
            logger.warning("Safety health check failed: %s", e)
            return False

    async def fetch_subjects(self, study_id: str) -> list[Subject]:
        """Fetch subjects from Safety system (subjects with AE reports).

        Args:
            study_id: Study identifier.

        Returns:
            List of Subject models.
        """
        if not self._client:
            raise ExternalSystemError("Safety", "Not connected")

        try:
            response = await self._client.get(f"/studies/{study_id}/subjects")
            response.raise_for_status()
            # TODO: Map safety system response to Subject models
            return []
        except httpx.HTTPError as e:
            raise ExternalSystemError("Safety", f"Failed to fetch subjects: {e}")

    async def push_data(self, entity_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Push data to Safety system.

        Args:
            entity_type: Entity type (typically 'icsr' for safety reports).
            payload: Data to push.

        Returns:
            Safety system acknowledgment.
        """
        if not self._client:
            raise ExternalSystemError("Safety", "Not connected")

        logger.info("Pushing %s to Safety system", entity_type)
        try:
            response = await self._client.post(f"/{entity_type}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ExternalSystemError("Safety", f"Failed to push {entity_type}: {e}")

    async def submit_icsr(self, ae: AdverseEvent) -> dict[str, Any]:
        """Submit an Individual Case Safety Report (ICSR) to the safety system.

        Implements: FR-020, SUSAR reporting workflow

        Args:
            ae: AdverseEvent to report.

        Returns:
            ICSR acknowledgment with case number.
        """
        if not self._client:
            raise ExternalSystemError("Safety", "Not connected")

        logger.info("Submitting ICSR for AE %s (SUSAR=%s)", ae.ae_id, ae.is_susar)
        icsr_payload = {
            "case_id": str(ae.ae_id),
            "study_id": str(ae.study_id),
            "subject_id": str(ae.subject_id),
            "term": ae.term,
            "meddra_code": ae.meddra_code,
            "severity": ae.severity.value,
            "seriousness": ae.seriousness.value,
            "onset_date": ae.onset_date.isoformat(),
            "narrative": ae.narrative,
            "is_susar": ae.is_susar,
        }
        try:
            response = await self._client.post("/icsr", json=icsr_payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ExternalSystemError("Safety", f"Failed to submit ICSR: {e}")
