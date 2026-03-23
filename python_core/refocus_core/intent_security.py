"""Local-first intent ingress security primitives.

These helpers provide the first concrete protections for user intents:
- schema validation at ingestion time
- conservative local sanitization
- structured, local audit logging
- explicit allowlist checks for any future execution path

The implementation is intentionally stdlib-only so it remains auditable,
offline-friendly, and easy to back up.
"""

from __future__ import annotations

import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .audit import AuditEvent, LocalAuditStore

_MAX_TEXT_LENGTH = 4000
_MAX_METADATA_ITEMS = 32
_MAX_METADATA_KEY_LENGTH = 64
_MAX_METADATA_VALUE_LENGTH = 512
_ALLOWED_SOURCES = {"hotkey", "ui", "voice", "api", "system"}
_SUSPICIOUS_PATTERNS = (
    r"ignore\s+(all|previous|prior)\s+instructions",
    r"developer\s+mode",
    r"system\s+prompt",
    r"sudo\b",
    r"rm\s+-rf",
    r"curl\s+.*\|\s*(sh|bash)",
    r"<script\b",
)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MULTI_BLANK_LINES = re.compile(r"\n{3,}")


class IntentValidationError(ValueError):
    """Raised when an intent payload fails schema or safety checks."""


@dataclass(frozen=True)
class SanitizationResult:
    """Output of local intent sanitization."""

    text: str
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class IntentRecord:
    """Validated intent payload ready for downstream planning."""

    intent_id: str
    source: str
    intent_text: str
    created_at: str
    metadata: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExecutionRequest:
    """A future command/tool execution request that must be allowlisted."""

    actor: str
    action_type: str
    action_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    intent_id: Optional[str] = None


class IntentSanitizer:
    """Normalize and locally sanitize free-form intent text."""

    def sanitize(self, text: Any) -> SanitizationResult:
        if not isinstance(text, str):
            raise IntentValidationError("intent_text must be a string")

        normalized = unicodedata.normalize("NFKC", text)
        cleaned = _CONTROL_CHARS.sub("", normalized.replace("\r\n", "\n").replace("\r", "\n"))
        cleaned = "\n".join(line.strip() for line in cleaned.split("\n"))
        cleaned = _MULTI_SPACE.sub(" ", cleaned)
        cleaned = _MULTI_BLANK_LINES.sub("\n\n", cleaned).strip()

        if not cleaned:
            raise IntentValidationError("intent_text cannot be empty after sanitization")
        if len(cleaned) > _MAX_TEXT_LENGTH:
            raise IntentValidationError(f"intent_text exceeds {_MAX_TEXT_LENGTH} characters")

        warnings = [
            "suspicious_pattern_detected"
            for pattern in _SUSPICIOUS_PATTERNS
            if re.search(pattern, cleaned, flags=re.IGNORECASE)
        ]
        if len(warnings) > 1:
            warnings = sorted(set(warnings))

        return SanitizationResult(text=cleaned, warnings=warnings)


class IntentSchemaValidator:
    """Strict schema validator for early intent ingestion."""

    def validate(self, payload: Mapping[str, Any]) -> IntentRecord:
        if not isinstance(payload, Mapping):
            raise IntentValidationError("intent payload must be a mapping")

        source = payload.get("source")
        if source not in _ALLOWED_SOURCES:
            raise IntentValidationError(f"source must be one of {sorted(_ALLOWED_SOURCES)}")

        created_at = payload.get("created_at") or datetime.now(timezone.utc).isoformat()
        _validate_iso8601(created_at)

        metadata = _validate_metadata(payload.get("metadata") or {})
        sanitizer = IntentSanitizer()
        sanitized = sanitizer.sanitize(payload.get("intent_text"))

        intent_id = payload.get("intent_id") or str(uuid.uuid4())
        if not isinstance(intent_id, str) or not intent_id.strip():
            raise IntentValidationError("intent_id must be a non-empty string")

        return IntentRecord(
            intent_id=intent_id.strip(),
            source=source,
            intent_text=sanitized.text,
            created_at=created_at,
            metadata=metadata,
            warnings=sanitized.warnings,
        )


class IntentIngress:
    """Earliest user-intent ingestion hook with mandatory audit logging."""

    def __init__(self, audit_store: LocalAuditStore) -> None:
        self.audit_store = audit_store
        self.validator = IntentSchemaValidator()

    def ingest(self, payload: Mapping[str, Any]) -> IntentRecord:
        try:
            record = self.validator.validate(payload)
        except IntentValidationError as exc:
            self.audit_store.append(
                AuditEvent(
                    event_type="intent.rejected",
                    actor=_safe_actor(payload),
                    status="rejected",
                    details={"reason": str(exc)},
                )
            )
            raise

        self.audit_store.append(
            AuditEvent(
                event_type="intent.accepted",
                actor=record.source,
                status="accepted",
                intent_id=record.intent_id,
                details={
                    "metadata_keys": sorted(record.metadata.keys()),
                    "warnings": record.warnings,
                    "text_length": len(record.intent_text),
                },
            )
        )
        return record


class ExecutionPolicy:
    """Allowlist gate for any future command or tool execution path."""

    def __init__(
        self,
        audit_store: LocalAuditStore,
        *,
        allowed_tools: Optional[Iterable[str]] = None,
        allowed_commands: Optional[Iterable[str]] = None,
    ) -> None:
        self.audit_store = audit_store
        self.allowed_tools = set(allowed_tools or [])
        self.allowed_commands = set(allowed_commands or [])

    def authorize(self, request: ExecutionRequest) -> bool:
        allowlist = self.allowed_tools if request.action_type == "tool" else self.allowed_commands
        approved = request.action_name in allowlist
        event_type = f"execution.{request.action_type}.{ 'approved' if approved else 'rejected'}"
        self.audit_store.append(
            AuditEvent(
                event_type=event_type,
                actor=request.actor,
                status="accepted" if approved else "rejected",
                intent_id=request.intent_id,
                details={
                    "action_name": request.action_name,
                    "action_type": request.action_type,
                    "argument_keys": sorted(request.arguments.keys()),
                    "allowlist_size": len(allowlist),
                },
            )
        )
        if not approved:
            raise IntentValidationError(
                f"{request.action_type} '{request.action_name}' is not explicitly allowlisted"
            )
        return True


def _validate_iso8601(value: Any) -> None:
    if not isinstance(value, str):
        raise IntentValidationError("created_at must be an ISO-8601 string")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IntentValidationError("created_at must be an ISO-8601 string") from exc


def _validate_metadata(value: Any) -> Dict[str, str]:
    if not isinstance(value, Mapping):
        raise IntentValidationError("metadata must be an object of string keys and values")
    if len(value) > _MAX_METADATA_ITEMS:
        raise IntentValidationError(f"metadata cannot exceed {_MAX_METADATA_ITEMS} items")

    normalized: Dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise IntentValidationError("metadata keys must be non-empty strings")
        if len(key) > _MAX_METADATA_KEY_LENGTH:
            raise IntentValidationError("metadata key exceeds maximum length")
        if not isinstance(item, str):
            raise IntentValidationError("metadata values must be strings")
        cleaned = unicodedata.normalize("NFKC", _CONTROL_CHARS.sub("", item)).strip()
        if len(cleaned) > _MAX_METADATA_VALUE_LENGTH:
            raise IntentValidationError("metadata value exceeds maximum length")
        normalized[key.strip()] = cleaned
    return normalized


def _safe_actor(payload: Mapping[str, Any]) -> str:
    source = payload.get("source") if isinstance(payload, Mapping) else None
    return source if isinstance(source, str) and source else "unknown"


__all__ = [
    "ExecutionPolicy",
    "ExecutionRequest",
    "IntentIngress",
    "IntentRecord",
    "IntentSanitizer",
    "IntentSchemaValidator",
    "IntentValidationError",
    "SanitizationResult",
]
