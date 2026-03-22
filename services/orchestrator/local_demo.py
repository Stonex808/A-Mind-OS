"""Local-first orchestrator demo with deterministic verification and local persistence."""

from __future__ import annotations

import argparse
import json
import re
import socketserver
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from contract_registry import ContractRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_CORE = REPO_ROOT / "python_core"
if str(PYTHON_CORE) not in sys.path:
    sys.path.insert(0, str(PYTHON_CORE))

from memory.memory_integration import CompleteAgentMemoryInterface  # noqa: E402

DATA_DIR = REPO_ROOT / "data" / "demo"
RULES_PATH = Path(__file__).resolve().parent / "rules" / "local_rules.json"
DEFAULT_SOCKET_PATH = DATA_DIR / "orchestrator.sock"
INTENT_RE = re.compile(r"\s+")


@dataclass
class VerificationResult:
    accepted: bool
    reasons: list[str]
    normalized_intent: str
    action: str


class LocalVerifier:
    def __init__(self, rules_path: Path) -> None:
        with open(rules_path, "r", encoding="utf-8") as handle:
            self.rules = json.load(handle)

    def verify(self, raw_intent: str) -> VerificationResult:
        cleaned = INTENT_RE.sub(" ", raw_intent.strip())
        reasons: list[str] = []
        lowered = cleaned.lower()

        if not cleaned:
            reasons.append("intent is empty")
        if len(cleaned) > int(self.rules["max_intent_length"]):
            reasons.append(f"intent exceeds {self.rules['max_intent_length']} characters")
        for pattern in self.rules["forbidden_patterns"]:
            if pattern.lower() in lowered:
                reasons.append(f"forbidden pattern detected: {pattern}")
        for pattern in self.rules["secret_patterns"]:
            if pattern.lower() in lowered:
                reasons.append(f"potential secret detected: {pattern}")
        if not any(keyword in lowered for keyword in self.rules["required_keywords"]):
            reasons.append(
                "intent must include one of: " + ", ".join(self.rules["required_keywords"])
            )

        action = "recall" if "recall" in lowered else "remember"
        return VerificationResult(
            accepted=not reasons,
            reasons=reasons,
            normalized_intent=cleaned,
            action=action,
        )


class LocalArtifactStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.runs_dir = data_dir / "runs"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = data_dir / "orchestrator.db"
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
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
            conn.commit()

    def persist_run(self, *, source: str, raw_intent: str, verification: VerificationResult, result: Dict[str, Any]) -> Dict[str, Any]:
        created_at = time.time()
        artifact_path = self.runs_dir / f"run-{int(created_at * 1000)}.json"
        payload = {
            "created_at": created_at,
            "source": source,
            "raw_intent": raw_intent,
            "normalized_intent": verification.normalized_intent,
            "action": verification.action,
            "accepted": verification.accepted,
            "reasons": verification.reasons,
            "result": result,
        }
        with open(artifact_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO orchestrator_runs (
                    created_at, source, raw_intent, normalized_intent, action, accepted, reasons_json, artifact_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    source,
                    raw_intent,
                    verification.normalized_intent,
                    verification.action,
                    1 if verification.accepted else 0,
                    json.dumps(verification.reasons),
                    str(artifact_path.relative_to(REPO_ROOT)),
                ),
            )
            conn.commit()
        payload["artifact_path"] = str(artifact_path.relative_to(REPO_ROOT))
        return payload


class LocalOrchestratorDemo:
    def __init__(self, data_dir: Path = DATA_DIR, rules_path: Path = RULES_PATH) -> None:
        self.memory = CompleteAgentMemoryInterface("local_demo_orchestrator", prefer_local_fallback=True)
        self.verifier = LocalVerifier(rules_path)
        self.artifacts = LocalArtifactStore(data_dir)
        self.contract_registry = ContractRegistry()
        self.registerable_agents = self.contract_registry.contracts_for_registration()
        self._seed_local_context()

    def _seed_local_context(self) -> None:
        self.memory.learn_fact("orchestrator", "stores", "intent history in local sqlite")
        self.memory.learn_fact("orchestrator", "registers_agents_from", ", ".join(sorted(self.registerable_agents)))
        self.memory.learn_fact("memory", "persists", "context in repo-local json")
        self.memory.define_concept(
            "local demo",
            "A deterministic offline workflow that reads an intent, verifies it, and persists local artifacts.",
            "workflow",
            examples=["remember to back up the data directory", "recall the last saved preference"],
        )

    def process_intent(self, raw_intent: str, source: str) -> Dict[str, Any]:
        verification = self.verifier.verify(raw_intent)
        recall = self.memory.recall_for_situation(verification.normalized_intent or raw_intent)
        if verification.accepted:
            outcome = self._apply_memory_action(verification, recall)
        else:
            outcome = {
                "status": "rejected",
                "message": "Intent rejected by local verifier.",
                "memory_recall": recall,
            }
        return self.artifacts.persist_run(
            source=source,
            raw_intent=raw_intent,
            verification=verification,
            result=outcome,
        )

    def _apply_memory_action(self, verification: VerificationResult, recall: Dict[str, Any]) -> Dict[str, Any]:
        if verification.action == "recall":
            return {
                "status": "recalled",
                "message": "Returned matching local context.",
                "memory_recall": recall,
            }

        normalized = verification.normalized_intent
        topic = self._extract_topic(normalized)
        self.memory.learn_fact(topic, "noted_as", normalized)
        episode_id = self.memory.remember_task(
            task=normalized,
            actions=["verified intent locally", "stored fact in semantic memory", "persisted run artifacts"],
            outcome="Stored locally for future deterministic recall",
            success=True,
            observations=["offline-only", "repo-local persistence"],
            tags=["local-demo", "intent"],
        )
        return {
            "status": "stored",
            "message": "Intent stored in local memory.",
            "episode_id": episode_id,
            "topic": topic,
            "memory_recall": recall,
        }

    @staticmethod
    def _extract_topic(intent: str) -> str:
        lowered = intent.lower()
        for prefix in ("remember ", "store ", "note "):
            if lowered.startswith(prefix):
                return intent[len(prefix):].strip() or "intent"
        return "intent"


class IntentSocketHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw_intent = self.rfile.readline().decode("utf-8", errors="replace")
        orchestrator = getattr(self.server, "orchestrator")
        socket_path = getattr(self.server, "socket_path", "local")
        result = orchestrator.process_intent(raw_intent, source=f"socket:{socket_path}")
        self.wfile.write((json.dumps(result, indent=2) + "\n").encode("utf-8"))


class UnixSocketServer(socketserver.UnixStreamServer):
    allow_reuse_address = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local Refocus-OS orchestrator demo.")
    parser.add_argument("--intent-file", type=Path, help="Read a plain-text intent from a local file.")
    parser.add_argument("--stdin", action="store_true", help="Read a plain-text intent from stdin.")
    parser.add_argument("--socket", action="store_true", help="Serve a simple local Unix socket.")
    parser.add_argument("--socket-path", type=Path, default=DEFAULT_SOCKET_PATH, help="Path for --socket mode.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    orchestrator = LocalOrchestratorDemo()

    if args.socket:
        args.socket_path.parent.mkdir(parents=True, exist_ok=True)
        if args.socket_path.exists():
            args.socket_path.unlink()
        with UnixSocketServer(str(args.socket_path), IntentSocketHandler) as server:
            server.orchestrator = orchestrator
            server.socket_path = args.socket_path
            print(f"Local orchestrator socket listening at {args.socket_path}")
            server.serve_forever()
        return 0

    if args.intent_file:
        raw_intent = args.intent_file.read_text(encoding="utf-8")
        source = f"file:{args.intent_file}"
    elif args.stdin:
        raw_intent = sys.stdin.read()
        source = "stdin"
    else:
        raise SystemExit("Choose one of --intent-file, --stdin, or --socket.")

    result = orchestrator.process_intent(raw_intent, source=source)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
