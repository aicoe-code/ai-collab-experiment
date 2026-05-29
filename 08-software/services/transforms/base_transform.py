"""Base transform — abstract interface for all data transformations.

Implements: TR-030 (Data Transformation Engine)
Ensures consistent transform lifecycle, validation, and error reporting.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTransform(ABC):
    """Abstract base class for data transformation pipelines.

    Transforms convert data from source formats (e.g., EDC CDASH)
    to target formats (e.g., CDISC SDTM). Each transform handles
    a specific source→target mapping.
    """

    @property
    @abstractmethod
    def source_format(self) -> str:
        """Return the source data format identifier."""

    @property
    @abstractmethod
    def target_format(self) -> str:
        """Return the target data format identifier."""

    @abstractmethod
    async def validate_input(self, data: dict[str, Any]) -> list[str]:
        """Validate input data against source schema.

        Args:
            data: Source data to validate.

        Returns:
            List of validation error messages. Empty if valid.
        """

    @abstractmethod
    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Execute the transformation.

        Args:
            data: Source data conforming to source_format schema.

        Returns:
            Transformed data conforming to target_format schema.

        Raises:
            ValidationError: If transformation fails.
        """

    @abstractmethod
    async def transform_batch(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute transformation on a batch of records.

        Args:
            records: List of source data records.

        Returns:
            List of transformed data records.
        """
