"""Local-first contract validation for Refocus-OS envelopes.

This module validates IPC envelopes against the repository's versioned JSON
Schemas before dispatch. It uses only local files under ``config/contracts`` and
performs no network calls or telemetry.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError


class ContractValidationError(ValueError):
    """Raised when an envelope does not match the required local contract."""


@dataclass(frozen=True)
class ValidationResult:
    """Structured result for successful validation."""

    contract_name: str
    schema_path: Path
    envelope_id: str


class ContractValidator:
    """Load and validate versioned envelope contracts from local disk only."""

    def __init__(self, contracts_dir: Path | None = None) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        self.contracts_dir = contracts_dir or repo_root / "config" / "contracts"
        self._schemas = self._load_schemas()
        self._format_checker = FormatChecker()

    def _load_schemas(self) -> dict[str, dict[str, Any]]:
        if not self.contracts_dir.exists():
            raise FileNotFoundError(f"Contracts directory not found: {self.contracts_dir}")

        schemas: dict[str, dict[str, Any]] = {}
        for schema_path in sorted(self.contracts_dir.glob("*.schema.json")):
            with schema_path.open("r", encoding="utf-8") as handle:
                schemas[schema_path.name] = json.load(handle)

        if "envelope.v1.schema.json" not in schemas:
            raise FileNotFoundError("Missing required base schema: envelope.v1.schema.json")

        return schemas

    def available_contracts(self) -> list[str]:
        """Return the schema filenames available for dispatch validation."""

        return sorted(self._schemas)

    def load_envelope(self, envelope_path: Path) -> dict[str, Any]:
        """Load a JSON envelope fixture from disk."""

        with envelope_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def validate_envelope(self, envelope: dict[str, Any], contract_name: str) -> ValidationResult:
        """Validate an envelope against the base schema and a service contract.

        Parameters
        ----------
        envelope:
            Envelope payload already loaded into memory.
        contract_name:
            Exact contract filename, for example
            ``orchestrator.envelope.v1.schema.json``.
        """

        self._validate_with_schema(envelope, "envelope.v1.schema.json")
        self._validate_with_schema(envelope, contract_name)

        return ValidationResult(
            contract_name=contract_name,
            schema_path=self.contracts_dir / contract_name,
            envelope_id=str(envelope["id"]),
        )

    def validate_before_dispatch(self, envelope: dict[str, Any], contract_name: str) -> ValidationResult:
        """Validate and return a dispatch-safe result.

        This method is the expected bus/orchestrator entry point. It keeps the
        validator explicit so contributors can call it before any local message
        dispatch and avoid accepting malformed or policy-breaking envelopes.
        """

        return self.validate_envelope(envelope=envelope, contract_name=contract_name)

    def _validate_with_schema(self, envelope: dict[str, Any], contract_name: str) -> None:
        schema = self._schemas.get(contract_name)
        if schema is None:
            available = ", ".join(self.available_contracts())
            raise ContractValidationError(f"Unknown contract '{contract_name}'. Available: {available}")

        validator = Draft202012Validator(schema, format_checker=self._format_checker)
        errors = sorted(validator.iter_errors(envelope), key=lambda error: list(error.path))
        if errors:
            raise ContractValidationError(self._format_errors(contract_name, errors))

    @staticmethod
    def _format_errors(contract_name: str, errors: list[ValidationError]) -> str:
        formatted: list[str] = []
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            formatted.append(f"{contract_name}::{location}: {error.message}")
        return " | ".join(formatted)


__all__ = [
    "ContractValidationError",
    "ContractValidator",
    "ValidationResult",
]
