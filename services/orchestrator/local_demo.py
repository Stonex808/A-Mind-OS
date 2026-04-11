"""Local-first orchestrator demo with deterministic verification, dispatch, and persistence."""

from __future__ import annotations

import argparse
import json
import os
import re
import socketserver
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from contract_registry import ContractRegistry
from orchestrator_service import (
    CodeWorker,
    ExecutionLogStore,
    LocalPlanner,
    MemoryWorker,
    ResearchWorker,
    TaskDispatcher,
    WorkerRegistry,
)
from task_schema import TaskEnvelope

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_CORE = REPO_ROOT / "python_core"
if str(PYTHON_CORE) not in sys.path:
    sys.path.insert(0, str(PYTHON_CORE))

from memory.memory_integration import CompleteAgentMemoryInterface  # noqa: E402

DATA_DIR = Path(os.environ.get("REFOCUS_DEMO_DATA_DIR", REPO_ROOT / "data" / "demo"))
MEMORY_DIR = Path(os.environ.get("REFOCUS_DEMO_MEMORY_ROOT", REPO_ROOT / "data" / "memory"))
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



class RunArtifactStore:
    def __init__(self, data_dir: Path) -> None:
        self.runs_dir = data_dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def persist(self, payload: dict[str, object]) -> str:
        created_at = time.time()
        path = self.runs_dir / f"run-{int(created_at * 1000)}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            return str(path)


class LocalOrchestratorDemo:
    def __init__(self, data_dir: Path = DATA_DIR, rules_path: Path = RULES_PATH) -> None:
        self.memory = CompleteAgentMemoryInterface(
            "local_demo_orchestrator",
            prefer_local_fallback=True,
            memory_root=MEMORY_DIR,
        )
        self.verifier = LocalVerifier(rules_path)
        self.contract_registry = ContractRegistry()
        self.registerable_agents = self.contract_registry.contracts_for_registration()
        self.artifacts = RunArtifactStore(data_dir)
        self.dispatcher = TaskDispatcher(
            planner=LocalPlanner(),
            registry=WorkerRegistry(
                [MemoryWorker(self.memory), ResearchWorker(), CodeWorker()]
            ),
            logs=ExecutionLogStore(data_dir),
        )
        self._seed_local_context()

    def _seed_local_context(self) -> None:
        self.memory.learn_fact("orchestrator", "stores", "intent history in local sqlite")
        self.memory.learn_fact(
            "orchestrator",
            "registers_agents_from",
            ", ".join(sorted(self.registerable_agents)),
        )
        self.memory.learn_fact("memory", "persists", "context in repo-local json")

    def process_intent(self, raw_intent: str, source: str) -> dict[str, object]:
        verification = self.verifier.verify(raw_intent)
        if not verification.accepted:
            payload = {
                "source": source,
                "raw_intent": raw_intent,
                "normalized_intent": verification.normalized_intent,
                "action": verification.action,
                "accepted": False,
                "reasons": verification.reasons,
                "result": {
                    "status": "rejected",
                    "message": "Intent rejected by local verifier.",
                },
            }
            payload["artifact_path"] = self.artifacts.persist(payload)
            return payload

        task = TaskEnvelope(
            kind="recall" if verification.action == "recall" else "memory",
            content=verification.normalized_intent,
            source=source.replace("/", ":").replace(" ", "_")[:64] or "stdin",
            metadata={"action": verification.action},
        )
        routed = self.dispatcher.dispatch(task)
        payload = {
            "source": source,
            "raw_intent": raw_intent,
            "normalized_intent": verification.normalized_intent,
            "action": verification.action,
            "accepted": True,
            "reasons": [],
            "result": routed["result"],
            "routing": routed["routing"],
            "event": routed["event"],
            "task": routed["task"],
        }
        payload["artifact_path"] = self.artifacts.persist(payload)
        return payload


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
