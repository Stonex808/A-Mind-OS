"""Local persistence configuration and sensitive-content safeguards.

This module is the single boundary for paths, retention settings, and data
sanitization. It is standard-library only and safe to import offline.
"""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "refocus-os.toml"
REDACTION_TEXT = "[REDACTED-SENSITIVE]"
VALID_SENSITIVE_MODES = frozenset({"off", "redact", "refuse"})

_SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("password_assignment", re.compile(r"\b(password|passwd|pwd)\b\s*[:=]\s*\S+", re.IGNORECASE)),
    ("api_key_assignment", re.compile(r"\b(api[-_ ]?key|token|secret)\b\s*[:=]\s*\S+", re.IGNORECASE)),
    ("bearer_token", re.compile(r"\bbearer\s+[a-z0-9._\-]+", re.IGNORECASE)),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("card_number", re.compile(r"\b(?:\d[ -]*?){13,19}\b")),
)


class PersistenceConfigurationError(ValueError):
    """Raised when persistence configuration is invalid or ambiguous."""


class SensitiveContentError(ValueError):
    """Raised when ``refuse`` mode detects sensitive content."""


@dataclass(frozen=True)
class MemoryPersistenceSettings:
    semantic_dir: Path
    episodic_dir: Path
    procedural_dir: Path
    sensitive_content_mode: str


@dataclass(frozen=True)
class DemoPersistenceSettings:
    data_dir: Path
    runs_dir: Path
    db_path: Path
    memory_dir: Path
    sensitive_content_mode: str
    retention_days: int
    max_run_artifacts: int


def load_memory_persistence_settings(
    *,
    memory_root: str | Path | None = None,
    sensitive_content_mode: str | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
    environ: Mapping[str, str] | None = None,
) -> MemoryPersistenceSettings:
    env = os.environ if environ is None else environ
    config = _load_local_persistence_config(config_path)
    storage = _mapping(config.get("storage"), "local_persistence.storage")
    sensitive = _mapping(config.get("sensitive_content"), "local_persistence.sensitive_content")

    if memory_root is not None:
        root = _resolve_path(memory_root, config_path)
        semantic_dir = root / "semantic_local"
        episodic_dir = root / "episodic_local"
        procedural_dir = root / "procedural"
    else:
        semantic_dir = _resolve_path(
            env.get("REFOCUS_MEMORY_SEMANTIC_DIR") or storage.get("semantic_dir") or "data/user/memory/semantic_local",
            config_path,
        )
        episodic_dir = _resolve_path(
            env.get("REFOCUS_MEMORY_EPISODIC_DIR") or storage.get("episodic_dir") or "data/user/memory/episodic_local",
            config_path,
        )
        procedural_dir = _resolve_path(
            env.get("REFOCUS_MEMORY_PROCEDURAL_DIR") or storage.get("procedural_dir") or "data/user/memory/procedural",
            config_path,
        )

    mode = _normalize_sensitive_mode(
        sensitive_content_mode
        or env.get("REFOCUS_SENSITIVE_CONTENT_MODE")
        or _string_or_none(sensitive.get("mode"))
        or "redact"
    )
    return MemoryPersistenceSettings(semantic_dir, episodic_dir, procedural_dir, mode)


def load_demo_persistence_settings(
    *,
    data_dir: str | Path | None = None,
    memory_dir: str | Path | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
    environ: Mapping[str, str] | None = None,
) -> DemoPersistenceSettings:
    env = os.environ if environ is None else environ
    config = _load_local_persistence_config(config_path)
    demo = _mapping(config.get("demo"), "local_persistence.demo")
    sensitive = _mapping(config.get("sensitive_content"), "local_persistence.sensitive_content")

    data_override = data_dir or env.get("REFOCUS_DEMO_DATA_DIR")
    explicit_data_dir = data_override is not None
    resolved_data_dir = _resolve_path(
        data_override or demo.get("data_dir") or "data/demo",
        config_path,
    )
    runs_default: str | Path = (
        resolved_data_dir / "runs"
        if explicit_data_dir
        else demo.get("runs_dir") or resolved_data_dir / "runs"
    )
    db_default: str | Path = (
        resolved_data_dir / "orchestrator.db"
        if explicit_data_dir
        else demo.get("db_path") or resolved_data_dir / "orchestrator.db"
    )

    runs_dir = _resolve_path(env.get("REFOCUS_DEMO_RUNS_DIR") or runs_default, config_path)
    db_path = _resolve_path(env.get("REFOCUS_DEMO_DB_PATH") or db_default, config_path)
    resolved_memory_dir = _resolve_path(
        memory_dir or env.get("REFOCUS_DEMO_MEMORY_ROOT") or resolved_data_dir / "memory",
        config_path,
    )
    mode = _normalize_sensitive_mode(
        env.get("REFOCUS_SENSITIVE_CONTENT_MODE")
        or _string_or_none(demo.get("sensitive_content_mode"))
        or _string_or_none(sensitive.get("mode"))
        or "redact"
    )
    retention_days = _nonnegative_int(
        env.get("REFOCUS_RETENTION_DAYS") or demo.get("retention_days", 7),
        "local_persistence.demo.retention_days",
    )
    max_run_artifacts = _nonnegative_int(
        env.get("REFOCUS_MAX_RUN_ARTIFACTS") or demo.get("max_run_artifacts", 50),
        "local_persistence.demo.max_run_artifacts",
    )
    return DemoPersistenceSettings(
        data_dir=resolved_data_dir,
        runs_dir=runs_dir,
        db_path=db_path,
        memory_dir=resolved_memory_dir,
        sensitive_content_mode=mode,
        retention_days=retention_days,
        max_run_artifacts=max_run_artifacts,
    )


def sanitize_for_local_persistence(value: Any, mode: str) -> Any:
    """Return a JSON-compatible value with obvious secrets handled by policy."""

    normalized_mode = _normalize_sensitive_mode(mode)
    if normalized_mode == "off":
        return value
    if isinstance(value, str):
        return _sanitize_string(value, normalized_mode)
    if isinstance(value, list):
        return [sanitize_for_local_persistence(item, normalized_mode) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_for_local_persistence(item, normalized_mode) for item in value)
    if isinstance(value, dict):
        return {
            sanitize_for_local_persistence(key, normalized_mode) if isinstance(key, str) else key:
            sanitize_for_local_persistence(item, normalized_mode)
            for key, item in value.items()
        }
    return value


def _sanitize_string(value: str, mode: str) -> str:
    sanitized = value
    matches: list[str] = []
    for name, pattern in _SENSITIVE_PATTERNS:
        if pattern.search(sanitized):
            matches.append(name)
            sanitized = pattern.sub(REDACTION_TEXT, sanitized)
    if matches and mode == "refuse":
        kinds = ", ".join(sorted(set(matches)))
        raise SensitiveContentError(f"refusing to persist sensitive content ({kinds})")
    return sanitized


def _load_local_persistence_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}
    try:
        with config_path.open("rb") as handle:
            payload = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise PersistenceConfigurationError(f"invalid TOML in {config_path}: {exc}") from exc
    return _mapping(payload.get("local_persistence"), "local_persistence")


def _resolve_path(value: str | Path, config_path: Path) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (config_path.parent.parent / candidate).resolve()


def _normalize_sensitive_mode(value: str) -> str:
    mode = value.strip().lower()
    if mode not in VALID_SENSITIVE_MODES:
        allowed = ", ".join(sorted(VALID_SENSITIVE_MODES))
        raise PersistenceConfigurationError(f"sensitive-content mode must be one of: {allowed}")
    return mode


def _nonnegative_int(value: Any, label: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise PersistenceConfigurationError(f"{label} must be a non-negative integer") from exc
    if parsed < 0:
        raise PersistenceConfigurationError(f"{label} must be a non-negative integer")
    return parsed


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PersistenceConfigurationError(f"{label} must be a table")
    return value


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


__all__ = [
    "DemoPersistenceSettings",
    "MemoryPersistenceSettings",
    "PersistenceConfigurationError",
    "REDACTION_TEXT",
    "SensitiveContentError",
    "load_demo_persistence_settings",
    "load_memory_persistence_settings",
    "sanitize_for_local_persistence",
]
