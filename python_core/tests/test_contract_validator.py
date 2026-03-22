from __future__ import annotations

from pathlib import Path

import pytest

from python_core.refocus_core import ContractValidationError, ContractValidator


FIXTURES_DIR = Path(__file__).resolve().parents[2] / "config" / "contracts" / "examples"


@pytest.fixture()
def validator() -> ContractValidator:
    return ContractValidator()


def test_available_contracts_include_required_schemas(validator: ContractValidator) -> None:
    contracts = validator.available_contracts()
    assert "envelope.v1.schema.json" in contracts
    assert "orchestrator.envelope.v1.schema.json" in contracts
    assert "verifier.envelope.v1.schema.json" in contracts
    assert "langsec.envelope.v1.schema.json" in contracts


@pytest.mark.parametrize(
    ("fixture_name", "contract_name"),
    [
        ("orchestrator.valid.json", "orchestrator.envelope.v1.schema.json"),
        ("verifier.valid.json", "verifier.envelope.v1.schema.json"),
        ("langsec.valid.json", "langsec.envelope.v1.schema.json"),
    ],
)
def test_valid_examples_pass_validation(
    validator: ContractValidator,
    fixture_name: str,
    contract_name: str,
) -> None:
    envelope = validator.load_envelope(FIXTURES_DIR / fixture_name)
    result = validator.validate_before_dispatch(envelope, contract_name)
    assert result.contract_name == contract_name
    assert result.envelope_id == envelope["id"]


@pytest.mark.parametrize(
    ("fixture_name", "contract_name"),
    [
        ("orchestrator.invalid.json", "orchestrator.envelope.v1.schema.json"),
        ("verifier.invalid.json", "verifier.envelope.v1.schema.json"),
        ("langsec.invalid.json", "langsec.envelope.v1.schema.json"),
    ],
)
def test_invalid_examples_fail_validation(
    validator: ContractValidator,
    fixture_name: str,
    contract_name: str,
) -> None:
    envelope = validator.load_envelope(FIXTURES_DIR / fixture_name)
    with pytest.raises(ContractValidationError):
        validator.validate_before_dispatch(envelope, contract_name)
