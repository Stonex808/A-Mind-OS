"""Local structured audit storage for A-Mind-OS.

Audit data is stored locally in either JSONL or SQLite using Python's stdlib.
That keeps the implementation offline by default and easy to inspect with common
system tools.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Literal, Optional

AuditBackend = Literal["jsonl", "sqlite"]


@dataclass(frozen=True)
class AuditEvent:
    """A structured audit record."""

    event_type: str
    actor: str
    status: str
    details: Dict[str, Any] = field(default_factory=dict)
    intent_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LocalAuditStore:
    """Append-only local audit store using JSONL or SQLite."""

    def __init__(
        self,
        path: str = "./data/audit/audit.jsonl",
        *,
        backend: AuditBackend = "jsonl",
    ) -> None:
        self.backend = backend
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.backend == "sqlite":
            self._initialize_sqlite()
        elif self.backend != "jsonl":
            raise ValueError("backend must be 'jsonl' or 'sqlite'")

    def append(self, event: AuditEvent) -> None:
        if self.backend == "jsonl":
            self._append_jsonl(event)
            return
        self._append_sqlite(event)

    def _append_jsonl(self, event: AuditEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), ensure_ascii=False, sort_keys=True) + "\n")

    def _initialize_sqlite(self) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    status TEXT NOT NULL,
                    intent_id TEXT,
                    details_json TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def _append_sqlite(self, event: AuditEvent) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    event_id, created_at, event_type, actor, status, intent_id, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.created_at,
                    event.event_type,
                    event.actor,
                    event.status,
                    event.intent_id,
                    json.dumps(event.details, ensure_ascii=False, sort_keys=True),
                ),
            )
            connection.commit()


__all__ = ["AuditBackend", "AuditEvent", "LocalAuditStore"]
