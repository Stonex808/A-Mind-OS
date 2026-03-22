"""Refocus-OS Python core utilities."""

from __future__ import annotations

from .logging import setup_logging

__all__ = ["setup_logging", "ContractValidationError", "ContractValidator", "ValidationResult"]


def __getattr__(name: str):
    if name in {"ContractValidationError", "ContractValidator", "ValidationResult"}:
        from .contracts import ContractValidationError, ContractValidator, ValidationResult

        exports = {
            "ContractValidationError": ContractValidationError,
            "ContractValidator": ContractValidator,
            "ValidationResult": ValidationResult,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
from .audit import AuditEvent, LocalAuditStore
from .intent_security import (
    ExecutionPolicy,
    ExecutionRequest,
    IntentIngress,
    IntentRecord,
    IntentSanitizer,
    IntentSchemaValidator,
    IntentValidationError,
    SanitizationResult,
)
from .logging import setup_logging

__all__ = [
    "AuditEvent",
    "ExecutionPolicy",
    "ExecutionRequest",
    "IntentIngress",
    "IntentRecord",
    "IntentSanitizer",
    "IntentSchemaValidator",
    "IntentValidationError",
    "LocalAuditStore",
    "SanitizationResult",
    "setup_logging",
]
