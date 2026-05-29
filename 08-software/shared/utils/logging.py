"""CDOS structured logging configuration.

Implements: TR-010 (Observability - Logging)
Provides JSON-structured log output for production,
human-readable output for development.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from shared.utils.config import get_settings


class CDOSFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data  # type: ignore[attr-defined]
        return str(log_entry)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name.

    Args:
        name: Module or component name (typically __name__).

    Returns:
        Configured logging.Logger instance.
    """
    settings = get_settings()
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if settings.debug:
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                )
            )
        else:
            handler.setFormatter(CDOSFormatter())
        logger.addHandler(handler)

    return logger
