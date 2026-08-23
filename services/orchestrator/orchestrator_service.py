"""Canonical planner/worker boundary for the local A-Mind orchestrator."""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from python_core.refocus_core.persistence import sanitize_for_local_persistence

from .task_schema import TaskEnvelope


class Worker(Protocol):
    name: str

    def can_handle(self, task: TaskEnvelope) -> bool: ...

    def execute(self, task: TaskEnvelope) -> dict[str, Any]: ...


@dataclass(frozen=True)
class PlannerDecision:
    worker_name: str
    rationale: str
    budget: dict[str, int]


class LocalPlanner:
    """Make explicit, deterministic routing decisions."""

    def choose_worker(self, task: TaskEnvelope, workers: list[Worker]) -> PlannerDecision:
        preferred = {
            "memory": "memory_worker",
            "recall": "memory_worker",
            "research": "research_worker",
            "code": "code_worker",
        }.get(task.kind)
        for worker in workers:
            if worker.name == preferred and worker.can_handle(task):
                return PlannerDecision(
                    worker.name,
                    f"task kind '{task.kind}' maps to {worker.name}",
                    {"max_context_items": 5, "time_budget_ms": 1000},
                )
        raise ValueError(f"no registered worker can handle task kind '{task.kind}'")


class WorkerRegistry:
    def __init__(self, workers: list[Worker] | None = None) -> None:
        self._workers: dict[str, Worker] = {}
        for worker in workers or []:
            self.register(worker)

    def register(self, worker: Worker) -> None:
        if worker.name in self._workers:
            raise ValueError(f"worker already registered: {worker.name}")
        self._workers[worker.name] = worker

    @property
    def workers(self) -> list[Worker]:
        return list(self._workers.values())

    def get(self, name: str) -> Worker:
        try:
            return self._workers[name]
        except KeyError as exc:
            raise KeyError(f"unknown worker: {name}") from exc


class ExecutionLogStore:
    """Append task events to JSONL and the demo's single SQLite database."""

    def __init__(
        self,
        db_path: Path,
        events_path: Path,
        sensitive_content_mode: str = "redact",
    ) -> None:
        self.db_path = db_path
        self.events_path = events_path
        self.sensitive_content_mode = sensitive_content_mode
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orchestrator_task_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    task_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    worker_name TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    details_json TEXT NOT NULL
                )
                """
            )

    def log_event(
        self,
        *,
        task: TaskEnvelope,
        status: str,
        worker_name: str,
        summary: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        event = sanitize_for_local_persistence(
            {
                "created_at": time.time(),
                "task_id": task.task_id,
                "source": task.source,
                "kind": task.kind,
                "status": status,
                "worker_name": worker_name,
                "summary": summary,
                "details": details,
            },
            self.sensitive_content_mode,
        )
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO orchestrator_task_events (
                    created_at, task_id, source, kind, status, worker_name, summary, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["created_at"],
                    event["task_id"],
                    event["source"],
                    event["kind"],
                    event["status"],
                    event["worker_name"],
                    event["summary"],
                    json.dumps(event["details"], ensure_ascii=False),
                ),
            )
        return event


class TaskDispatcher:
    def __init__(self, planner: LocalPlanner, registry: WorkerRegistry, logs: ExecutionLogStore) -> None:
        self.planner = planner
        self.registry = registry
        self.logs = logs

    def dispatch(self, task: TaskEnvelope) -> dict[str, Any]:
        task.validate()
        decision = self.planner.choose_worker(task, self.registry.workers)
        worker = self.registry.get(decision.worker_name)
        result = worker.execute(task)
        status = str(result.get("status", "completed"))
        summary = str(result.get("message", "Task completed."))
        event = self.logs.log_event(
            task=task,
            status=status,
            worker_name=worker.name,
            summary=summary,
            details={"planner_rationale": decision.rationale, "result": result},
        )
        return {
            "task": task.as_dict(),
            "routing": {
                "worker": worker.name,
                "rationale": decision.rationale,
                "budget": decision.budget,
            },
            "result": result,
            "event": event,
        }


class MemoryWorker:
    name = "memory_worker"

    def __init__(self, memory_interface: Any) -> None:
        self.memory = memory_interface

    def can_handle(self, task: TaskEnvelope) -> bool:
        return task.kind in {"memory", "recall"}

    def execute(self, task: TaskEnvelope) -> dict[str, Any]:
        if task.kind == "recall":
            return {
                "status": "recalled",
                "message": "Returned matching local context.",
                "memory_recall": _bounded_recall(self.memory.recall_for_situation(task.content), 5),
            }
        topic = _extract_topic(task.content)
        self.memory.learn_fact(topic, "noted_as", task.content)
        episode_id = self.memory.remember_task(
            task=task.content,
            actions=["validated task envelope", "stored semantic fact", "recorded episodic memory"],
            outcome="Stored locally for deterministic recall",
            observations=["offline-only", "local-first"],
            tags=["orchestrator", "memory"],
        )
        return {
            "status": "stored",
            "message": "Intent stored in local memory.",
            "episode_id": episode_id,
            "topic": topic,
            "memory_recall": _bounded_recall(self.memory.recall_for_situation(task.content), 5),
        }


class ResearchWorker:
    name = "research_worker"

    def __init__(self, memory_interface: Any) -> None:
        self.memory = memory_interface

    def can_handle(self, task: TaskEnvelope) -> bool:
        return task.kind == "research"

    def execute(self, task: TaskEnvelope) -> dict[str, Any]:
        recall = _bounded_recall(self.memory.recall_for_situation(task.content), 5)
        return {
            "status": "completed",
            "message": "Completed a bounded local research pass; no network calls were made.",
            "memory_recall": recall,
        }


class CodeWorker:
    name = "code_worker"

    def __init__(self, memory_interface: Any) -> None:
        self.memory = memory_interface

    def can_handle(self, task: TaskEnvelope) -> bool:
        return task.kind == "code"

    def execute(self, task: TaskEnvelope) -> dict[str, Any]:
        return {
            "status": "completed",
            "message": "Recorded a bounded local code-task recommendation.",
            "recommendations": [
                "Use contract-driven interfaces.",
                "Keep worker context deterministic and bounded.",
            ],
            "memory_recall": _bounded_recall(self.memory.recall_for_situation(task.content), 5),
        }


def classify_task_kind(intent: str, action: str) -> str:
    if action == "recall":
        return "recall"
    lowered = intent.lower()
    if any(word in lowered for word in ("research", "compare", "investigate", "search")):
        return "research"
    if any(word in lowered for word in ("code", "refactor", "python", "function", "bug")):
        return "code"
    return "memory"


def _extract_topic(intent: str) -> str:
    lowered = intent.lower()
    for prefix in ("remember ", "store ", "note "):
        if lowered.startswith(prefix):
            return intent[len(prefix) :].strip() or "intent"
    return "intent"


def _bounded_recall(recall: dict[str, Any], limit: int) -> dict[str, Any]:
    bounded = {"situation": recall.get("situation", "")}
    for key in ("past_experiences", "relevant_facts", "relevant_concepts", "applicable_procedures"):
        value = recall.get(key, [])
        bounded[key] = value[:limit] if isinstance(value, list) else []
    return bounded


__all__ = [
    "CodeWorker",
    "ExecutionLogStore",
    "LocalPlanner",
    "MemoryWorker",
    "ResearchWorker",
    "TaskDispatcher",
    "WorkerRegistry",
    "classify_task_kind",
]
