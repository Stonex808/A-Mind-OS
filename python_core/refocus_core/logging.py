"""Idempotent structured logging for A-Mind-OS components."""

from __future__ import annotations

import logging
import json
from pathlib import Path
from typing import Any, Optional


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "service": record.name,
            "level": record.levelname.lower(),
            "event": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def setup_logging(service_name: str, log_dir: Optional[Path] = None, level: str = "INFO") -> logging.Logger:
    """Return one logger per service without modifying the process root logger."""

    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    target = str(Path(log_dir).resolve()) if log_dir else "stderr"
    if getattr(logger, "_a_mind_target", None) == target:
        return logger

    for existing in logger.handlers:
        existing.close()
    logger.handlers.clear()
    handler: logging.Handler
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(Path(log_dir) / f"{service_name}.jsonl", encoding="utf-8")
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    logger._a_mind_target = target  # type: ignore[attr-defined]
    return logger


__all__ = ["setup_logging"]
