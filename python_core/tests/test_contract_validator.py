from __future__ import annotations

import builtins
import importlib
import sys
from pathlib import Path

import pytest

from python_core.refocus_core import ContractValidationError, ContractValidator


FIXTURES_DIR = Path(__file__).resolve().parents[2] / "config" / "contracts" / "examples"


@pytest.fixture()
def validator() -> ContractValidator:
    return ContractValidator()


def test_available_contracts_include_required_schemas(validator: ContractValidator) -> None:
    contracts = validator.available_contracts()
    assert "envelope.v1.schema.json" not in contracts
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


def test_validate_before_dispatch_rejects_base_schema(validator: ContractValidator) -> None:
    envelope = validator.load_envelope(FIXTURES_DIR / "orchestrator.valid.json")

    with pytest.raises(ContractValidationError, match="cannot be used as a dispatch contract"):
        validator.validate_before_dispatch(envelope, "envelope.v1.schema.json")


def test_contract_validator_prefers_system_contracts_when_dev_copy_missing(tmp_path: Path) -> None:
    system_contracts = tmp_path / "etc" / "refocus" / "contracts"
    system_contracts.mkdir(parents=True)

    for schema_name in (
        "envelope.v1.schema.json",
        "orchestrator.envelope.v1.schema.json",
    ):
        source = FIXTURES_DIR.parents[0] / schema_name
        (system_contracts / schema_name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    original_system_dir = ContractValidator.SYSTEM_CONTRACTS_DIR
    ContractValidator.SYSTEM_CONTRACTS_DIR = system_contracts
    try:
        validator = ContractValidator(contracts_dir=ContractValidator.SYSTEM_CONTRACTS_DIR)
    finally:
        ContractValidator.SYSTEM_CONTRACTS_DIR = original_system_dir

    assert validator.contracts_dir == system_contracts
    assert validator.available_contracts() == ["orchestrator.envelope.v1.schema.json"]


def test_default_contracts_dir_falls_back_to_system_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    system_contracts = tmp_path / "etc" / "refocus" / "contracts"
    system_contracts.mkdir(parents=True)

    original_system_dir = ContractValidator.SYSTEM_CONTRACTS_DIR
    ContractValidator.SYSTEM_CONTRACTS_DIR = system_contracts

    original_exists = Path.exists

    def fake_exists(path: Path) -> bool:
        if path == Path(__file__).resolve().parents[2] / "config" / "contracts":
            return False
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", fake_exists)
    try:
        assert ContractValidator._default_contracts_dir() == system_contracts
    finally:
        ContractValidator.SYSTEM_CONTRACTS_DIR = original_system_dir


def test_package_init_does_not_import_jsonschema(monkeypatch: pytest.MonkeyPatch) -> None:
    module_name = "python_core.refocus_core"
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("jsonschema"):
            raise AssertionError("jsonschema should not be imported during package init")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    sys.modules.pop(module_name, None)
    module = importlib.import_module(module_name)

    assert module.setup_logging is not None
