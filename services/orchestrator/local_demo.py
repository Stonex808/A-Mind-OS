"""Offline A-Mind orchestrator demo with verified, bounded local persistence."""

from __future__ import annotations

import argparse
import json
import re
import socketserver
import sqlite3
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_core.memory.memory_integration import CompleteAgentMemoryInterface  # noqa: E402
from python_core.refocus_core.persistence import (  # noqa: E402
    DemoPersistenceSettings,
    SensitiveContentError,
    load_demo_persistence_settings,
    sanitize_for_local_persistence,
)
from services.orchestrator.contract_registry import ContractRegistry  # noqa: E402
from services.orchestrator.orchestrator_service import (  # noqa: E402
    CodeWorker,
    ExecutionLogStore,
    LocalPlanner,
    MemoryWorker,
    ResearchWorker,
    TaskDispatcher,
    WorkerRegistry,
    classify_task_kind,
)
from services.orchestrator.task_schema import TaskEnvelope  # noqa: E402

RULES_PATH = Path(__file__).resolve().parent / "rules" / "local_rules.json"
_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class VerificationResult:
    accepted: bool
    reasons: list[str]
    normalized_intent: str
    action: str


class LocalVerifier:
    """Strictly load verifier rules and fail closed on malformed policy."""

    REQUIRED_RULES = {
        "max_intent_length": int,
        "required_keywords": list,
        "forbidden_patterns": list,
        "secret_patterns": list,
    }

    def __init__(self, rules_path: Path = RULES_PATH) -> None:
        try:
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot load verifier rules from {rules_path}: {exc}") from exc
        if not isinstance(rules, dict):
            raise ValueError("verifier rules must be a JSON object")
        missing = sorted(set(self.REQUIRED_RULES) - set(rules))
        if missing:
            raise ValueError(f"verifier rules missing required keys: {', '.join(missing)}")
        unknown = sorted(set(rules) - set(self.REQUIRED_RULES))
        if unknown:
            raise ValueError(f"verifier rules contain unknown keys: {', '.join(unknown)}")
        for key, expected_type in self.REQUIRED_RULES.items():
            if not isinstance(rules[key], expected_type) or isinstance(rules[key], bool):
                raise ValueError(f"verifier rule '{key}' must be {expected_type.__name__}")
        if rules["max_intent_length"] <= 0:
            raise ValueError("max_intent_length must be positive")
        for key in ("required_keywords", "forbidden_patterns", "secret_patterns"):
            if not rules[key] or not all(isinstance(item, str) and item for item in rules[key]):
                raise ValueError(f"verifier rule '{key}' must be a non-empty string array")
        self.rules = rules

    def verify(self, raw_intent: str) -> VerificationResult:
        if not isinstance(raw_intent, str):
            raise TypeError("raw_intent must be a string")
        cleaned = _WHITESPACE_RE.sub(" ", raw_intent.strip())
        lowered = cleaned.lower()
        reasons: list[str] = []
        if not cleaned:
            reasons.append("intent is empty")
        if len(cleaned) > self.rules["max_intent_length"]:
            reasons.append(f"intent exceeds {self.rules['max_intent_length']} characters")
        for pattern in self.rules["forbidden_patterns"]:
            if pattern.lower() in lowered:
                reasons.append(f"forbidden pattern detected: {pattern}")
        for pattern in self.rules["secret_patterns"]:
            if pattern.lower() in lowered:
                reasons.append(f"potential secret detected: {pattern}")
        if not any(keyword.lower() in lowered for keyword in self.rules["required_keywords"]):
            reasons.append("intent must include one of: " + ", ".join(self.rules["required_keywords"]))
        return VerificationResult(not reasons, reasons, cleaned, "recall" if "recall" in lowered else "remember")


class LocalArtifactStore:
    """Persist sanitized run records and enforce configured retention."""

    def __init__(self, settings: DemoPersistenceSettings) -> None:
        self.settings = settings
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        settings.runs_dir.mkdir(parents=True, exist_ok=True)
        settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(settings.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orchestrator_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    source TEXT NOT NULL,
                    raw_intent TEXT NOT NULL,
                    normalized_intent TEXT NOT NULL,
                    action TEXT NOT NULL,
                    accepted INTEGER NOT NULL,
                    reasons_json TEXT NOT NULL,
                    artifact_path TEXT NOT NULL
                )
                """
            )
        self.enforce_retention()

    def persist_run(
        self,
        *,
        source: str,
        raw_intent: str,
        verification: VerificationResult,
        outcome: dict[str, Any],
    ) -> dict[str, Any]:
        created_at = time.time()
        artifact_path = self.settings.runs_dir / f"run-{time.time_ns()}.json"
        payload = sanitize_for_local_persistence(
            {
                "created_at": created_at,
                "source": source,
                "raw_intent": raw_intent,
                "normalized_intent": verification.normalized_intent,
                "action": verification.action,
                "accepted": verification.accepted,
                "reasons": verification.reasons,
                **outcome,
                "persisted": True,
                "artifact_path": f"runs/{artifact_path.name}",
            },
            self.settings.sensitive_content_mode,
        )
        artifact_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        with sqlite3.connect(self.settings.db_path) as connection:
            connection.execute(
                """
                INSERT INTO orchestrator_runs (
                    created_at, source, raw_intent, normalized_intent, action,
                    accepted, reasons_json, artifact_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    payload["source"],
                    payload["raw_intent"],
                    payload["normalized_intent"],
                    payload["action"],
                    int(payload["accepted"]),
                    json.dumps(payload["reasons"], ensure_ascii=False),
                    payload["artifact_path"],
                ),
            )
        self.enforce_retention()
        return payload

    def enforce_retention(self) -> None:
        now = time.time()
        if self.settings.retention_days:
            cutoff = now - self.settings.retention_days * 86400
            for path in self.settings.runs_dir.glob("run-*.json"):
                if path.stat().st_mtime < cutoff:
                    path.unlink()
            with sqlite3.connect(self.settings.db_path) as connection:
                connection.execute("DELETE FROM orchestrator_runs WHERE created_at < ?", (cutoff,))
        if self.settings.max_run_artifacts:
            paths = sorted(
                self.settings.runs_dir.glob("run-*.json"),
                key=lambda path: path.stat().st_mtime_ns,
                reverse=True,
            )
            for path in paths[self.settings.max_run_artifacts :]:
                path.unlink()
            with sqlite3.connect(self.settings.db_path) as connection:
                connection.execute(
                    """
                    DELETE FROM orchestrator_runs
                    WHERE id NOT IN (
                        SELECT id FROM orchestrator_runs ORDER BY created_at DESC, id DESC LIMIT ?
                    )
                    """,
                    (self.settings.max_run_artifacts,),
                )


class LocalOrchestratorDemo:
    def __init__(
        self,
        data_dir: str | Path | None = None,
        memory_dir: str | Path | None = None,
        rules_path: Path = RULES_PATH,
    ) -> None:
        self.settings = load_demo_persistence_settings(data_dir=data_dir, memory_dir=memory_dir)
        self.verifier = LocalVerifier(rules_path)
        self.artifacts = LocalArtifactStore(self.settings)
        self.memory = CompleteAgentMemoryInterface(
            "local_demo_orchestrator",
            prefer_local_fallback=True,
            memory_root=self.settings.memory_dir,
            sensitive_content_mode=self.settings.sensitive_content_mode,
        )
        self.registerable_agents = ContractRegistry().contracts_for_registration()
        workers = [MemoryWorker(self.memory), ResearchWorker(self.memory), CodeWorker(self.memory)]
        self.dispatcher = TaskDispatcher(
            LocalPlanner(),
            WorkerRegistry(workers),
            ExecutionLogStore(
                self.settings.db_path,
                self.settings.data_dir / "execution_events.jsonl",
                self.settings.sensitive_content_mode,
            ),
        )
        self._seed_local_context()

    def _seed_local_context(self) -> None:
        self.memory.learn_fact("orchestrator", "stores", "intent history in local SQLite and JSON")
        self.memory.learn_fact(
            "orchestrator",
            "registers_agents_from",
            ", ".join(sorted(self.registerable_agents)),
        )
        self.memory.define_concept(
            "local demo",
            "A deterministic offline workflow that verifies an intent and persists bounded local artifacts.",
            "workflow",
        )

    def process_intent(self, raw_intent: str, source: str) -> dict[str, Any]:
        verification = self.verifier.verify(raw_intent)
        try:
            clean_raw = sanitize_for_local_persistence(raw_intent, self.settings.sensitive_content_mode)
            clean_source = sanitize_for_local_persistence(source, self.settings.sensitive_content_mode)
            clean_intent = sanitize_for_local_persistence(
                verification.normalized_intent,
                self.settings.sensitive_content_mode,
            )
        except SensitiveContentError as exc:
            return {
                "accepted": False,
                "persisted": False,
                "reasons": [str(exc)],
                "result": {"status": "refused", "message": "Sensitive content was not persisted."},
            }

        verification = replace(verification, normalized_intent=clean_intent)
        if verification.accepted:
            task = TaskEnvelope(
                kind=classify_task_kind(clean_intent, verification.action),
                content=clean_intent,
                source=_normalize_source(clean_source),
                metadata={"input_source": clean_source[:200]},
            )
            outcome = self.dispatcher.dispatch(task)
        else:
            outcome = {
                "result": {
                    "status": "rejected",
                    "message": "Intent rejected by the local verifier.",
                }
            }
        return self.artifacts.persist_run(
            source=clean_source,
            raw_intent=clean_raw,
            verification=verification,
            outcome=outcome,
        )


def _normalize_source(source: str) -> str:
    normalized = re.sub(r"[^a-z0-9_:\-]", "_", source.lower()).strip("_:")
    if len(normalized) < 2:
        normalized = "ui"
    if not normalized[0].isalpha():
        normalized = "source_" + normalized
    return normalized[:64]


class IntentSocketHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw_intent = self.rfile.readline().decode("utf-8", errors="replace")
        result = self.server.orchestrator.process_intent(raw_intent, source="socket")  # type: ignore[attr-defined]
        self.wfile.write((json.dumps(result, indent=2) + "\n").encode("utf-8"))


class UnixSocketServer(socketserver.UnixStreamServer):
    allow_reuse_address = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the offline A-Mind orchestrator demo.")
    parser.add_argument("--intent-file", type=Path, help="Read an intent from a local text file.")
    parser.add_argument("--stdin", action="store_true", help="Read an intent from standard input.")
    parser.add_argument("--socket", action="store_true", help="Serve a local Unix socket.")
    parser.add_argument("--socket-path", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    orchestrator = LocalOrchestratorDemo()
    if args.socket:
        socket_path = args.socket_path or orchestrator.settings.data_dir / "orchestrator.sock"
        socket_path.parent.mkdir(parents=True, exist_ok=True)
        if socket_path.exists():
            socket_path.unlink()
        try:
            with UnixSocketServer(str(socket_path), IntentSocketHandler) as server:
                server.orchestrator = orchestrator  # type: ignore[attr-defined]
                print(f"Local orchestrator socket listening at {socket_path}")
                server.serve_forever()
        finally:
            if socket_path.exists():
                socket_path.unlink()
        return 0
    if args.intent_file:
        raw_intent = args.intent_file.read_text(encoding="utf-8")
        source = "file"
    elif args.stdin:
        raw_intent = sys.stdin.read()
        source = "stdin"
    else:
        raise SystemExit("Choose one of --intent-file, --stdin, or --socket.")
    print(json.dumps(orchestrator.process_intent(raw_intent, source), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
