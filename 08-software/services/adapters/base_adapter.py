"""Base adapter — abstract interface for all external system adapters.

Implements: TR-020 (Integration Patterns)
All concrete adapters (EDC, LIMS, Safety, etc.) extend this ABC.
Ensures consistent connection management, health checks, and error handling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from shared.models.subject import Subject
from shared.models.adverse_event import AdverseEvent
from shared.models.lab_result import LabResult


class BaseAdapter(ABC):
    """Abstract base class for external system adapters.

    Provides a standard lifecycle (connect, health_check, disconnect)
    and a standard data-fetch interface that concrete adapters implement.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the external system.

        Raises:
            ExternalSystemError: If connection cannot be established.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the external system."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the external system is reachable and healthy.

        Returns:
            True if system is healthy, False otherwise.
        """

    @abstractmethod
    async def fetch_subjects(self, study_id: str) -> list[Subject]:
        """Fetch subject records from the external system.

        Args:
            study_id: Study identifier to filter by.

        Returns:
            List of Subject models.
        """

    @abstractmethod
    async def push_data(self, entity_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Push data to the external system.

        Args:
            entity_type: Type of entity being pushed.
            payload: Data payload.

        Returns:
            Acknowledgment response from the external system.
        """
