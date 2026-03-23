"""Structured logging helpers for Refocus-OS Python components."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - optional dependency
    import structlog  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback when structlog missing
    structlog = None  # type: ignore[assignment]


_STRUCTLOG_CONFIGURED = False


def _ensure_structlog_configured(service_name: str, log_dir: Optional[Path], level: str) -> logging.Logger:
    """Configure a structlog logger when structlog is available."""

    global _STRUCTLOG_CONFIGURED

    assert structlog is not None  # nosec: B101 - ensured by caller

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    if log_dir:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    if not _STRUCTLOG_CONFIGURED:
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        _STRUCTLOG_CONFIGURED = True

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{service_name}.log"
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(format="%(message)s", level=getattr(logging, level.upper(), logging.INFO), handlers=handlers)

    logger = structlog.get_logger(service_name)
    logger.info("logging_initialized", service=service_name, level=level)
    return logger


def setup_logging(service_name: str, log_dir: Optional[Path] = None, level: str = "INFO") -> logging.Logger:
    """Return a structured logger for the given service.

    Falls back to the standard library's :mod:`logging` when ``structlog`` is not
    available so that modules can be imported without optional dependencies.
    """

    if structlog is not None:
        return _ensure_structlog_configured(service_name, log_dir, level)

    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    logger = logging.getLogger(service_name)
    logger.info(
        "logging_initialized",
        extra={"service": service_name, "level": level, "adapter": "stdlib"},
    )
    return logger


__all__ = ["setup_logging"]
