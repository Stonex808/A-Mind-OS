"""Shared task schema for local orchestrator intake and dispatch."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

TASK_KIND_RE = re.compile(r"^[a-z][a-z0-9_]{1,31}$")
TASK_SOURCE_RE = re.compile(r"^[a-z][a-z0-9_:\-]{1,63}$")
TASK_ID_RE = re.compile(r"^task-[a-f0-9]{12}$")


class TaskSchemaError(ValueError):
    """Raised when a task payload does not satisfy the local wire contract."""


@dataclass(slots=True)
class TaskEnvelope:
    """Normalized task envelope accepted by the local orchestrator boundary."""

    kind: str
    content: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: f"task-{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def validate(self) -> None:
        if not isinstance(self.kind, str):
            raise TaskSchemaError("kind must be a string")
        if TASK_KIND_RE.fullmatch(self.kind) is None:
            raise TaskSchemaError("kind must match ^[a-z][a-z0-9_]{1,31}$")
        if not isinstance(self.content, str) or not self.content.strip():
            raise TaskSchemaError("content must be a non-empty string")
        if len(self.content) > 1000:
            raise TaskSchemaError("content must be <= 1000 characters")
        if not isinstance(self.source, str):
            raise TaskSchemaError("source must be a string")
        if TASK_SOURCE_RE.fullmatch(self.source) is None:
            raise TaskSchemaError("source must match ^[a-z][a-z0-9_:\\-]{1,63}$")
        if not isinstance(self.metadata, dict):
            raise TaskSchemaError("metadata must be an object")
        if not isinstance(self.task_id, str) or TASK_ID_RE.fullmatch(self.task_id) is None:
            raise TaskSchemaError("task_id must match ^task-[a-f0-9]{12}$")
        if not isinstance(self.created_at, str):
            raise TaskSchemaError("created_at must be an ISO-8601 UTC string")
        try:
            timestamp = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise TaskSchemaError("created_at must be an ISO-8601 UTC string") from exc
        if timestamp.utcoffset() != timedelta(0):
            raise TaskSchemaError("created_at must be an ISO-8601 UTC string")

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "TaskEnvelope":
        if not isinstance(payload, dict):
            raise TaskSchemaError("task payload must be an object")
        for key in ("kind", "content", "source"):
            if key in payload and not isinstance(payload[key], str):
                raise TaskSchemaError(f"{key} must be a string")
        if "metadata" in payload and not isinstance(payload["metadata"], dict):
            raise TaskSchemaError("metadata must be an object")
        if "task_id" in payload and not isinstance(payload["task_id"], str):
            raise TaskSchemaError("task_id must be a string")
        if "created_at" in payload and not isinstance(payload["created_at"], str):
            raise TaskSchemaError("created_at must be a string")
        envelope = cls(
            kind=str(payload.get("kind", "")).strip(),
            content=str(payload.get("content", "")),
            source=str(payload.get("source", "")).strip(),
            metadata=payload.get("metadata", {}),
            task_id=str(payload.get("task_id", "")).strip() or f"task-{uuid.uuid4().hex[:12]}",
            created_at=str(payload.get("created_at", "")).strip() or datetime.now(UTC).isoformat(),
        )
        envelope.validate()
        return envelope

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "created_at": self.created_at,
            "kind": self.kind,
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata,
        }
