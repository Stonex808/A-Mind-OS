from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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

    BASE_SCHEMA_NAME = "envelope.v1.schema.json"
    SYSTEM_CONTRACTS_DIR = Path("/etc/refocus/contracts")

    def __init__(self, contracts_dir: Path | None = None) -> None:
        self.contracts_dir = contracts_dir or self._default_contracts_dir()
        self._schemas = self._load_schemas()

    @classmethod
    def _default_contracts_dir(cls) -> Path:
        repo_root = Path(__file__).resolve().parents[2]
        dev_contracts_dir = repo_root / "config" / "contracts"
        if dev_contracts_dir.exists():
            return dev_contracts_dir
        return cls.SYSTEM_CONTRACTS_DIR

    def _load_schemas(self) -> dict[str, dict[str, Any]]:
        if not self.contracts_dir.exists():
            raise FileNotFoundError(f"Contracts directory not found: {self.contracts_dir}")

        schemas: dict[str, dict[str, Any]] = {}
        for schema_path in sorted(self.contracts_dir.glob("*.schema.json")):
            with schema_path.open("r", encoding="utf-8") as handle:
                schemas[schema_path.name] = json.load(handle)

        if self.BASE_SCHEMA_NAME not in schemas:
            raise FileNotFoundError(f"Missing required base schema: {self.BASE_SCHEMA_NAME}")

        return schemas

    def available_contracts(self) -> list[str]:
        """Return the service schema filenames available for dispatch validation."""

        return sorted(
            contract_name
            for contract_name in self._schemas
            if contract_name != self.BASE_SCHEMA_NAME
        )

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
        if contract_name == self.BASE_SCHEMA_NAME:
            raise ContractValidationError(
                f"'{self.BASE_SCHEMA_NAME}' is the base envelope schema and cannot be used as a dispatch contract. "
                f"Choose one of: {', '.join(self.available_contracts())}"
            )

        self._validate_with_schema(envelope, self.BASE_SCHEMA_NAME)
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
        try:
            from jsonschema import Draft202012Validator, FormatChecker
            from jsonschema.exceptions import ValidationError
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Contract validation requires the optional 'jsonschema' dependency. "
                "Install it with `pip install jsonschema`."
            ) from exc

        schema = self._schemas.get(contract_name)
        if schema is None:
            available = ", ".join(self.available_contracts())
            raise ContractValidationError(f"Unknown contract '{contract_name}'. Available: {available}")

        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(envelope), key=lambda error: list(error.path))
        if errors:
            raise ContractValidationError(self._format_errors(contract_name, errors, ValidationError))

    @staticmethod
    def _format_errors(contract_name: str, errors: list[Any], validation_error_type: type[Any]) -> str:
        formatted: list[str] = []
        for error in errors:
            if not isinstance(error, validation_error_type):
                continue
            location = ".".join(str(part) for part in error.path) or "<root>"
            formatted.append(f"{contract_name}::{location}: {error.message}")
        return " | ".join(formatted)


__all__ = [
    "ContractValidationError",
    "ContractValidator",
    "ValidationResult",
]
