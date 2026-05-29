"""CDOS custom exception hierarchy.

Implements: TR-011 (Error Handling)
Provides structured error types following RFC 9457 (Problem Details).
"""

from __future__ import annotations

from typing import Any


class CDOSError(Exception):
    """Base exception for all CDOS application errors.

    Attributes:
        message: Human-readable error description.
        error_code: Machine-readable error code.
        details: Additional context about the error.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "CDOS_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Serialize to RFC 9457 Problem Details format."""
        return {
            "type": f"https://cdos.io/errors/{self.error_code.lower()}",
            "title": self.error_code.replace("_", " ").title(),
            "detail": self.message,
            **self.details,
        }


class NotFoundError(CDOSError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self, resource_type: str, resource_id: str, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id, **(details or {})},
        )


class ValidationError(CDOSError):
    """Raised when input data fails validation rules."""

    def __init__(
        self, message: str, errors: list[dict[str, Any]] | None = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"validation_errors": errors or []},
        )


class ExternalSystemError(CDOSError):
    """Raised when communication with an external system fails.

    Covers EDC, LIMS, Safety, IWRS, and other integrated systems.
    """

    def __init__(
        self, system_name: str, message: str, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=f"External system error ({system_name}): {message}",
            error_code="EXTERNAL_SYSTEM_ERROR",
            details={"system": system_name, **(details or {})},
        )


class AuthorizationError(CDOSError):
    """Raised when a user lacks required permissions."""

    def __init__(
        self, message: str = "Insufficient permissions", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message, error_code="AUTHORIZATION_ERROR", details=details
        )


class ConflictError(CDOSError):
    """Raised when an operation conflicts with current state."""

    def __init__(
        self, message: str, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message, error_code="CONFLICT_ERROR", details=details
        )
