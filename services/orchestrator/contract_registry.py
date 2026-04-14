"""Deterministic local contract loading and validation for orchestrator agent registration.

This module is intentionally stdlib-only so contract validation works offline and does
not require network access or third-party schema packages.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SYSTEM_CONTRACT_DIR = Path("/etc/refocus/contracts")
DEV_CONTRACT_DIR = Path(__file__).resolve().parents[2] / "config" / "contracts"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
CONTRACT_VERSION_RE = re.compile(r"^contract/v(0|[1-9]\d*)\.(0|[1-9]\d*)$")
VALID_AGENT_ROLES = {"orchestrator", "verifier", "worker"}
VALID_TOOL_CATEGORIES = {
    "memory.read",
    "memory.write",
    "ipc.unix",
    "planner.dag",
    "verification.schema",
    "verification.regex",
    "verification.logic",
    "filesystem.read",
    "filesystem.write",
    "process.inspect",
}
VALID_SYSCALL_CATEGORIES = {
    "none",
    "read",
    "write",
    "metadata",
    "ipc",
    "process",
}
VALID_VERIFIER_STAGES = {"pre_registration", "pre_execution", "post_execution"}


class ContractValidationError(ValueError):
    """Raised when a contract file is malformed or unsafe."""


@dataclass(frozen=True)
class AgentContract:
    source_path: Path
    payload: dict[str, Any]

    @property
    def agent_name(self) -> str:
        return str(self.payload["agent"]["name"])

    @property
    def role(self) -> str:
        return str(self.payload["agent"]["role"])

    @property
    def version(self) -> str:
        return str(self.payload["version"])


class ContractRegistry:
    """Loads validated contracts before agents are considered registerable."""

    def __init__(self, search_roots: Iterable[Path] | None = None) -> None:
        if search_roots is None:
            search_roots = (SYSTEM_CONTRACT_DIR, DEV_CONTRACT_DIR)
        self.search_roots = tuple(Path(root) for root in search_roots)

    def discover_contract_files(self) -> list[Path]:
        files: list[Path] = []
        seen: set[Path] = set()
        for root in self.search_roots:
            if not root.exists() or not root.is_dir():
                continue
            for path in sorted(root.glob("*.json")):
                resolved = path.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                files.append(path)
        return files

    def load_contracts(self) -> list[AgentContract]:
        contracts: list[AgentContract] = []
        seen_names: dict[str, Path] = {}
        for path in self.discover_contract_files():
            contract = self._load_contract(path)
            existing = seen_names.get(contract.agent_name)
            if existing is not None:
                raise ContractValidationError(
                    f"duplicate contract for agent '{contract.agent_name}' found in {existing} and {path}"
                )
            seen_names[contract.agent_name] = path
            contracts.append(contract)
        return contracts

    def contracts_for_registration(self) -> dict[str, dict[str, Any]]:
        registerable: dict[str, dict[str, Any]] = {}
        for contract in self.load_contracts():
            registerable[contract.agent_name] = {
                "role": contract.role,
                "version": contract.version,
                "source_path": str(contract.source_path),
                "handshake": contract.payload["registration"],
                "budgets": contract.payload["budgets"],
                "verifier_hooks": contract.payload["verifier_hooks"],
            }
        return registerable

    def _load_contract(self, path: Path) -> AgentContract:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ContractValidationError(f"{path}: invalid JSON ({exc})") from exc

        validate_contract_payload(payload, source=path)
        return AgentContract(source_path=path, payload=payload)


def validate_contract_payload(payload: dict[str, Any], *, source: Path | None = None) -> None:
    label = str(source) if source is not None else "<contract>"
    if not isinstance(payload, dict):
        raise ContractValidationError(f"{label}: top-level contract must be a JSON object")

    _require_keys(
        payload,
        label,
        [
            "contract_version",
            "version",
            "agent",
            "description",
            "input_schema",
            "output_schema",
            "permissions",
            "budgets",
            "verifier_hooks",
            "registration",
        ],
    )

    _require_semver(payload["version"], f"{label}: version")
    _require_regex(payload["contract_version"], CONTRACT_VERSION_RE, f"{label}: contract_version")
    _require_non_empty_string(payload["description"], f"{label}: description")

    agent = payload["agent"]
    _require_keys(agent, f"{label}: agent", ["name", "role", "service", "summary"])
    _require_slug(agent["name"], f"{label}: agent.name")
    _require_in(agent["role"], VALID_AGENT_ROLES, f"{label}: agent.role")
    _require_non_empty_string(agent["service"], f"{label}: agent.service")
    _require_non_empty_string(agent["summary"], f"{label}: agent.summary")

    _validate_schema(payload["input_schema"], f"{label}: input_schema")
    _validate_schema(payload["output_schema"], f"{label}: output_schema")

    permissions = payload["permissions"]
    _require_keys(permissions, f"{label}: permissions", ["tools", "syscalls"])
    tools = permissions["tools"]
    if not isinstance(tools, list) or not tools:
        raise ContractValidationError(f"{label}: permissions.tools must be a non-empty array")
    for tool in tools:
        _require_in(tool, VALID_TOOL_CATEGORIES, f"{label}: permissions.tools[]")

    syscalls = permissions["syscalls"]
    if not isinstance(syscalls, list) or not syscalls:
        raise ContractValidationError(f"{label}: permissions.syscalls must be a non-empty array")
    for category in syscalls:
        _require_in(category, VALID_SYSCALL_CATEGORIES, f"{label}: permissions.syscalls[]")

    budgets = payload["budgets"]
    _require_keys(
        budgets,
        f"{label}: budgets",
        ["token_budget", "time_budget_ms", "max_depth", "max_memory_mb"],
    )
    for key in ("token_budget", "time_budget_ms", "max_depth", "max_memory_mb"):
        value = budgets[key]
        if not isinstance(value, int) or value <= 0:
            raise ContractValidationError(f"{label}: budgets.{key} must be a positive integer")

    hooks = payload["verifier_hooks"]
    if not isinstance(hooks, list) or not hooks:
        raise ContractValidationError(f"{label}: verifier_hooks must be a non-empty array")
    for index, hook in enumerate(hooks):
        hook_label = f"{label}: verifier_hooks[{index}]"
        _require_keys(hook, hook_label, ["stage", "verifier", "on_failure"])
        _require_in(hook["stage"], VALID_VERIFIER_STAGES, f"{hook_label}.stage")
        _require_non_empty_string(hook["verifier"], f"{hook_label}.verifier")
        _require_in(hook["on_failure"], {"reject", "quarantine", "log_only"}, f"{hook_label}.on_failure")

    registration = payload["registration"]
    _require_keys(registration, f"{label}: registration", ["requires_contract_validation", "handshake", "attestation"])
    if registration["requires_contract_validation"] is not True:
        raise ContractValidationError(f"{label}: registration.requires_contract_validation must be true")
    _require_non_empty_string(registration["handshake"], f"{label}: registration.handshake")
    _require_non_empty_string(registration["attestation"], f"{label}: registration.attestation")


def _validate_schema(schema: Any, label: str) -> None:
    if not isinstance(schema, dict):
        raise ContractValidationError(f"{label} must be an object")
    schema_type = schema.get("type")
    if schema_type != "object":
        raise ContractValidationError(f"{label}.type must be 'object'")
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, dict) or not properties:
        raise ContractValidationError(f"{label}.properties must be a non-empty object")
    if not isinstance(required, list):
        raise ContractValidationError(f"{label}.required must be an array")
    if schema.get("additionalProperties") is not False:
        raise ContractValidationError(f"{label}.additionalProperties must be false")
    for name in required:
        if name not in properties:
            raise ContractValidationError(f"{label}.required contains unknown property '{name}'")
    for name, prop in properties.items():
        if not isinstance(prop, dict):
            raise ContractValidationError(f"{label}.properties.{name} must be an object")
        prop_type = prop.get("type")
        if prop_type not in {"string", "integer", "number", "boolean", "array", "object"}:
            raise ContractValidationError(
                f"{label}.properties.{name}.type must be one of string/integer/number/boolean/array/object"
            )
        if prop_type == "array" and "items" not in prop:
            raise ContractValidationError(f"{label}.properties.{name}.items is required for array types")


def _require_keys(value: Any, label: str, keys: list[str]) -> None:
    if not isinstance(value, dict):
        raise ContractValidationError(f"{label} must be an object")
    missing = [key for key in keys if key not in value]
    if missing:
        raise ContractValidationError(f"{label} missing required keys: {', '.join(missing)}")


def _require_non_empty_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{label} must be a non-empty string")


def _require_semver(value: Any, label: str) -> None:
    _require_regex(value, SEMVER_RE, label)


def _require_regex(value: Any, pattern: re.Pattern[str], label: str) -> None:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ContractValidationError(f"{label} must match {pattern.pattern}")


def _require_in(value: Any, options: set[str], label: str) -> None:
    if value not in options:
        raise ContractValidationError(f"{label} must be one of: {', '.join(sorted(options))}")


def _require_slug(value: Any, label: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[a-z][a-z0-9_]*", value) is None:
        raise ContractValidationError(f"{label} must be a lowercase slug using letters, numbers, and underscores")
